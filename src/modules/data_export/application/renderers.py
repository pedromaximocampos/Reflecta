import json
from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from .models import UserDataExportPackage


README = """Exportação de dados do Reflecta

Este pacote contém uma cópia dos dados registrados na conta no momento indicado
em manifest.json. Os arquivos JSON usam UTF-8 e datas no padrão ISO 8601.

Conteúdo:
- perfil.json: informações cadastrais da conta;
- reflexoes.json: entradas do diário e respectivas análises;
- analises-contextuais.json: análises de períodos do diário;
- compartilhamentos.json: conteúdos compartilhados e seus estados;
- orientacoes.json: atividades e reflexões guiadas recebidas;
- foto-perfil.webp: foto da conta, quando disponível.

Credenciais, senhas, tokens, embeddings e registros operacionais não fazem parte
da exportação. Guarde este arquivo em local seguro, pois ele pode conter conteúdo
pessoal e sensível escrito pelo próprio usuário.
"""


def _json_bytes(value) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        separators=(",", ": "),
    ).encode("utf-8")


def render_json_export(package: UserDataExportPackage) -> bytes:
    return _json_bytes(package.json_document())


def render_zip_export(package: UserDataExportPackage) -> bytes:
    files = [
        "LEIA-ME.txt",
        "manifest.json",
        "perfil.json",
        "reflexoes.json",
        "analises-contextuais.json",
        "compartilhamentos.json",
        "orientacoes.json",
    ]
    if package.avatar is not None:
        files.append(package.avatar.filename)

    avatar_metadata = None
    if package.avatar is not None:
        avatar_metadata = {
            "filename": package.avatar.filename,
            "content_type": package.avatar.content_type,
        }

    output = BytesIO()
    with ZipFile(output, mode="w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("LEIA-ME.txt", README.encode("utf-8"))
        archive.writestr(
            "manifest.json",
            _json_bytes(package.manifest(files=files)),
        )
        archive.writestr(
            "perfil.json",
            _json_bytes({**package.account.profile, "avatar": avatar_metadata}),
        )
        archive.writestr(
            "reflexoes.json",
            _json_bytes({"entries": list(package.journal.entries)}),
        )
        archive.writestr(
            "analises-contextuais.json",
            _json_bytes(
                {"context_analyses": list(package.journal.context_analyses)}
            ),
        )
        archive.writestr(
            "compartilhamentos.json",
            _json_bytes({"shares": list(package.sharing.shares)}),
        )
        archive.writestr(
            "orientacoes.json",
            _json_bytes(
                {
                    "professional_activities": list(
                        package.sharing.professional_activities
                    )
                }
            ),
        )
        if package.avatar is not None:
            archive.writestr(package.avatar.filename, package.avatar.content)
    return output.getvalue()
