import asyncio
import logging
from dataclasses import replace
from .failure_reasons import FailureReason

from pydantic import ValidationError

from src.modules.ai_processing.application.contracts import (
    ITextInterpreter, IThemeCatalog, Interpretation, InterpretationRequest,
    InterpretationFailedError, InvalidInterpretationError, ProviderNotConfiguredError,
    InvalidJournalInputError,
)
from src.modules.ai_processing.application.contextual_passage_selection import (
    ContextualPassageAssociation,
    ContextualPassageSelection,
    ContextualPassageSelectionRequest,
    IContextualPassageSelector,
    PassageSelectionSentence,
    PassageSelectionTheme,
)
from src.modules.catalog.public.contextual_passage import (
    ContextualPassageCandidate,
    IContextualPassageCatalog,
)
from src.modules.journal.public.analysis import (
    IJournalAnalysisGateway,
    SentenceAnalysis,
    SentencePassageAnalysis,
)
from src.shared.domain.ports.system.iclock import IClock
from src.shared.domain.ports.system.iulid_generator import IULIDGenerator


logger = logging.getLogger(__name__)


class InterpretEntry:
    def __init__(
        self, journal: IJournalAnalysisGateway, catalog: IThemeCatalog,
        interpreter: ITextInterpreter, clock: IClock, ids: IULIDGenerator,
        *, passage_catalog: IContextualPassageCatalog,
        passage_selector: IContextualPassageSelector,
        timeout_seconds: float = 30,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("Timeout must be positive.")
        self.journal, self.catalog, self.interpreter = journal, catalog, interpreter
        self.passage_catalog = passage_catalog
        self.passage_selector = passage_selector
        self.clock, self.ids, self.timeout_seconds = clock, ids, timeout_seconds

    async def execute(self, entry_id: str, user_id: str) -> str:
        # A trusted caller supplies the owner; never take it from the AI response.
        snapshot = await self.journal.read(entry_id, user_id)
        self.interpreter.ensure_available()
        themes = await self.catalog.active_themes()
        try:
            request = InterpretationRequest(
                content_text=snapshot.content_text, context_tags=snapshot.context_tags,
                themes=themes,
            )
        except ValidationError:
            raise InvalidJournalInputError("Invalid journal input.") from None
        try:
            async with asyncio.timeout(self.timeout_seconds):
                raw = await self.interpreter.interpret(request)
        except (ProviderNotConfiguredError, InterpretationFailedError):
            raise
        except TimeoutError:
            raise InterpretationFailedError(reason=FailureReason.TIMEOUT) from None
        except Exception:
            raise InterpretationFailedError("Text interpretation failed.") from None
        try:
            result = Interpretation.model_validate(raw)
        except ValidationError:
            raise InvalidInterpretationError("Invalid interpretation response.") from None

        allowed = {theme.id: theme for theme in themes}
        # The provider owns the semantic relevance score. The application only
        # normalizes its presentation so downstream selection is deterministic.
        ordered_matches = sorted(
            result.themes,
            key=lambda match: (-match.confidence, match.theme_id),
        )
        selected = [theme.theme_id for theme in ordered_matches]
        if len(selected) != len(set(selected)) or not set(selected) <= allowed.keys():
            raise InvalidInterpretationError("Invalid theme selection.", reason=FailureReason.THEMES)
        # Derive offsets from literal source text, never trust AI character counts.
        sentences = []
        cursor = 0
        for index, sentence in enumerate(result.sentences):
            start = snapshot.content_text.find(sentence.sentence_text, cursor)
            if start < 0 or snapshot.content_text[cursor:start].strip():
                raise InvalidInterpretationError("Invalid sentence segmentation.", reason=FailureReason.SENTENCES)
            end = start + len(sentence.sentence_text)
            ordered_sentence_matches = sorted(
                sentence.themes,
                key=lambda match: (-match.confidence, match.theme_id),
            )
            matches = [match.theme_id for match in ordered_sentence_matches]
            if len(matches) != len(set(matches)) or not set(matches) <= set(selected):
                raise InvalidInterpretationError("Invalid sentence theme selection.", reason=FailureReason.THEMES)
            sentences.append(SentenceAnalysis(
                id=self.ids.generate_ulid(), sentence_index=index,
                sentence_text=sentence.sentence_text, start_offset=start, end_offset=end,
                themes=tuple(
                    {**allowed[match.theme_id].model_dump(), "confidence": match.confidence,
                     "source": "ai", "confirmed_by_user": False}
                    for match in ordered_sentence_matches
                ),
            ))
            cursor = end
        if snapshot.content_text[cursor:].strip():
            raise InvalidInterpretationError("Incomplete sentence segmentation.", reason=FailureReason.SENTENCES)
        # Recheck eligibility after the external call. Neo4j/PostgreSQL are not
        # a distributed transaction; retain the catalog snapshot for traceability.
        current = {theme.id: theme for theme in await self.catalog.active_themes()}
        if any(current.get(theme_id) != allowed[theme_id] for theme_id in selected):
            raise InvalidInterpretationError("Selected catalog themes changed.", reason=FailureReason.CATALOG_CHANGED)

        used_theme_ids = {
            theme["id"]
            for sentence in sentences
            for theme in sentence.themes
        }
        contextual_theme_ids = tuple(
            match.theme_id
            for match in ordered_matches
            if match.theme_id in used_theme_ids
        )
        contextual_candidates = ()
        if contextual_theme_ids:
            try:
                contextual_candidates = await self.passage_catalog.find_active_by_themes(
                    contextual_theme_ids,
                )
                logger.info(
                    "Contextual passage candidates loaded: themes=%d candidates=%d",
                    len(contextual_theme_ids),
                    len(contextual_candidates),
                )
            except Exception:
                raise InterpretationFailedError(
                    reason=FailureReason.CATALOG,
                ) from None

        selected_passages = ()
        if contextual_candidates:
            selection_request = ContextualPassageSelectionRequest(
                sentences=tuple(
                    PassageSelectionSentence(
                        sentence_id=sentence.id,
                        sentence_text=sentence.sentence_text,
                        themes=tuple(
                            PassageSelectionTheme(
                                theme_id=theme["id"],
                                label=theme["label"],
                                description=theme["description"],
                                confidence=theme["confidence"],
                            )
                            for theme in sentence.themes
                        ),
                    )
                    for sentence in sentences
                    if sentence.themes
                ),
                candidates=contextual_candidates,
            )
            self.passage_selector.ensure_available()
            try:
                async with asyncio.timeout(self.timeout_seconds):
                    raw_selection = (
                        await self.passage_selector.select_contextual_passages(
                            selection_request,
                        )
                    )
            except (ProviderNotConfiguredError, InterpretationFailedError):
                raise
            except TimeoutError:
                raise InterpretationFailedError(
                    reason=FailureReason.TIMEOUT,
                ) from None
            except Exception:
                raise InterpretationFailedError(
                    "Contextual passage selection failed.",
                ) from None
            try:
                passage_selection = ContextualPassageSelection.model_validate(
                    raw_selection,
                )
            except ValidationError:
                raise InvalidInterpretationError(
                    "Invalid contextual passage selection.",
                    reason=FailureReason.PASSAGES,
                ) from None
            selected_passages = self._validated_passage_associations(
                passage_selection,
                selection_request,
            )
            logger.info(
                "Contextual passages selected: associations=%d",
                len(selected_passages),
            )
            sentences = list(self._attach_passages(
                sentences=tuple(sentences),
                associations=selected_passages,
                candidates=contextual_candidates,
            ))

        metadata = {
            "schema_version": 2,
            "sentiments": list(dict.fromkeys(emotion.casefold() for emotion in result.sentiments)),
            "tone": result.tone,
            "themes": [
                {**allowed[match.theme_id].model_dump(), "confidence": match.confidence,
                 "source": "ai", "confirmed_by_user": False}
                for match in ordered_matches
                if match.theme_id in used_theme_ids
            ],
        }
        analysis_id = self.ids.generate_ulid()
        await self.journal.save(
            snapshot, analysis_id=analysis_id, summary=result.summary,
            main_message=result.main_message, metadata=metadata, now=self.clock.now(),
            sentences=tuple(sentences),
        )
        return analysis_id

    @staticmethod
    def _validated_passage_associations(
        selection: ContextualPassageSelection,
        request: ContextualPassageSelectionRequest,
    ) -> tuple[ContextualPassageAssociation, ...]:
        sentence_themes = {
            sentence.sentence_id: {
                theme.theme_id for theme in sentence.themes
            }
            for sentence in request.sentences
        }
        candidate_themes: dict[str, set[str]] = {}
        for candidate in request.candidates:
            candidate_themes.setdefault(candidate.passage_id, set()).add(
                candidate.matched_theme_id,
            )

        sentence_ids = [item.sentence_id for item in selection.associations]
        passage_ids = [item.passage_id for item in selection.associations]
        invalid = (
            len(sentence_ids) != len(set(sentence_ids))
            or len(passage_ids) != len(set(passage_ids))
            or any(
                item.sentence_id not in sentence_themes
                or item.passage_id not in candidate_themes
                or not (
                    sentence_themes[item.sentence_id]
                    & candidate_themes[item.passage_id]
                )
                for item in selection.associations
            )
        )
        if invalid:
            raise InvalidInterpretationError(
                "Invalid contextual passage selection.",
                reason=FailureReason.PASSAGES,
            )
        return tuple(
            sorted(
                selection.associations,
                key=lambda item: (
                    -item.confidence,
                    item.sentence_id,
                    item.passage_id,
                ),
            )
        )

    def _attach_passages(
        self,
        *,
        sentences: tuple[SentenceAnalysis, ...],
        associations: tuple[ContextualPassageAssociation, ...],
        candidates: tuple[ContextualPassageCandidate, ...],
    ) -> tuple[SentenceAnalysis, ...]:
        candidates_by_passage: dict[str, list[ContextualPassageCandidate]] = {}
        for candidate in candidates:
            candidates_by_passage.setdefault(candidate.passage_id, []).append(
                candidate,
            )
        associations_by_sentence = {
            association.sentence_id: association
            for association in associations
        }

        enriched: list[SentenceAnalysis] = []
        for sentence in sentences:
            association = associations_by_sentence.get(sentence.id)
            if association is None:
                enriched.append(sentence)
                continue
            passage_candidates = candidates_by_passage[association.passage_id]
            snapshot = self._passage_snapshot(
                passage_candidates,
                sentence_theme_ids={theme["id"] for theme in sentence.themes},
            )
            enriched.append(replace(
                sentence,
                passages=(SentencePassageAnalysis(
                    id=self.ids.generate_ulid(),
                    passage_id=association.passage_id,
                    confidence=association.confidence,
                    reason=association.reason,
                    payload_snapshot=snapshot,
                ),),
            ))
        return tuple(enriched)

    @staticmethod
    def _passage_snapshot(
        candidates: list[ContextualPassageCandidate],
        *,
        sentence_theme_ids: set[str],
    ) -> dict:
        canonical = candidates[0]
        catalog_data = {
            "passage_id": canonical.passage_id,
            "short_text": canonical.short_text,
            "paraphrase": canonical.paraphrase,
            "interpretation_note": canonical.interpretation_note,
            "locator": canonical.locator,
            "priority": canonical.priority,
            "start_page": canonical.start_page,
            "end_page": canonical.end_page,
            "work": {
                "id": canonical.work_id,
                "title": canonical.work_title,
                "author_name": canonical.author_name,
            },
        }
        for candidate in candidates[1:]:
            comparable = {
                "passage_id": candidate.passage_id,
                "short_text": candidate.short_text,
                "paraphrase": candidate.paraphrase,
                "interpretation_note": candidate.interpretation_note,
                "locator": candidate.locator,
                "priority": candidate.priority,
                "start_page": candidate.start_page,
                "end_page": candidate.end_page,
                "work": {
                    "id": candidate.work_id,
                    "title": candidate.work_title,
                    "author_name": candidate.author_name,
                },
            }
            if comparable != catalog_data:
                raise InvalidInterpretationError(
                    "Inconsistent contextual passage catalog data.",
                    reason=FailureReason.PASSAGES,
                )

        theme_matches: dict[str, float] = {}
        for candidate in candidates:
            if candidate.matched_theme_id in sentence_theme_ids:
                theme_matches[candidate.matched_theme_id] = max(
                    theme_matches.get(candidate.matched_theme_id, 0),
                    candidate.matched_theme_confidence,
                )
        return {
            "schema_version": 1,
            **catalog_data,
            "theme_matches": [
                {"theme_id": theme_id, "confidence": confidence}
                for theme_id, confidence in sorted(
                    theme_matches.items(),
                    key=lambda item: (-item[1], item[0]),
                )
            ],
        }
