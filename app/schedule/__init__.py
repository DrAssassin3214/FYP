"""Project schedules (Microsoft Project XML) for the Input tab: parse, critical-path check, and bridge to the analysis case."""
from .mspdi import ScheduleError, parse_mspdi  # noqa: F401
from .cpm import analyse  # noqa: F401
