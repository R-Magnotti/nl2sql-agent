select
    product_key,
    sku,
    product_name,
    brand,
    category,
    subcategory,
    list_price
from {{ source('raw_loaded_csv', 'dim_product_raw') }}