Sure! Here's a clear walkthrough of how the system works and how to enter numbers.

---

## How the MCDSS works

The system uses **Simple Additive Weighting**: every alternative gets a score on each criterion, that score is multiplied by the criterion's weight, everything is summed up, and the total is normalized to a **0–100% final score**.

---

## Step 1 — Run the program

```bash
python mcdss.py
```

You'll see:
```
  1. Run built-in demo
  2. Interactive session

Choose (1/2):
```

Type `2` and press Enter for a live session.

---

## Step 2 — Give your decision a title

```
Decision title: Choosing a laptop
```

This is just a label. Press Enter to skip.

---

## Step 3 — Enter criteria

Criteria are the **factors that matter** to your decision. For each one you also set a **weight** — how important it is relative to the others.

```
Criterion name: Price
Weight for 'Price' (1–10): 8

Criterion name: Battery life
Weight for 'Battery life' (1–10): 6

Criterion name: Performance
Weight for 'Performance' (1–10): 9

Criterion name:        ← blank line to stop
```

**Weight guidance:**

| Weight | Meaning |
|--------|---------|
| 1–3 | Nice to have, not critical |
| 4–6 | Moderately important |
| 7–9 | Very important |
| 10 | Absolute top priority |

Weights don't need to add up to anything — they're normalized internally. So `8, 6, 9` and `4, 3, 4.5` would produce identical rankings.

---

## Step 4 — Enter alternatives

Alternatives are the **options you're choosing between**.

```
Alternative name: MacBook Air
Alternative name: Dell XPS 13
Alternative name: ThinkPad X1
Alternative name:        ← blank line to stop
```

---

## Step 5 — Score each alternative (0–10)

For every alternative, you score it on **each criterion** from 0 (worst) to 10 (best).

```
Scores for 'MacBook Air':
  Price: 6          ← expensive, so low score
  Battery life: 9   ← excellent battery
  Performance: 8    ← very fast

Scores for 'Dell XPS 13':
  Price: 8
  Battery life: 7
  Performance: 7

Scores for 'ThinkPad X1':
  Price: 7
  Battery life: 8
  Performance: 7
```

**Score guidance:**

| Score | Meaning |
|-------|---------|
| 0–2 | Very poor / fails this criterion |
| 3–4 | Below average |
| 5 | Average / acceptable |
| 6–7 | Good |
| 8–9 | Very good |
| 10 | Perfect / best possible |

---

## Step 6 — Read the results

```
  RANKING
  Rank  Alternative     Price  Battery life  Performance   Score
  🥇    MacBook Air       6.0           9.0          8.0   77.2%
  🥈    ThinkPad X1       7.0           8.0          7.0   74.1%
  🥉    Dell XPS 13       8.0           7.0          7.0   73.4%

  ✔  Best choice: MacBook Air (77.2%)
```

Even though MacBook Air scored low on Price, its high Performance and Battery Life (both heavily weighted) pushed it to the top.

---

## Step 7 — Sensitivity analysis (optional)

This shows how the ranking **changes if you tweak one criterion's weight**. Useful for sanity-checking your decision.

```
Run sensitivity analysis? y
Criterion to vary: Price

  Weight   Rankings
     0.0   MacBook Air > ThinkPad X1 > Dell XPS 13
     2.5   MacBook Air > ThinkPad X1 > Dell XPS 13
     5.0   MacBook Air > Dell XPS 13 > ThinkPad X1
    10.0   Dell XPS 13 > ThinkPad X1 > MacBook Air
```

This tells you: *"MacBook Air wins unless you care a lot about price — then Dell XPS 13 takes over."* That's actionable insight.

---

## Step 8 — Save your session

```
Save to JSON? y
File path: laptop_decision.json
```

Reload it later with:
```bash
python mcdss.py --load laptop_decision.json
```

---

## Quick tips

- **Scores are relative** — you don't need to be precise, just consistent. If option A is clearly better than B on a criterion, its score should be noticeably higher.
- **Weights matter more than scores** — a criterion with weight 9 has almost double the impact of one with weight 5, so set weights thoughtfully.
- **Run sensitivity analysis** on any criterion you're unsure about to see if it would flip the winner.
