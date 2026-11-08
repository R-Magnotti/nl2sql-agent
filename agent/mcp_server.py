'''
the MCP server: exposes the three tools in RAG_agent.py to an agent.
the tools stay plain python in RAG_agent.py, so the notebook and the console driver use them without MCP.
the wrappers here add what MCP needs: typed parameters, and the descriptions the agent reads to decide what to call.
'''
import contextlib
import sys

from mcp.server.mcpserver import MCPServer
from pydantic import Field

import RAG_agent   ## loads the models and connects to postgres once, at server start


## initialize the MCP server, give it a name and log level
mcp = MCPServer("nl2sqlMCP", log_level="ERROR")

@mcp.tool(
    name="check_ambiguity",
    description="Match each phrase of the user's question to warehouse columns and judge how sure each match is. Call this first. "
                "Every phrase comes back with a verdict: clear, ambiguous (ask the user which candidate they mean), "
                "no_match (nothing in the warehouse answers it) or unrated (the critic skipped it, treat it like ambiguous), "
                "plus its candidate columns with cosine scores and critic probabilities. It never asks the user anything."
)
def check_ambiguity(question: str = Field(description="The user's question, as they asked it")) -> dict:
    return RAG_agent.check_ambiguity(question)


@mcp.tool(
    name="answer_question",
    description="Write the SQL for the question from your phrase-to-column picks, check it, and run it on BigQuery. "
                "columns holds the clear picks from check_ambiguity plus the user's answers for ambiguous phrases. Leave out no_match phrases. "
                "Returns status (answered or error), the sql, columns_used, column_fixes, rows, and an error naming the stage that failed."
)
def answer_question(
    question: str = Field(description="The user's question, as passed to check_ambiguity"),
    columns: dict[str, str] = Field(description='Each phrase mapped to the column it means, e.g. {"Which quarter": "dim_date.fiscal_quarter"}'),
) -> dict:
    return RAG_agent.answer_question(question, columns)


@mcp.tool(
    name="describe_data",
    description="Every table and column the SQL can use, with types, grain and notes such as calendar vs 4-4-5 fiscal months. "
                "Use it to answer what data exists, or to explain the candidates when you ask the user to clarify."
)
def describe_data() -> str:
    return RAG_agent.describe_data()


if __name__ == "__main__":
    ## stdio for Claude clients, which hold one connection open.
    ## http for the LlamaIndex client, which starts a new stdio process per call
    if "--http" in sys.argv:
        mcp.run(transport="streamable-http")   ## http://127.0.0.1:8000/mcp
    else:
        mcp.run(transport="stdio")
