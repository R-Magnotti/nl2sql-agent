## plain string, NOT an f-string bcthe slots stay open until .format() fills them per question
t = '''
You map chunks of a database question to table columns.

You will get the full question, then numbered chunks. Each chunk shows its
text and its own candidate columns lettered A-C.

Rules:
- For each chunk, pick the single best candidate FROM THAT CHUNK'S OWN LIST,
  or X if none fit.
- X means: no listed candidate matches, or the chunk has no database content
  (question words, function words).
- Never use a letter from another chunk's list. Never write a column name.
- Some chunks are pieces of other chunks. Mapping several chunks to the same
  column is often correct; do not avoid repeats.
- Output exactly one line per chunk, in order, format: <number> -> <letter>
  Nothing else. No explanations.

Example
Question: Which department had the highest payroll in March overall?
Chunks:
1. "Which department"
   A. location
   B. dept_name
   C. dept_id
2. "the highest payroll"
   A. headcount
   B. bonus_amt
   C. salary_total
3. "in March"
   A. hire_date
   B. pay_month
   C. fiscal_qtr
4. "March"
   A. hire_date
   B. pay_month
   C. fiscal_qtr
5. "overall"
   A. region
   B. store_id
   C. channel

Output:
1 -> B
2 -> C
3 -> B
4 -> B
5 -> X

Question: {question}
Chunks:
{chunks}

Output:
'''

## add /no_think before output when using qwen models