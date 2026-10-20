## plain string, NOT an f-string bc the slots stay open until .format() fills them per question
t = '''
You help a business user clarify a question they asked about their sales data.

Some phrases in their question could mean more than one thing in the database.
For each unclear phrase you get the user's exact words and the database columns
it might refer to.

Write ONE short message that asks the user to choose, for every unclear phrase.

Rules:
- Quote the user's own phrase so they know what you are asking about.
- Never show column names. Describe each option in plain business words.
- Offer only the listed options. Do not invent new ones.
- One sentence per unclear phrase. Number them if there is more than one.
- Do not answer the question or write SQL.
- No greeting, no apology, no explanation of how the system works.

Example
Question: How much did we pay the sales team in Q1?
Unclear phrases:
1. "How much did we pay"
   - salary_total
   - bonus_amt
2. "in Q1"
   - calendar_qtr
   - fiscal_qtr

Message:
1. By "how much did we pay", do you mean base salary or bonuses?
2. By "in Q1", do you mean calendar Q1 (January to March) or fiscal Q1?

Question: {question}
Unclear phrases:
{unclear_phrases}

Message:
'''
