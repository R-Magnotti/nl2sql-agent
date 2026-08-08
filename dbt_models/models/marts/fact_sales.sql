with deduped as (
    select distinct
        date_key,
        product_key,
        retailer_key,
        units_sold,
        sales_amount,
        is_promo
    from {{ ref('stg_sales') }}
)

select
    d.date_key,
    d.product_key,
    d.retailer_key,
    d.units_sold,
    d.sales_amount,
    d.is_promo
from deduped as d
inner join {{ ref('dim_date') }} as dd on d.date_key = dd.date_key
inner join {{ ref('dim_product') }} as dp on d.product_key = dp.product_key
inner join {{ ref('dim_retailer') }} as dr on d.retailer_key = dr.retailer_key
