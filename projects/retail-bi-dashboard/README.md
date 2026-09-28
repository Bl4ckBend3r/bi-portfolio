# Retail Sales BI Dashboard

Synthetic retail analytics from CSV to a queryable star schema and interactive report. No Power BI license or SQL Server instance is required to run the demo.

## Reproduce

From the repository root, run:

```bash
python projects/retail-bi-dashboard/build_report.py
python -m unittest discover -s projects/retail-bi-dashboard
```

Open `projects/retail-bi-dashboard/output/dashboard.html` in a browser. A [ready-made demo report](dashboard_demo.html) is also included; download that HTML file and open it locally to explore without running Python. The page is self-contained and works offline. Choose year, store and category; KPI cards, monthly trend, category bars and store table update together. The script recreates all CSV files and `output/retail.db` deterministically with seed 42. Generated data and database are ignored by Git.

## What is measured

- 12,000 orders and 19,359 sales lines from January 2024 to August 2026.
- Revenue after discounts, gross margin (revenue minus cost), gross margin percentage and average order value (revenue / distinct orders).
- Dimensions: date, product and store. Fact grain: **one row per order line**. Orders are counted distinctly after filtering, so a multi-line order is not counted several times.
- Money is generated with `Decimal`, stored in SQLite as integer cents and reconciled against source CSV. Foreign keys are checked.

| File | Purpose |
| --- | --- |
| `generate_data.py` | Reproducible source CSV generator |
| `build_report.py` | SQLite load, reconciliation and report creation |
| `dashboard_template.html` | Offline HTML dashboard with interactive filters |
| `schema.sql` | SQL Server target schema (reference DDL; no SQL Server import is automated) |
| `dax_measures.md` | Suggested Power BI measures for a future `.pbix` build |

**Scope:** The working dashboard is HTML/JavaScript backed by generated SQLite data. The repo does not contain a `.pbix` Power BI report. For Power BI, import the dimension and fact tables, mark `DimDate` as a date table, connect each dimension 1:* to FactSales and add the documented DAX measures.
