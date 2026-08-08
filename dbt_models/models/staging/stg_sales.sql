select
    date_key,
    product_key,
    retailer_key,
    units_sold,
    sales_amount,
    promo_flag = 1 as is_promo
from {{ source('raw_loaded_csv', 'fact_sales_raw') }}
