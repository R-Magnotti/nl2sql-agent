select
    product_key,
    sku,
    product_name,
    brand,
    category,
    subcategory,
    list_price
from {{ ref('stg_product') }}
