"""The data files the tool reads must be consistent: no dangling risk / study / evidence ids, no RII outside (0, 1],
no rank that contradicts the RII order inside a study (scripts/check_data.py; it never edits a file)."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_check_data_script_reports_no_findings():
    out = subprocess.run([sys.executable, str(ROOT / "scripts" / "check_data.py")], cwd=ROOT, capture_output=True,
                         text=True, timeout=120)
    assert out.returncode == 0, out.stdout[-1500:] + out.stderr[-500:]
    assert "FINDING" not in out.stdout and out.stdout.strip().endswith("OK")
