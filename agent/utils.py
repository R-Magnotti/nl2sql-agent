import re

## this will add DATABASE. prefix to all FROM clauses
# TODO: fails for CTEs, maybe better to use sqglot in future ...
def add_table_prefix(query: str, prefix: str = "nl2sql_dev") -> str:
    pattern = re.compile(
        r'\b(FROM|JOIN)(\s+)'   # the keyword + whitespace
        r'(?!\()'               # skip subqueries: FROM (SELECT ...)
        r'([A-Za-z_]\w*)'       # a bare table name
        r'(?![\w.])',           # not already schema-qualified
        flags=re.IGNORECASE,
    )
    return pattern.sub(rf'\1\2{prefix}.\3', query)


def clean_SQL_query_driver(query: str):
    ## fix FROM clause prefixes
    return add_table_prefix(query)
    
    