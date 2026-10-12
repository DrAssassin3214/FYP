import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# These two files test service functions (explain_result, india_norms / india_norm_output) that belonged to the
# simulation, cost and decision features, which the lean app no longer exposes. They are kept on disk unchanged
# until their removal is confirmed, and are not collected because they cannot import.
collect_ignore = ["test_explain.py", "test_india_norms.py"]
