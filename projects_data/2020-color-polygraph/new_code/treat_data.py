"""
Aggregate save.ligma into a set of compact JSON files for the portfolio
visualization.

The output is split so the page can render the default "girls likes" view
almost instantly and only fetch heavier detail data when the user actually
opens a filter:

  summary.json
    Metadata, favourite/least-favourite swatches, the mood-by-group grid,
    overall stats, and two pre-aggregated bracket buckets (g_all and j_all)
    that cover every gender preset (boys/girls/diff/both/free) when neither
    the age, mood nor time-of-day filter is engaged.

  by_age.json
    Per-(gender, single-age) bracket counts. Loaded the first time the user
    turns on the age slider. Keys: g_6..g_68, j_6..j_68. Each bucket also
    carries mood_mean and time_mean for approximate cross-filter gating.

  by_mood.json
    Per-(gender, mood-score range) bracket counts. Loaded the first time
    the user turns on the mood slider. Keys: g_happy..g_glum, j_happy..j_glum.

  by_time.json
    Per-(gender, hour-of-day) bracket counts. Loaded the first time the user
    turns on the time-of-day slider. Keys: g_0..g_23, j_0..j_23. Hours are
    interpreted in Europe/Oslo local time since the survey was run there.

For every bucket we store, per 8x8x8 RGB voxel that was offered enough
times, the array [offered, round1, round2, final]:
  - offered: how often a color in that voxel was shown
  - round1 : survived round 1 (4 -> 1)
  - round2 : survived round 2 (16 -> 4)
  - final  : the very last pick
The front-end mixes these four counts with user-controlled weights.
"""

import datetime
import json
import os
from collections import Counter

try:
    from zoneinfo import ZoneInfo
    OSLO = ZoneInfo("Europe/Oslo")
except ImportError:
    OSLO = None

HERE = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(HERE, "..", "code", "save.ligma")
OUT_DIR = os.path.join(HERE, "..")

GRID = 8
SHIFT = 8 - 3  # quantize 0..255 -> 0..7

# Single-age bins. Mirror what the age slider exposes (6..68).
AGE_BUCKETS = [(str(a), a, a) for a in range(6, 69)]

# Age groupings used by the "mood by group" display card.
MOOD_GRID_BUCKETS = [
    ("kids",     6,  9),
    ("preteen", 10, 12),
    ("early",   13, 15),
    ("late",    16, 18),
    ("young",   19, 25),
    ("adult",   26, 68),
]

# Mood-score ranges for the mood slider (raw mood scale spans 0..60,
# where 0 is happy and 60 is glum).
MOOD_LEVEL_BUCKETS = [
    ("happy",   0,  9),
    ("upbeat", 10, 19),
    ("steady", 20, 29),
    ("low",    30, 39),
    ("blue",   40, 49),
    ("glum",   50, 60),
]

# Hour-of-day buckets for the time-of-day slider (0..23 local time).
HOUR_BUCKETS = [(str(h), h, h) for h in range(24)]

GENDERS = ["g", "j"]

# Minimum offered count to keep a voxel in a bucket.
MIN_OFFERED_BUCKET = 3
MIN_OFFERED_AGGREGATE = 1


def voxel(rgb):
    r, g, b = rgb
    return (r >> SHIFT, g >> SHIFT, b >> SHIFT)


def vkey(vx):
    return vx[0] * GRID * GRID + vx[1] * GRID + vx[2]


