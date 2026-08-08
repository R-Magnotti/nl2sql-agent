select
    retailer_key,
    retailer_code,
    retailer_name,
    channel,
    region,
    country
from {{ ref('stg_retailer') }}
