# Seed Data

Synthetic CPG point-of-sale data for the NL2SQL agent project. Four CSVs forming a star schema. One fact table (events) and three dimensions (context of those events).

All data is synthetic. Brands, retailers, and numbers are invented.

## schema at a glance

```
               dim_date (104 rows)
                     |
                  date_key
                     |
dim_product ---- fact_sales ---- dim_retailer
 (61 rows)      (66,234 rows)      (15 rows)
product_key                      retailer_key
```

Grain of `fact_sales`: one row per product per retailer per week.

## fact_sales.csv

66,234 rows. Sales measurements. Sparse on purpose: about 10% of product-retailer pairs are never carried, and weekly presence varies. A missing product-week is an absent row, not a zero. Queries that need zeros must generate them.

| column | type | notes |
|---|---|---|
| date_key | int | FK to dim_date, format YYYYMMDD of week start |
| product_key | int | FK to dim_product |
| retailer_key | int | FK to dim_retailer |
| units_sold | int | units sold that week |
| sales_amount | decimal | gross revenue in USD; **contains nulls** (see Known mess) |
| promo_flag | int (0/1) | 1 = promotional week (higher units, ~20% price discount) |

Baked-in patterns: 
- seasonality with a Q4 holiday ramp, 
- a summer bump for Personal Care, 
- mild growth across the two years, 
- promo lift
Enough signal for window-function and trend queries to return non-boring answers.

## dim_date.csv

104 rows, one per week, Mondays from 2024-01-01 through week starting 2025-12-22. Two full years, so year-over-year and month-over-month comparisons are possible.

Carries **two calendars** and they disagree:

- **Calendar**: normal months. A week belongs to the month of its start date.
- **Fiscal**: a 4-4-5 calendar, standard in CPG. Each quarter is 13 weeks split into   fiscal months of 4, 4, and 5 weeks. Fiscal months are built from whole weeks, so   they drift off the normal months.

Worked example: 
fiscal February FY2024 covers the four weeks starting Jan 29 through Feb 19. Calendar February 2024 covers the four weeks starting Feb 5 through Feb 26. Total revenue for "February 2024" is $643,735.40 on the calendar definition and $637,895.06 on the fiscal definition. Same question, two defensible answers. This is the ambiguity the agent's clarifying-question layer exists to catch.

| column | type | notes |
|---|---|---|
| date_key | int | PK, YYYYMMDD of week start |
| week_start_date | date | Monday |
| week_end_date | date | Sunday |
| calendar_year | int | year of week start |
| calendar_quarter | int | 1-4 |
| calendar_month | int | 1-12, month of week start |
| calendar_month_name | text | January..December |
| fiscal_year | int | FY2024 = weeks 1-52, FY2025 = weeks 53-104 |
| fiscal_quarter | int | 1-4, thirteen weeks each |
| fiscal_month | int | 1-12 on the 4-4-5 pattern |
| fiscal_month_name | text | January..December (fiscal) |
| iso_week | int | ISO week number of week start |

## dim_product.csv

61 rows. Product catalog across 4 categories (Oral Care, Personal Care, Home Care, Pet Nutrition), 12 subcategories, 7 invented brands.

| column | type | notes |
|---|---|---|
| product_key | int | PK |
| sku | text | e.g. OC-1001; prefix encodes category |
| product_name | text | brand + variant + size |
| brand | text | BrightSmile, FreshDent, PureGlow, SilkTouch, HomeShine, SparkleWave, VitaPaw |
| category | text | 4 values |
| subcategory | text | 12 values |
| list_price | decimal | non-promo shelf price, USD |

## dim_retailer.csv

15 rows. Retail accounts across 5 channels and 5 regions. The region column is what makes user-role scoping meaningful: "show me my sales" from a Latin America rep and a North America rep must resolve to different rows.

| column | type | notes |
|---|---|---|
| retailer_key | int | PK |
| retailer_code | text | R101-R115 |
| retailer_name | text | invented |
| channel | text | Mass, Grocery, Club, Drug, eCommerce |
| region | text | North America, Latin America, Europe, Asia-Pacific, Africa-Eurasia |
| country | text | one per retailer |

## Known mess (deliberate)

The raw fact file ships dirty. Staging models are expected to handle every item below, and the dbt tests are expected to catch them if staging does not. Counts are exact and reproducible (fixed seed).

| defect | count | what should catch it |
|---|---|---|
| exact duplicate rows | 300 | dedup in staging; uniqueness test on the staged grain |
| null sales_amount | 250 | not-null test / explicit null-handling rule in staging |
| impossible date_keys (20240230, 20251133) | 2 | relationship test to dim_date |
| orphan product_keys (997, 998, 999) | 30 | relationship test to dim_product |

Dimensions are clean. All mess lives in the fact.