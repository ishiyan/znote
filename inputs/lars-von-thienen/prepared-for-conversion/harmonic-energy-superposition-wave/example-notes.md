# Example provenance

All six source histories are SYNTHETIC transformations of the supplied
INPUT_CLOSE: in lag order 8,11,19,27,30,38, source j rotates the input
by 7*j samples and scales by 1+0.1*j. The six source years for target
2021 are 2013,2010,2002,1994,1991,1983. Dates are artificial evenly
selected weekdays, not exchange calendars or actual historical records.

example-model-*.json files are checked full-year fits with max_period=80,
candidate_pool=10 and max_components=7, matching the synthetic reference
source-generation convention. example-superposition.json and example-wave.csv
use these saved models with RMS normalization and ordinal extension.

example-history.csv contains all six synthetic histories in increasing date
order. The history-mode example uses the annual decoder's default
max_period=125 and records the explicit completeness assertion.
example-history-superposition.json and example-history-wave.csv therefore
can differ from the imported-model example.

example-target-calendar.csv has 252 artificial target-year session dates.
No target prices are used. None of these files is the source's 2008 example.
