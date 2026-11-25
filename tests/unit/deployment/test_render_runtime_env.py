import importlib.util
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[3]
    / "infra"
    / "deployment"
    / "aws"
    / "render_runtime_env.py"
)
SPEC = importlib.util.spec_from_file_location("render_runtime_env", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_compose_value_escapes_dollar_signs() -> None:
    assert MODULE._compose_value("prefix$value") == '"prefix$$value"'
