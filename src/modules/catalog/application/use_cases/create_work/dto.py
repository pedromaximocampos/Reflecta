from dataclasses import dataclass

from src.modules.catalog.application.dto.work import WorkOutputDTO


@dataclass(frozen=True, slots=True)
class CreateAuthorInputDTO:
    name: str
    description: str = ""


@dataclass(frozen=True, slots=True)
class CreateWorkInputDTO:
    title: str
    synopsis: str
    work_type: str
    language: str
    author: CreateAuthorInputDTO

    @classmethod
    def from_dict(cls, data: dict) -> "CreateWorkInputDTO":
        author = data["author"]
        return cls(
            title=data["title"],
            synopsis=data["synopsis"],
            work_type=data["type"],
            language=data["language"],
            author=CreateAuthorInputDTO(
                name=author["name"],
                description=author.get("description", ""),
            ),
        )


CreateWorkOutputDTO = WorkOutputDTO
