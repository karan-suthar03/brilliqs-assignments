# Assignment 2 - Advanced SQL Transformations

Three queries over a denormalised sales table. Plain SELECTs - no stored
procedures, no cursors, no loops.

Written for PostgreSQL.

## Files

```
01_schema.sql    the two tables
02_seed.sql      5000 sales rows and 358 monthly targets, generated in SQL
03_queries.sql   the three queries
```

## Running

```
createdb assignment2
psql -d assignment2 -f 01_schema.sql
psql -d assignment2 -f 02_seed.sql
psql -d assignment2 -f 03_queries.sql
```

The seed starts with `setseed`, so the data is identical every run, and with
`TRUNCATE`, so it can be re-run without recreating the database.

## The two tables

`sales` is one row per order line, and deliberately denormalised - the
customer, product and rep details repeat on every row, the way a flat export
from a reporting system does.

`monthly_targets` is one row per region, category and month. That coarser
grain is the mismatch the third query has to bridge.

## The queries

**Q1 - moving average.** Monthly revenue per category, with the previous
month from `LAG` and a 3 month average. Both use one named window; the
average adds a frame to it.

**Q2 - top 3 per category.** `ROW_NUMBER` inside a CTE, filtered outside it,
because a window function cannot be used in `WHERE` - it is computed after
`WHERE` has already run.

**Q3 - sales against targets.** The sales are rolled up to the target's grain
before joining, otherwise each target would be multiplied by the number of
order lines that month. The join is `FULL OUTER` so that both gaps show up:
28 months have sales with no target, and 2 have a target with no sales. An
inner join would drop all 30 and look perfectly healthy doing it.
