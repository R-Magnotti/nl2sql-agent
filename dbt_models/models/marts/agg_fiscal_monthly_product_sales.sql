SELECT ddate.fiscal_year AS fiscal_year, ddate.fiscal_month AS fiscal_month, fsales.product_key AS product_key, dprod.product_name as product_name, SUM(units_sold) AS total_units, SUM(sales_amount) AS total_revenue 
FROM {{ ref('fact_sales') }} fsales
JOIN {{ ref('dim_date') }} ddate ON fsales.date_key = ddate.date_key
JOIN {{ ref('dim_product') }} dprod ON fsales.product_key = dprod.product_key
GROUP BY ddate.fiscal_year, ddate.fiscal_month, fsales.product_key, dprod.product_name