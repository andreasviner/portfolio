# Color Polygraph

A 2020 hobby project that turned a color-preference survey into a small
neural net guessing age, gender, and self-reported mood from the colors
people picked. This folder holds the raw export, the cleaner, the
aggregated voxel data the live viz reads, and the original glue scripts.

Live page: https://andreaslindeman.com/projects/color-polygraph

## How it worked

Each participant answered three demographic questions (age, gender, and a
1 to 10 mood rating), then went through sixteen rounds of "pick your
favourite out of four random color swatches". The sixteen winners then
played a knockout: four groups of four, then one final group of four,
leaving one color at the end.

Alongside every click the survey logged the meta-signal: time per
question, click coordinates relative to the swatch centre, total session
time, and click order. The model leaned on these as much as the color
picks themselves.

The mail went out through the Oslo school directory. Around 160,000
students opened it; around 20,000 finished the full survey; 6,731 sessions
survived the cleaning pipeline below.

## Files

- `code/save.ligma` is the raw JSON export from the survey backend, around
  10 MB. Each entry is `[id, time, ip, age, mood, gender, valg, tider, farger]`.
- `code/andy.py` is the original loader, filter, and helper class I wrote
  in 2020 to download, deduplicate, and explore the data. The docstring at
  the bottom (Norwegian) is the user guide I wrote for a classmate.
- `code/Start_denne_Sander.py` is my classmate Sander's starter script.
- `new_code/treat_data.py` is the aggregator that turns `save.ligma` into
  the compact `preferences.json` the portfolio page reads. It quantises
  colors into an 8x8x8 RGB grid, scores each voxel by how often colors
  from that bin survived the knockout versus how often they were shown,
  and breaks the result down by gender and age bucket.
- `preferences.json` is the aggregator output, around 75 KB. Already
  binned, ready to load.
- `info.json` and `info.data` are portfolio metadata.

## The save.ligma row format

```
[
  id,       # numeric ID assigned per recipient
  time,     # unix start time, "0" if the mail was opened in an untrackable client
  ip,       # client IP, "0" if same
  age,      # self-reported, integer, "0" if blank
  mood,     # 0 happy, 60 glum
  gender,   # "g" boy, "j" girl, "u" undefined
  valg,     # 21 ASCII digits: 16 first-round picks (0-3) + 4 knockout picks + 1 final
  tider,    # 21 cumulative timestamps in ms (last entry = total session time)
  farger    # [
            #   [64 colors that were offered],
            #   [16 first-round winners],
            #   [4 knockout winners],
            #   final winner
            # ]
]
```

Each color is `[r, g, b]` with channels in `0..255`.

## Cleaning

`preferences.json` is built from 6,731 sessions out of the roughly 20,000
finishers. The rest fail at least one of these checks (all live at the top
of `new_code/treat_data.py`):

- Self-reported gender must match the gender on file in the Oslo school
  directory. A recipient flagged as a boy reporting being a girl (or the
  other way round) was almost always joking.
- Self-reported age must be plausibly close to the directory age. A
  first-grader claiming to be 47 is not answering seriously.
- Hard age bounds: under 6 dropped, over 68 dropped. Roughly half of all
  "adults" in the raw data claimed to be exactly 69.
- One-coordinate spammers dropped: sessions where almost every click landed
  on the same screen coordinate are not picking colors, they are banging
  a corner.
- Speed runners dropped: anyone averaging under 0.3 seconds per question.
  You cannot read four swatches that fast.
- Plus minor heuristics for duplicate IDs, missing required fields,
  impossible total times, and sessions where the mouse never moved.

## Running the aggregator

```
python new_code/treat_data.py
```

Reads `code/save.ligma` and writes `preferences.json`. No dependencies
beyond the Python stdlib.

## Reusing the data

The raw `save.ligma` is enough to train your own model. If you want a
quick exploratory cube without writing your own aggregator, fetch
`preferences.json` instead. It is already binned and per-bucket scored.

Either way: ages were self-reported, the directory match is not perfect,
and 2020-era Oslo school students are not a representative sample of
anyone in particular. Do not ship a color personality test on top of it.
