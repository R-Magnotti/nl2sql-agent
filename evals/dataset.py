'''
the gold set: the columns on offer, how a column is rendered to a model, and the
41 probes with the verdict a human says each one deserves.

pure data, no model imports -- so a case can be added or a label argued with
without loading 11GB of weights to read the file.
'''

COLUMNS = {
        "fiscal_year": "A fiscal year (also known as a financial year, or sometimes budget year) is a one-year time interval whose beginning and end may be shifted with respect to the calendar year (1 January to 31 December)",
        "fiscal_month": "Any fiscal month of any Fiscal Year, which month shall generally end on the Saturday closest to the last day of each calendar month in accordance with the fiscal accounting calendar",
        "calendar_year": "A period of a year beginning and ending with the dates that are conventionally accepted as marking the beginning and end of a numbered year",
        "calendar_month": "one of the months as named in the calendar",
        "product_key": "surrogate key identifying a product, joins fact_sales to dim_product",
        "product_name": "the full display name of a product, including brand, variant, and size",
        "total_units": "total number of units sold, summed",
        "total_revenue": "total sales revenue in dollars, summed"
}

## the second variant carries the name AS WELL AS the description: the judge is
## asked to name the column it picks, which it cannot do if it was only ever
## shown prose. so this asks "does the description help the name" rather than
## "does the description work instead of the name"
VARIANTS = {"name_only": "{name}", "name_and_desc": "{name}: {desc}"}

## (probe, expected_top, expected_other, gold_verdict)
CASES = [
    ## --- time, bare terms: the core ambiguity ---
    ("year",                 "calendar_year",  "fiscal_year",    "ambiguous"),
    ("month",                "calendar_month", "fiscal_month",   "ambiguous"),
    ("february",             "calendar_month", "fiscal_month",   "ambiguous"),
    ("april",                "calendar_month", "fiscal_month",   "ambiguous"),
    ("october",              "calendar_month", "fiscal_month",   "ambiguous"),
    ("october 2024",         "calendar_month", "fiscal_month",   "ambiguous"),

    ## --- time, qualified: the qualifier should win decisively ---
    ("fiscal year",          "fiscal_year",    "calendar_year",  "clear"),
    ("fiscal month",         "fiscal_month",   "calendar_month", "clear"),
    ("fiscal february",      "fiscal_month",   "calendar_month", "clear"),
    ("fiscal april",         "fiscal_month",   "calendar_month", "clear"),
    ("fiscal october",       "fiscal_month",   "calendar_month", "clear"),
    ("fiscal october 2024",  "fiscal_month",   "calendar_month", "clear"),
    ("calendar february",    "calendar_month", "fiscal_month",   "clear"),
    ("FY2024",               "fiscal_year",    "calendar_year",  "clear"),
    ("fiscal 2024",          "fiscal_year",    "calendar_year",  "clear"),
    ("calendar 2024",        "calendar_year",  "fiscal_year",    "clear"),

    ## --- qualified with no shared token: tests semantics vs string overlap ---
    ("accounting february",  "fiscal_month",   "calendar_month", "clear"),
    ("4-4-5 february",       "fiscal_month",   "calendar_month", "clear"),

    ## --- natural phrasing: do extra tokens wreck the signal ---
    ("in february",          "calendar_month", "fiscal_month",   "ambiguous"),
    ("the month of february","calendar_month", "fiscal_month",   "ambiguous"),
    ("last month",           "calendar_month", "fiscal_month",   "ambiguous"),

    ## --- clear measures: these set the floor. if these score low,
    ##     any floor that catches profit also blocks normal questions ---
    ("revenue",              "total_revenue",  "total_units",    "clear"),
    ("total sales",          "total_revenue",  "total_units",    "clear"),
    ("dollars",              "total_revenue",  "total_units",    "clear"),
    ("units",                "total_units",    "total_revenue",  "clear"),
    ("units sold",           "total_units",    "total_revenue",  "clear"),
    ("how many units",       "total_units",    "total_revenue",  "clear"),

    ## --- clear dimensions ---
    ("product",              "product_name",   "product_key",    "clear"),
    ("product name",         "product_name",   "product_key",    "clear"),
    ("item",                 "product_name",   "product_key",    "clear"),

    ## --- second ambiguity axis: measure, not time ---
    ("sales",                "total_revenue",  "total_units",    "ambiguous"),
    ("performance",          "total_revenue",  "total_units",    "ambiguous"),
    ("how did it do",        "total_revenue",  "total_units",    "ambiguous"),

    ## --- refuse: nothing in the schema answers these.
    ##     watch top_score, not the gap ---
    ("profit",               "total_revenue",  "total_units",    "refuse"),
    ("margin",               "total_revenue",  "total_units",    "refuse"),
    ("gross margin",         "total_revenue",  "total_units",    "refuse"),
    ("cost",                 "total_revenue",  "total_units",    "refuse"),
    ("cogs",                 "total_revenue",  "total_units",    "refuse"),
    ("discount",             "total_revenue",  "total_units",    "refuse"),
    ("inventory",            "total_units",    "total_revenue",  "refuse"),
    ("customer count",       "total_units",    "total_revenue",  "refuse"),
]

VERDICTS = ("clear", "ambiguous", "refuse")


def probes():
    '''the probe strings, in case order'''
    return [case[0] for case in CASES]


def cases(verdict=None):
    '''the CASES rows carrying one gold verdict, or every row when asked for none'''
    return [c for c in CASES if verdict is None or c[3] == verdict]


def render(column, variant):
    '''one column as the given variant shows it to a model'''
    return VARIANTS[variant].format(name=column, desc=COLUMNS[column])
