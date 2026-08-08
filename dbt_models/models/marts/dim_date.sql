select
    date_key,
    week_start_date,
    week_end_date,
    calendar_year,
    calendar_quarter,
    calendar_month,
    calendar_month_name,
    fiscal_year,
    fiscal_quarter,
    fiscal_month,
    fiscal_month_name,
    iso_week
from {{ ref('stg_date') }}
