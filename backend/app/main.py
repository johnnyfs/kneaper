import asyncio
from dataclasses import dataclass
from typing import Any
from arcadepy import Client as ArcadeClient
from pydantic_ai import Agent, RunContext

dgraph_test = Agent(
    model="gpt-5-mini",
    instructions="""
    You are an assistant that helps users interact with a DGraph database.
    
    Run the necessary mutations and/or queries to fulfill the user's request,
    then respond with the relevant information.
"""
)

# TODO: This is good enough for a quick demo, but in the future we should expose
# the tools directly to the agent API, rather than requiring a round trip through
# the pydantic proxy for each invocation.

@dataclass
class DGraphAgentContext:
    client: ArcadeClient

@dgraph_test.tool
def mutate(context: RunContext[DGraphAgentContext], nquads: list[str] | None, json_data: dict | None, is_delete: bool = False) -> dict:
    """
    Mutate the graph by running the given NQuad mutations.

    Returns a dict of node labels -> assigned UIDs.
    """
    result = context.deps.client.tools.execute(tool_name="DGraph.mutate", input={"nquads": nquads, "json_data": json_data, "is_delete": is_delete})
    return result

@dgraph_test.tool
def query(context: RunContext[DGraphAgentContext], query: str) -> dict:
    """
    Query the graph using the given DQL query.

    Returns the query result as a dictionary.
    """
    result = context.deps.client.tools.execute(tool_name="DGraph.query", input={"query": query})
    return result

@dgraph_test.tool
def alter_schema(context: RunContext[DGraphAgentContext], schema_: str) -> dict:
    """
    Alter or extend the DGraph schema.
    """
    result = context.deps.client.tools.execute(tool_name="DGraph.AlterSchema", input={"schema_": schema_})
    return result

@dgraph_test.tool
def get_schema(context: RunContext[DGraphAgentContext]) -> dict:
    """
    Get the current DGraph schema.
    """
    result = context.deps.client.tools.execute(tool_name="DGraph.getschema_")
    return result

async def main():
    client = ArcadeClient()
    history = []

    while True:
        try:
            text = input("> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not text.strip():
            continue
        print("...")
        response = await dgraph_test.run(
            user_prompt=text,
            deps=DGraphAgentContext(client=client),
            message_history=history,
        )
        print("Assistant:", response.output)
        history.extend(response.all_messages())
    
if __name__ == "__main__":
    asyncio.run(main())