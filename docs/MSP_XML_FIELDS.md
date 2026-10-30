# Data taken from an MS Project XML file

Export from MS Project: **File > Save As > XML Format** (MSPDI). Native `.mpp` and Primavera `.xer` files are refused with a message.
This list is exactly what is read: the reader (`app/schedule/mspdi.py`) takes exactly these items and nothing else. Anything outside it is
either counted in the **Import check** panel as "in the file but not modelled", or ignored.

## Scope: masonry only

Only the masonry work is taken. A task counts as masonry when its name mentions brick, block, masonry, walling, wall, partition, parapet,
lintel, sill band, scaffold, DPC, mortar or "curing and inspection". Every other task is left out of the grid. The effect of the left-out
tasks is kept: the start a kept task gets from left-out predecessors becomes a start-to-start link from a "Programme start" milestone, and the
room left by left-out successors and the project finish becomes a link to a "Programme finish" milestone. The kept tasks therefore keep the
dates and total float they have in the full programme, and the Import check compares them with MS Project's own saved slack and dates.
If no task name matches, the whole schedule is kept and the panel says so.

Labour and material come only from assignments on the kept tasks: work resources give *Workers required* (sum of units), material
resources are listed with their quantity and unit. Stock cover, lead times and the other site facts are not in MS Project and are typed in
the Task information tabs. Resources or assignments on left-out tasks are ignored and counted.

## Taken from the file

| Item | XML element | Used for |
|---|---|---|
| Project name | `Project/Name` (or `Title`) | Shown on the schedule; fills the project name if empty |
| Hours per day | `MinutesPerDay` (default 480) | Converting durations and lags to working days |
| Project start | `StartDate` (else the first task's `Start`) | First date of the programme |
| Project calendar | `CalendarUID`, then `Calendars/Calendar`: `WeekDays` (`DayType` 1 = Sunday ... 7, `DayWorking`) and `Exceptions` (`FromDate`, `ToDate`, `DayWorking`); base calendars followed | Working weekdays and holidays, so Start/Finish dates skip days off |
| Task identity | `UID`, `ID`, `Name`, `WBS` | Row numbers, names, activity ID |
| Outline | `OutlineLevel`, `Summary`, `Milestone` | Summary rows (spans of their children), milestones |
| Duration | `Duration` (`PT#H#M#S`) | Planned duration in working days (hours / hours per day) |
| Links | `PredecessorLink`: `PredecessorUID`, `Type` (0 FF, 1 FS, 2 SF, 3 SS), `LinkLag` (tenths of a minute), `LagFormat` | Critical-path pass. Percentage and elapsed-time lags are ignored (taken as 0) and reported |
| Saved dates | `Start`, `Finish` | Only to compare with the tool's dates (Import check) |
| MS Project's own result | `Critical`, `TotalSlack` (tenths of a minute) | Only to compare with the tool's float and critical flag (Import check) |
| Percent complete | `PercentComplete` | Shown only |
| Labour | `Resources` (`Type` 1 = work) with `Assignments` (`TaskUID`, `ResourceUID`, `Units`), kept tasks only | Workers required, and the crew shown in the Labour tab |
| Material | `Resources` (`Type` 0 = material, `MaterialLabel`) with `Assignments` (`Units` = quantity), kept tasks only | Shown in the Material tab (quantity and unit) |

## Counted but not modelled (reported in the Import check)

Date constraints (`ConstraintType` other than 0), tasks on their own calendar, manually scheduled tasks, inactive tasks, baselines, and
resource assignments on left-out tasks. Resource levelling and cost resources are not modelled either.

## Refused

Native `.mpp` files, files with a DOCTYPE or ENTITY declaration, files over 30 MB or over 20,000 tasks, files that are not in the
Microsoft Project namespace, duplicate task UIDs, a loop in the links, and files with no tasks or only summary tasks.

## How it is checked

* `tests/test_schedule_msp.py` and `tests/test_schedule_grid.py`: hand-worked early/late times, link types and lags, calendar and
  holiday dates, refusals.
* **Import check** panel after every import: tasks and links read versus in the file, total slack and dates compared with the values
  MS Project saved, critical flag compared, and the not-modelled counts.
* The bundled `examples/example_schedule_msp.xml` carries slack, critical flags and dates that were generated from hand-checked
  early/late times, not exported from MS Project. It exercises the check but is **not** evidence that real exports agree: test at least
  one real export before relying on the import.
