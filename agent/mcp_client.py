'''
client, qwen3:8b on ollama driving the nl2sql MCP tools, with the clarification loop in the terminal.
run the server first:  python agent/mcp_server.py --http
then:                  python agent/mcp_client.py
'''
import asyncio
import json

from llama_index.core.agent.workflow import FunctionAgent, ToolCall, ToolCallResult
from llama_index.core.workflow import Context
from llama_index.llms.ollama import Ollama
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

## the asking and answering rules come from prompt_clarifying_question.py and prompt_final_answer.py,
## which did those two jobs before the agent took them over. the example columns are payroll ones, like in
## those prompts, so the model can't copy a real column out of the example
SYSTEM_PROMPT = """You answer a business user's questions about their CPG sales data, using three tools.
Never state a result unless answer_question returned it in this conversation. If you haven't called it, you don't have an answer yet.

Tools:
- check_ambiguity: splits the question into phrases and matches each phrase to database columns. Every phrase comes back with a verdict, a pick and its candidate columns.
- answer_question: writes and runs the SQL. Takes the question and columns, which maps each phrase to the one column it means.
- describe_data: describes every table and column. Use it when the user asks what data there is, or when you need to know what a column means.

For every new question:
1. Call check_ambiguity once, with the user's question word for word. Don't repeat a check you have already run.
2. Go through the phrases by verdict:
   - clear: use its pick.
   - ambiguous or unrated: the user has to choose between its candidates, unless the conversation already settles it.
   - no_match: leave it out. If it is something the user actually asked about (like profit) rather than a filler word, tell them the data doesn't cover it and offer the closest candidates.
3. If the user has to choose anything, send ONE message that asks about all of it, then stop and wait for their reply. Do not call answer_question yet. When they reply, match their answer to one of the candidates you offered. If you still aren't sure which column a phrase means, for example because their reply adds something the question didn't have or doesn't clearly match a candidate, you may call check_ambiguity one more time on the question rewritten to include their answer. Keep every choice the user already made.
4. When every phrase that matters has a column, call answer_question once, with the question you last passed to check_ambiguity and columns, for example {"Which region": "dim_store.region", "the total payroll": "fact_payroll.salary_total"}. Use each phrase exactly as check_ambiguity returned it, and only a column from that phrase's own candidates.
5. If answer_question comes back with status "error", tell the user which stage failed. Do not answer from memory.

Asking the user to choose:
- Quote the user's own phrase so they know what you are asking about.
- Never show column names. Describe each option in plain business words.
- Offer only the listed candidates. Do not invent new ones.
- Phrases can overlap, like "the highest sales" and "sales". Ask about each meaning once, and apply the answer to every phrase it covers.
- One sentence per unclear phrase. Number them if there is more than one.
- Example: By "in Q1", do you mean calendar Q1 (January to March) or fiscal Q1?

Answering:
- Answer in one or two plain English sentences. If there are several rows, list them in order.
- Use only values that appear in the rows. You may format them (add $, commas, round money to cents), but never calculate, estimate or invent a number.
- If there are no rows, or only empty values, say that no data matched. Do not guess.
- Read the sql in the result to say which reading was used: calendar or fiscal, units or revenue.
- Calendar quarters cover months: Q1 January to March, Q2 April to June, Q3 July to September, Q4 October to December. Fiscal quarters and months do not line up with calendar months, so never give month ranges for them.
- Never show column names, table names or SQL. No greeting."""


## a tool's own result dict, out of whatever wrapper the MCP client hands back:
## structured content when the server sends it, else the JSON text block
def tool_result(tool_output):
    raw = tool_output.raw_output
    if isinstance(raw, dict):
        return raw
    if getattr(raw, "structuredContent", None):
        return raw.structuredContent
    for block in getattr(raw, "content", None) or []:
        try:
            return json.loads(block.text)
        except (AttributeError, ValueError):
            continue
    return {}


async def main():
    ## the 30s default is too short once SQL generation and BigQuery are both in a call
    client = BasicMCPClient("http://127.0.0.1:8000/mcp", timeout=300)
    tools = await McpToolSpec(client=client).to_tool_list_async()

    llm = Ollama(
        model="qwen3:8b",   ## qwen3:4b-instruct skipped answer_question and made up a result. llama3.1:8b wrote tool calls out as text
        request_timeout=360.0,
        context_window=16000,   ## left unset, the wrapper asks ollama for the model's full context window and eats memory
        temperature=0,
    )
    agent = FunctionAgent(tools=tools, llm=llm, system_prompt=SYSTEM_PROMPT)
    ctx = Context(agent)   ## same ctx every turn, so the answer to a clarifying question reaches the next run

    while True:
        question = input("\nyou> ").strip()
        if question.lower() in {"", "quit", "exit"}:
            break
        handler = agent.run(user_msg=question, ctx=ctx, max_iterations=10)
        called = []   ## tool names called this turn
        ## every tool call the agent makes, to catch it calling a tool more than once per question
        async for event in handler.stream_events():
            if isinstance(event, ToolCall):
                called.append(event.tool_name)
                print(f"[tool] {event.tool_name} {event.tool_kwargs}")
            elif isinstance(event, ToolCallResult) and event.tool_name == "answer_question":
                ## what the query was and what came back, to tell a wrong query from a misread result
                result = tool_result(event.tool_output)
                if not result:
                    print(f"[result] {event.tool_output.content}")
                print(f"[sql] {result.get('sql')}")
                print(f"[rows] {result.get('rows')}")
                if result.get("error"):
                    print(f"[error] {result['error']}")
        response = await handler
        print(f"\nagent> {response}")

        ## a reply that isn't a question, from a turn that never called answer_question, has no query behind it
        if not {"answer_question", "describe_data"} & set(called) and not str(response).rstrip().endswith("?"):
            print("(no query was run)")


if __name__ == "__main__":
    asyncio.run(main())