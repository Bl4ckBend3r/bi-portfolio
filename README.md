# BI Portfolio

Two small, reproducible business intelligence projects with synthetic data. Each has a runnable local workflow, documented model and concrete validation. No cloud credentials or paid services are needed.

| Project | Run | Result |
| --- | --- | --- |
| [Retail Sales BI Dashboard](projects/retail-bi-dashboard/) | `python projects/retail-bi-dashboard/build_report.py` | SQLite star schema plus self-contained interactive `output/dashboard.html` |
| [Incremental ETL & Data Warehouse](projects/etl-data-warehouse/) | `python projects/etl-data-warehouse/etl_pipeline.py` | Incremental SQLite warehouse with SCD Type 2, watermarks, audit and quality logs |

Download and open the [interactive retail demo](projects/retail-bi-dashboard/dashboard_demo.html) to explore the report immediately.

Use Python 3.10+; no third-party Python packages are required. Run `python -m unittest discover -s projects/retail-bi-dashboard` and `python -m unittest discover -s projects/etl-data-warehouse` to verify the workflows.

**Scope:** The retail report is plain HTML/JavaScript, not a Power BI `.pbix` file. DAX measures and SQL Server schemas are supplied as implementation references. Azure Data Factory is an architecture blueprint, not a deployed service.
