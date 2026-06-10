# Book Sales Analytics

*A data-engineering exercise, cleaned up and documented as a portfolio piece.*

A pipeline that ingests messy book-sales data from three different file formats,
cleans and reconciles it, computes sales analytics, and renders a self-contained
BI-style dashboard.

**[View the live dashboard →](https://amelylina.github.io/books-sales-analytics/)**

## What it does

The pipeline runs over three independent datasets (`DATA1`, `DATA2`, `DATA3`),
each split across three formats:

| File             | Format  | Contents                          |
|------------------|---------|-----------------------------------|
| `users.csv`      | CSV     | Customer records                  |
| `orders.parquet` | Parquet | Order line items                  |
| `books.yaml`     | YAML    | Book catalog with author lists    |

For each dataset it:

1. **Loads & cleans** - parses mixed-currency prices (EUR converted to USD at
   €1 = $1.20), normalizes inconsistent timestamps, and strips phone formatting.
2. **Reconciles user identities** - the same person may appear under multiple
   IDs with one changed field (new address, new phone, an alias instead of a
   real name). These are merged into single logical users.
3. **Computes analytics** - daily revenue and top revenue days, count of truly
   unique users, count of unique author sets, the best-selling author/author
   set, and the top customer by total spend (with all their alias IDs).
4. **Builds a dashboard** - a tabbed HTML page (one tab per dataset) with KPI
   cards, a top-days table, and a daily-revenue chart.

## Identity reconciliation

Users are deduplicated with a **Union-Find** structure. The task assumes a
duplicate record differs from the original in *at most one* identifying field,
so two records are treated as the same person when **at least 3 of the 4 fields**
(`name`, `address`, `phone`, `email`) match. Each connected group collapses to
one logical user, and the group's member IDs are preserved as that user's
aliases.

## Running

```bash
pip install -r requirements.txt
python main.py
```

The dashboard is written to `docs/index.html`. That file is committed so it can
be served via GitHub Pages - it's a generated artifact, not hand-written.

Data is expected at `data/DATA1/`, `data/DATA2/`, `data/DATA3/`, each containing
`users.csv`, `orders.parquet`, and `books.yaml`.

## Project structure

```
book-sales-analytics/
├── README.md
├── requirements.txt
├── main.py                 # orchestrator: load → aggregate → dashboard
├── data/
│   ├── DATA1/  ({users.csv, orders.parquet, books.yaml})
│   ├── DATA2/
│   └── DATA3/
├── src/
│   ├── load.py             # multi-format ingestion + cleaning + reconciliation
│   ├── aggregate.py        # analytics
│   ├── unionfind.py        # identity-reconciliation data structure
│   └── dashboard.py        # HTML dashboard generation
└── docs/
    └── index.html          # generated dashboard (served by GitHub Pages)
```

## Implementation notes

- **Price parsing.** I checked which characters actually appear in the price
  fields before writing the parser. Since no prices contain thousands separators
  (`,`), the parser extracts digit groups and joins them around the decimal
  point - simpler and more robust here than maintaining a regex per price
  variant. (This shortcut would need revisiting for data containing commas.)
- **Timestamps.** The raw timestamps are inconsistent, so a plain
  `pd.to_datetime` wouldn't work without first mapping every format. I normalize
  a few known quirks (e.g. `A.M.`/`P.M.`) and let `dateutil` handle the rest.
- **Missing values.** Only non-essential columns (e.g. `shipment` in orders)
  contain nulls. `address` has some nulls too, but I deliberately leave them
  unfilled - imputing them could corrupt the user-reconciliation grouping. The
  reconciliation still works, since matches are checked across multiple field
  combinations.
