with deduped as (
    select
        date_key,
        product_key,
        retailer_key,
        units_sold,
        sales_amount,
        is_promo
    from {{ ref('stg_sales') }}
    qualify row_number() over (
        partition by date_key, product_key, retailer_key
        order by sales_amount is null, units_sold is null
    ) = 1
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