def hex_of(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def age_bucket_for(age):
    for name, lo, hi in AGE_BUCKETS:
        if lo <= age <= hi:
            return name
    return None


def mood_level_for(score):
    for name, lo, hi in MOOD_LEVEL_BUCKETS:
        if lo <= score <= hi:
            return name
    return None


def hour_minute_for(timestamp):
    """Return (hour, minute) in Oslo local time, or (None, None) if unusable."""
    try:
        t = int(timestamp)
    except (TypeError, ValueError):
        return None, None
    if t <= 0:
        return None, None
    try:
        if OSLO is not None:
            dt = datetime.datetime.fromtimestamp(t, tz=OSLO)
        else:
            dt = datetime.datetime.fromtimestamp(t)
        return dt.hour, dt.minute
    except (OSError, OverflowError, ValueError):
        return None, None


def hour_for(timestamp):
    h, _ = hour_minute_for(timestamp)
    return h


def is_valid(row):
    try:
        if row[5] not in ("g", "j"):
            return False
        age = int(row[3])
        if not (5 <= age <= 68):
            return False
        if row[8] == "no data":
            return False
        if len(row[8]) < 4:
            return False
        if len(row[8][0]) < 64 or len(row[8][1]) < 16 or len(row[8][2]) < 4:
            return False
        if len(row[7]) < 2:
            return False
        if int(row[7][-1]) < 15000:
            return False
        return True
    except Exception:
        return False


def empty_bucket():
    return {
        "offered": Counter(),
        "round1":  Counter(),
        "round2":  Counter(),
        "final":   Counter(),
        "n":       0,
        "mood":    0,
        "hour":    0,
        "n_hour":  0,
        "dur_ms":  0,    # total test duration sum (ms)
        "perq_ms": 0,    # mean per-question time sum (ms)
        "n_dur":   0,    # count of sessions with parseable timing
    }


def encode_bucket(b, min_offered, with_means):
    n = b["n"]
    vox = {}
    for v, off in b["offered"].items():
        if off < min_offered:
            continue
        vox[v] = [
            off,
            b["round1"].get(v, 0),
            b["round2"].get(v, 0),
            b["final"].get(v, 0),
        ]
    out = {"n": n, "v": vox}
    if with_means:
        out["mood_mean"] = round((b["mood"] / n) if n else 0, 2)
        out["time_mean"] = round((b["hour"] / b["n_hour"]) if b["n_hour"] else 0, 2)
        if b["n_dur"]:
            out["dur_sec"]  = round(b["dur_ms"]  / b["n_dur"] / 1000, 2)
            out["perq_sec"] = round(b["perq_ms"] / b["n_dur"] / 1000, 3)
        else:
            out["dur_sec"]  = 0
            out["perq_sec"] = 0
    return out


DURATION_MIN_MS = 15_000     # below 15 s, the row is filtered upstream anyway
DURATION_MAX_MS = 600_000    # above 10 min: tab was left open, drop for averages


def session_timing(row):
    """Returns (total_ms, mean_per_question_ms) or (None, None) if unusable
    or out of plausible bounds."""
    try:
        tider = [int(x) for x in row[7]]
    except (TypeError, ValueError):
        return None, None
    if len(tider) < 2:
        return None, None
    total = tider[-1]
    if total < DURATION_MIN_MS or total > DURATION_MAX_MS:
        return None, None
    # tider[i] is cumulative ms at click i, starting from start-of-test.
    # Per-question deltas: tider[0] (first click), tider[i] - tider[i-1] for the rest.
    deltas = [tider[0]]
    for i in range(1, len(tider)):
        d = tider[i] - tider[i - 1]
        if d < 0:
            return None, None
        deltas.append(d)
    if not deltas:
        return None, None
    return total, sum(deltas) / len(deltas)


def main():
    with open(SOURCE, "r", encoding="utf-8") as fh:
        rows = json.load(fh)

    print(f"loaded {len(rows)} raw rows")

    age_buckets = {}
    mood_buckets = {}
    time_buckets = {}
    all_buckets = {}
    for g in GENDERS:
        all_buckets[g] = empty_bucket()
        for name, _, _ in AGE_BUCKETS:
            age_buckets[(g, name)] = empty_bucket()
        for name, _, _ in MOOD_LEVEL_BUCKETS:
            mood_buckets[(g, name)] = empty_bucket()
        for name, _, _ in HOUR_BUCKETS:
            time_buckets[(g, name)] = empty_bucket()

    overall_final = Counter()
    overall_offered = Counter()
    overall_picked = Counter()
    voxel_offered = Counter()
    voxel_round1 = Counter()
    voxel_round2 = Counter()
    voxel_final = Counter()
    used = 0

    for row in rows:
        if not is_valid(row):
            continue
        gender = row[5]
        age = int(row[3])
        ab = age_bucket_for(age)
        if ab is None:
            continue

        mood_score = int(row[4]) if str(row[4]).lstrip("-").isdigit() else None
        ml = mood_level_for(mood_score) if mood_score is not None else None
        hour = hour_for(row[1])
        total_ms, perq_ms = session_timing(row)

        offered_arr = row[8][0]
        round1_arr  = row[8][1]
        round2_arr  = row[8][2]
        final_rgb   = row[8][3]

        targets = [
            age_buckets[(gender, ab)],
            all_buckets[gender],
        ]
        if ml is not None:
            targets.append(mood_buckets[(gender, ml)])
        if hour is not None:
            targets.append(time_buckets[(gender, str(hour))])

        for t in targets:
            t["n"] += 1
            if mood_score is not None:
                t["mood"] += mood_score
            if hour is not None:
                t["hour"] += hour
                t["n_hour"] += 1
            if total_ms is not None:
                t["dur_ms"]  += total_ms
                t["perq_ms"] += perq_ms
                t["n_dur"]   += 1

        round1_set = {tuple(c) for c in round1_arr}
        round2_set = {tuple(c) for c in round2_arr}
        final_tuple = tuple(final_rgb)

        for c in offered_arr:
            tc = tuple(c)
            v = vkey(voxel(tc))
            voxel_offered[v] += 1
            overall_offered[hex_of(tc)] += 1
            r1_hit = tc in round1_set
            r2_hit = tc in round2_set
            fn_hit = tc == final_tuple
            if r1_hit:
                voxel_round1[v] += 1
                overall_picked[hex_of(tc)] += 1
            if r2_hit:
                voxel_round2[v] += 1
            if fn_hit:
                voxel_final[v] += 1
                overall_final[hex_of(tc)] += 1
            for t in targets:
                t["offered"][v] += 1
                if r1_hit:
                    t["round1"][v] += 1
                if r2_hit:
                    t["round2"][v] += 1
                if fn_hit:
                    t["final"][v] += 1

        used += 1

    print(f"used {used} valid rows")

    # Per-age bucket data (heavy file)
    by_age_out = {}
    for (gender, name), b in age_buckets.items():
        by_age_out[f"{gender}_{name}"] = encode_bucket(
            b, min_offered=MIN_OFFERED_BUCKET, with_means=True
        )

    # Per-mood bucket data
    by_mood_out = {}
    for (gender, name), b in mood_buckets.items():
        by_mood_out[f"{gender}_{name}"] = encode_bucket(
            b, min_offered=MIN_OFFERED_BUCKET, with_means=True
        )

    # Per-hour bucket data
    by_time_out = {}
    for (gender, name), b in time_buckets.items():
        by_time_out[f"{gender}_{name}"] = encode_bucket(
            b, min_offered=MIN_OFFERED_BUCKET, with_means=True
        )

    # Pre-aggregated "all" buckets per gender (cheap to include in summary)
    summary_buckets = {}
    for gender, b in all_buckets.items():
        summary_buckets[f"{gender}_all"] = encode_bucket(
            b, min_offered=MIN_OFFERED_AGGREGATE, with_means=True
        )

    # Favourites / least-favourites across the whole dataset
    voxel_rows = []
    for v, off in voxel_offered.items():
        if off < 200:
            continue
        r1 = voxel_round1.get(v, 0)
        r2 = voxel_round2.get(v, 0)
        fn = voxel_final.get(v, 0)
        love = (r1 + 2 * r2 + 4 * fn) / off
        reject_ratio = r1 / off
        r = ((v // (GRID * GRID)) & 7)
        g = ((v // GRID) & 7)
        b = (v & 7)
        center = ((r * 32) + 16, (g * 32) + 16, (b * 32) + 16)
        voxel_rows.append((hex_of(center), love, reject_ratio, off, r1, fn))

    voxel_rows.sort(key=lambda x: x[1], reverse=True)
    fav_list = [
        {"hex": h, "ratio": round(love, 4), "offered": off, "finals": fn}
        for h, love, _, off, _, fn in voxel_rows[:12]
    ]

    voxel_rows.sort(key=lambda x: x[2])
    least_list = [
        {"hex": h, "ratio": round(rej, 4), "offered": off, "picked": r1}
        for h, _, rej, off, r1, _ in voxel_rows[:12]
    ]

    # Session-level demographic distributions (re-walk for safety)
    age_dist = Counter()
    gender_dist = Counter()
    mood_total = 0
    mood_n = 0
    for row in rows:
        if not is_valid(row):
            continue
        age_dist[int(row[3])] += 1
        gender_dist[row[5]] += 1
        if str(row[4]).lstrip("-").isdigit():
            mood_total += int(row[4])
            mood_n += 1

    # Mood-by-group display data (uses the age groupings, not the new mood levels)
    mood_grid = {}
    for gender in GENDERS:
        for mname, mlo, mhi in MOOD_GRID_BUCKETS:
            n_sum = 0
            mood_sum = 0
            for a in range(mlo, mhi + 1):
                b = age_buckets.get((gender, str(a)))
                if not b:
                    continue
                n_sum += b["n"]
                mood_sum += b["mood"]
            mood_grid[f"{gender}_{mname}"] = {
                "n": n_sum,
                "mood_mean": round(mood_sum / n_sum, 2) if n_sum else 0,
            }

    # Pre-computed series for the breakdown plots. Stored on summary.json so
    # the page can draw the plots without waiting for the heavier detail files.
    def series_by_age(getter):
        out = {}
        for g in GENDERS:
            series = []
            for name, _, _ in AGE_BUCKETS:
                b = age_buckets[(g, name)]
                series.append({"a": int(name), "v": getter(b), "n": b["n"]})
            out[g] = series
        return out

    def series_by_hour(getter):
        out = {}
        for g in GENDERS:
            series = []
            for name, _, _ in HOUR_BUCKETS:
                b = time_buckets[(g, name)]
                series.append({"h": int(name), "v": getter(b), "n": b["n"]})
            out[g] = series
        return out

    def happiness_from(b):
        if not b["n"]:
            return None
        return round(1 - (b["mood"] / b["n"]) / 60.0, 4)

    def mean_ratio(numer_key, denom_key, b, scale=1.0):
        d = b[denom_key]
        if not d:
            return None
        return round((b[numer_key] / d) * scale, 4)

    happiness_by_age  = series_by_age(happiness_from)

    # Hourly response counts per gender (used by "Responses through the day").
    responses_by_hour = {}
    for g in GENDERS:
        series = []
        for name, _, _ in HOUR_BUCKETS:
            series.append({"h": int(name), "n": time_buckets[(g, name)]["n"]})
        responses_by_hour[g] = series

    # Daily response counts since launch (used by "Responses over the first days").
    # Launch day is the first day with a valid response in the dataset.
    DAYS_TO_SHOW = 30
    response_days = {g: [0] * DAYS_TO_SHOW for g in GENDERS}
    launch_date = None
    daily_dates = []
    for raw in rows:
        if not is_valid(raw):
            continue
        try:
            t = int(raw[1])
            if t <= 0:
                continue
            d = (datetime.datetime.fromtimestamp(t, tz=OSLO)
                 if OSLO is not None
                 else datetime.datetime.fromtimestamp(t)).date()
        except (TypeError, ValueError, OSError, OverflowError):
            continue
        if launch_date is None or d < launch_date:
            launch_date = d
    if launch_date is not None:
        for raw in rows:
            if not is_valid(raw):
                continue
            gender = raw[5]
            try:
                t = int(raw[1])
                if t <= 0:
                    continue
                d = (datetime.datetime.fromtimestamp(t, tz=OSLO)
                     if OSLO is not None
                     else datetime.datetime.fromtimestamp(t)).date()
            except (TypeError, ValueError, OSError, OverflowError):
                continue
            delta = (d - launch_date).days
            if 0 <= delta < DAYS_TO_SHOW:
                response_days[gender][delta] += 1
        daily_dates = [
            (launch_date + datetime.timedelta(days=i)).isoformat()
            for i in range(DAYS_TO_SHOW)
        ]
    responses_by_day = {
        "launch_date": launch_date.isoformat() if launch_date else None,
        "dates": daily_dates,
        "g": response_days["g"],
        "j": response_days["j"],
    }

    # Happiness through the day uses a mixed-granularity x axis:
    #   skip middle-of-the-night hours (1..5), where the dataset has 3-17
    #     responses an hour and the line is pure noise;
    #   hourly buckets for the shoulder hours (0, 6, 7, 22, 23);
    #   15-minute buckets through the most active stretch (8..21), so the
    #     curve is smoother where data is dense.
    NIGHT_HOURS    = {1, 2, 3, 4, 5}
    SHOULDER_HOURS = {0, 6, 7, 22, 23}
    ACTIVE_START, ACTIVE_END = 8, 21
    MIN_BIN_N = 20  # combined boys+girls per bin to include it

    quarter = {g: {} for g in GENDERS}  # gender -> {(h, q): [mood_sum, n]}
    for raw in rows:
        if not is_valid(raw):
            continue
        gender = raw[5]
        h, m = hour_minute_for(raw[1])
        if h is None:
            continue
        if not str(raw[4]).lstrip("-").isdigit():
            continue
        mood = int(raw[4])
        q = m // 15
        key = (h, q)
        bucket = quarter[gender].setdefault(key, [0, 0])
        bucket[0] += mood
        bucket[1] += 1

    def bin_sum(target, h, q):
        if q is None:
            ms = sum(target.get((h, qq), [0, 0])[0] for qq in range(4))
            nn = sum(target.get((h, qq), [0, 0])[1] for qq in range(4))
            return ms, nn
        return tuple(target.get((h, q), [0, 0]))

    happiness_by_hour = {g: [] for g in GENDERS}
    for h in range(24):
        if h in NIGHT_HOURS:
            continue
        bins = [None] if h in SHOULDER_HOURS else list(range(4))
        for q in bins:
            n_g = bin_sum(quarter["g"], h, q)[1]
            n_j = bin_sum(quarter["j"], h, q)[1]
            if n_g + n_j < MIN_BIN_N:
                continue
            x = (h + 0.5) if q is None else (h + q * 0.25 + 0.125)
            for g in GENDERS:
                ms, nn = bin_sum(quarter[g], h, q)
                v = None if nn == 0 else round(1 - (ms / nn) / 60.0, 4)
                happiness_by_hour[g].append({"h": round(x, 4), "v": v, "n": nn})
    duration_by_age   = series_by_age(lambda b: mean_ratio("dur_ms",  "n_dur", b, 1 / 1000.0))
    perq_by_age       = series_by_age(lambda b: mean_ratio("perq_ms", "n_dur", b, 1 / 1000.0))
    count_by_age      = series_by_age(lambda b: b["n"])

    # Per-gender duration and per-question speed histograms.
    bin_edges_sec = list(range(0, 301, 15))   # 0,15,30..300 sec (last is 5min+ overflow)
    perq_edges    = list(range(0, 21))        # 0..20 sec per-question
    duration_hist = {g: [0] * len(bin_edges_sec) for g in GENDERS}
    perq_hist     = {g: [0] * len(perq_edges)    for g in GENDERS}

    # Mean time spent on each click in the 21-question bracket.
    N_QUESTIONS = 21
    perslide_sum   = {g: [0.0] * N_QUESTIONS for g in GENDERS}
    perslide_count = {g: [0]   * N_QUESTIONS for g in GENDERS}

    for raw in rows:
        if not is_valid(raw):
            continue
        g = raw[5]
        total_ms, perq_ms = session_timing(raw)
        if total_ms is None:
            continue
        sec = total_ms / 1000.0
        duration_hist[g][min(int(sec // 15), len(bin_edges_sec) - 1)] += 1
        pq_sec = perq_ms / 1000.0
        perq_hist[g][min(int(pq_sec), len(perq_edges) - 1)] += 1
        try:
            tider = [int(x) for x in raw[7]]
        except (TypeError, ValueError):
            continue
        prev = 0
        for q in range(min(N_QUESTIONS, len(tider))):
            delta = tider[q] - prev
            if delta < 0:
                break
            perslide_sum[g][q]   += delta
            perslide_count[g][q] += 1
            prev = tider[q]

    time_per_slide = {}
    for g in GENDERS:
        series = []
        for q in range(N_QUESTIONS):
            n = perslide_count[g][q]
            v = round(perslide_sum[g][q] / n / 1000, 3) if n else None
            series.append({"q": q + 1, "v": v, "n": n})
        time_per_slide[g] = series

    summary = {
        "grid": GRID,
        "age_buckets": [
            {"name": n, "lo": lo, "hi": hi} for n, lo, hi in AGE_BUCKETS
        ],
        "mood_buckets": [
            {"name": n, "lo": lo, "hi": hi} for n, lo, hi in MOOD_GRID_BUCKETS
        ],
        "mood_levels": [
            {"name": n, "lo": lo, "hi": hi} for n, lo, hi in MOOD_LEVEL_BUCKETS
        ],
        "time_buckets": [
            {"name": n, "lo": lo, "hi": hi} for n, lo, hi in HOUR_BUCKETS
        ],
        "mood_data": mood_grid,
        "favourites": fav_list,
        "least_favourites": least_list,
        "stats": {
            "total_valid": used,
            "raw_rows": len(rows),
            "gender": dict(gender_dist),
            "age_hist": dict(sorted(age_dist.items())),
            "mood_mean": round(mood_total / max(1, mood_n), 2),
        },
        "buckets": summary_buckets,
        "viz": {
            "happiness_by_age":  happiness_by_age,
            "happiness_by_hour": happiness_by_hour,
            "duration_by_age":   duration_by_age,
            "perq_by_age":       perq_by_age,
            "count_by_age":      count_by_age,
            "responses_by_hour": responses_by_hour,
            "responses_by_day":  responses_by_day,
            "time_per_slide":    time_per_slide,
            "duration_hist":     {"edges": bin_edges_sec, "g": duration_hist["g"], "j": duration_hist["j"]},
            "perq_hist":         {"edges": perq_edges,    "g": perq_hist["g"],     "j": perq_hist["j"]},
        },
    }

    summary_path = os.path.join(OUT_DIR, "summary.json")
    by_age_path = os.path.join(OUT_DIR, "by_age.json")
    by_mood_path = os.path.join(OUT_DIR, "by_mood.json")
    by_time_path = os.path.join(OUT_DIR, "by_time.json")

    with open(summary_path, "w", encoding="utf-8") as fh:
        json.dump(summary, fh, separators=(",", ":"))
    with open(by_age_path, "w", encoding="utf-8") as fh:
        json.dump({"buckets": by_age_out}, fh, separators=(",", ":"))
    with open(by_mood_path, "w", encoding="utf-8") as fh:
        json.dump({"buckets": by_mood_out}, fh, separators=(",", ":"))
    with open(by_time_path, "w", encoding="utf-8") as fh:
        json.dump({"buckets": by_time_out}, fh, separators=(",", ":"))

    for label, path in (
        ("summary", summary_path),
        ("by_age", by_age_path),
        ("by_mood", by_mood_path),
        ("by_time", by_time_path),
    ):
        size_kb = os.path.getsize(path) / 1024
        print(f"wrote {label}.json ({size_kb:.1f} kB)")


if __name__ == "__main__":
    main()
