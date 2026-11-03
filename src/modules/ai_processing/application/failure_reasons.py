"""Allowlisted diagnostics. Never persist exception strings or provider bodies."""
from enum import Enum


class FailureReason(str, Enum):
    TIMEOUT = "provider_timeout"
    NETWORK = "provider_network_error"
    AUTH = "provider_authentication_error"
    PERMISSION = "provider_permission_error"
    MODEL = "provider_model_not_found"
    QUOTA = "provider_quota_exceeded"
    RATE_LIMIT = "provider_rate_limit"
    REQUEST = "provider_invalid_request"
    UNAVAILABLE = "provider_unavailable"
    HTTP = "provider_http_error"
    INCOMPLETE = "provider_incomplete_response"
    REFUSAL = "provider_refusal"
    RESPONSE = "provider_invalid_response"
    INVALID_RESULT = "invalid_interpretation"
    THEMES = "invalid_theme_selection"
    SENTENCES = "invalid_sentence_segmentation"
    CATALOG_CHANGED = "catalog_changed"
    PASSAGES = "invalid_passage_selection"
    INPUT = "invalid_journal_input"
    CATALOG = "catalog_unavailable"
    DATABASE = "database_error"
    INTERPRETATION = "interpretation_failed"
    UNEXPECTED = "unexpected_error"

    @property
    def message(self) -> str:
        return {
            self.TIMEOUT: "O provedor excedeu o tempo limite da análise.",
            self.NETWORK: "Não foi possível conectar ao provedor de IA.",
            self.AUTH: "O provedor recusou as credenciais configuradas.",
            self.PERMISSION: "A configuração não tem permissão para acessar o recurso solicitado.",
            self.MODEL: "O modelo ou recurso solicitado não foi encontrado no provedor.",
            self.QUOTA: "A quota disponível no provedor foi excedida.",
            self.RATE_LIMIT: "O limite de requisições do provedor foi atingido.",
            self.REQUEST: "O provedor rejeitou os parâmetros da solicitação.",
            self.UNAVAILABLE: "O provedor de IA apresentou indisponibilidade.",
            self.HTTP: "O provedor retornou um erro HTTP.",
            self.INCOMPLETE: "O provedor não concluiu a resposta da análise.",
            self.REFUSAL: "O provedor recusou produzir a análise.",
            self.RESPONSE: "O provedor retornou uma resposta vazia ou incompatível com o formato esperado.",
            self.INVALID_RESULT: "A análise retornada não atende ao contrato esperado.",
            self.THEMES: "A análise contém temas inexistentes, duplicados ou inconsistentes.",
            self.SENTENCES: "As frases da análise não reproduzem integralmente o texto original na ordem correta.",
            self.CATALOG_CHANGED: "Os temas selecionados foram alterados durante a análise.",
            self.PASSAGES: "A seleção de passagens contém associações inválidas ou inconsistentes.",
            self.INPUT: "A entrada do diário não atende aos requisitos da análise.",
            self.CATALOG: "Não foi possível consultar o catálogo de temas.",
            self.DATABASE: "Ocorreu uma falha de acesso ou gravação no banco de dados.",
            self.INTERPRETATION: "Não foi possível concluir a interpretação do texto.",
            self.UNEXPECTED: "O processamento encontrou uma falha interna não classificada.",
        }[self]
