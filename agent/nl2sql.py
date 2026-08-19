import os
from openai import OpenAI

url = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1")
model = os.getenv("LLM_MODEL", "llama3.1:8b")
api_key = os.getenv("LLM_API_KEY", "ollama")    ## ollama api key for local use

SCHEMA_PROMPT = f'''
You convert questions into BigQuery GoogleSQL. Answer with only the final single SQL query, no explanation, no markdown, no options, no quotes.

Dataset: nl2sql_dev. Qualify all tables as nl2sql_dev.<table>.

Tables:

fact_sales (one row = one product at one retailer for one week):
- date_key (INT64) - week identifier like 20240415. NOT a date type. Join to dim_date for any calendar or fiscal fields.
- product_key (INT64) - join to dim_product
- retailer_key (INT64) - join to dim_retailer
- units_sold (INT64)
- sales_amount (FLOAT64) - revenue in dollars
- is_promo (INT64) - 1 if promotional sale, 0 otherwise

dim_date (WEEKLY grain: one row per week, 104 rows total):
- date_key (INT64) - week start date as integer, joins to fact_sales
- week_start_date (DATE), week_end_date (DATE)
- calendar_year (INT64), calendar_quarter (INT64), calendar_month (INT64), calendar_month_name (STRING)
- fiscal_year (INT64), fiscal_quarter (INT64), fiscal_month (INT64), fiscal_month_name (STRING)
- iso_week (INT64)
Note: calendar and fiscal months differ (4-4-5 fiscal calendar). If a question says "month" without specifying, calendar and fiscal give different answers.

dim_product (one row per product, 61 rows):
- product_key (INT64), sku (STRING), product_name (STRING), brand (STRING), category (STRING), subcategory (STRING), list_price (FLOAT64)

dim_retailer (one row per retailer, 15 rows):
- retailer_key (INT64), retailer_code (STRING), retailer_name (STRING), channel (STRING), region (STRING), country (STRING)

agg_monthly_product_sales (pre-aggregated: one row = one product per calendar month):
- calendar_year (INT64), calendar_month (INT64), product_key (INT64), product_name (STRING), total_units (INT64), total_revenue (FLOAT64)

agg_fiscal_monthly_product_sales (pre-aggregated: one row = one product per fiscal month):
- fiscal_year (INT64), fiscal_month (INT64), product_key (INT64), product_name (STRING), total_units (INT64), total_revenue (FLOAT64)

Prefer the agg_ tables for monthly revenue/units questions; they need no joins. Use fact_sales joined to dims for weekly, retailer-level, or promo questions.

Data covers calendar years 2024-2025.
'''

def load_client(url=url, api_key=api_key):
    return OpenAI(base_url=url, api_key=api_key)


def get_response(client, model=model, question="What color is the sky?"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SCHEMA_PROMPT},
            {"role": "user", "content": question},
        ],
        temperature=0
    )
    return response.choices[0].message.content