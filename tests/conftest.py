import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# These two files test service functions (explain_result, india_norms / india_norm_output) that belonged to the
# simulation, cost and decision features, which the lean app no longer exposes. They are kept on disk unchanged
# until their removal is confirmed, and are not collected because they cannot import.
collect_ignore = ["test_explain.py", "test_india_norms.py"]


import pytest  # noqa: E402


@pytest.fixture(autouse=True)
def _isolated_data_dir(tmp_path, monkeypatch):
    """Every test sees only the bundled data: no installed online pack, no search cache, no network update."""
    monkeypatch.setenv("BRICKSLY_DATA_DIR", str(tmp_path / "userdata"))
    monkeypatch.setenv("BRICKSLY_PACK_URL", "")
