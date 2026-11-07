import json
from pathlib import Path

## the warehouse description lives in its own file, so describe_data can hand the agent the same text the sql model gets.
## its path is in config.json (read here directly: importing agent_utils would connect to postgres just for this)
AGENT_DIR = Path(__file__).resolve().parent
with open(AGENT_DIR / "config.json") as f:
    warehouse = (AGENT_DIR.parent / json.load(f)["warehouse_doc"]).read_text()

## f-string: any { or } added to the examples has to be doubled
exemplars = f'''
You convert questions into BigQuery GoogleSQL. Answer with only the final single SQL query, no explanation, no markdown, no options, no quotes.

{warehouse}
Make absolutely sure that any columns used in the sql are listed above, and belong to the right table.

Examples:

Q: What was total revenue in March 2024?
A: SELECT SUM(total_revenue) FROM nl2sql_dev.agg_monthly_product_sales WHERE calendar_year = 2024 AND calendar_month = 3

Q: What was total fiscal revenue in fiscal March 2024?
A: SELECT SUM(total_revenue) FROM nl2sql_dev.agg_fiscal_monthly_product_sales WHERE fiscal_year = 2024 AND fiscal_month = 3

Q: How many units were sold in Q2 2025?
A: SELECT SUM(total_units) FROM nl2sql_dev.agg_monthly_product_sales WHERE calendar_year = 2025 AND calendar_month BETWEEN 4 AND 6

Q: What are the top 5 products by revenue in 2024?
A: SELECT product_name, SUM(total_revenue) AS revenue FROM nl2sql_dev.agg_monthly_product_sales WHERE calendar_year = 2024 GROUP BY product_name ORDER BY revenue DESC LIMIT 5

Q: What was total revenue by region in 2024?
A: SELECT r.region, SUM(f.sales_amount) AS revenue FROM nl2sql_dev.fact_sales f JOIN nl2sql_dev.dim_retailer r ON f.retailer_key = r.retailer_key JOIN nl2sql_dev.dim_date d ON f.date_key = d.date_key WHERE d.calendar_year = 2024 GROUP BY r.region

Q: How much promo revenue did BrightSmile Whitening Toothpaste 120g generate in 2024?
A: SELECT SUM(f.sales_amount) AS promo_revenue FROM nl2sql_dev.fact_sales f JOIN nl2sql_dev.dim_product p ON f.product_key = p.product_key JOIN nl2sql_dev.dim_date d ON f.date_key = d.date_key WHERE p.product_name = 'BrightSmile Whitening Toothpaste 120g' AND f.is_promo = TRUE AND d.calendar_year = 2024
'''
