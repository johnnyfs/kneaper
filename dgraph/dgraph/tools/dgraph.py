from typing import Annotated, Any

from arcade_tdk import tool, ToolContext

from dgraph.client.dgraph_client import DGraphClient

# TODO: Pass namespace in as a secret -- it's meant to be affined to a role.

@tool(requires_secrets=["DGRAPH_ADDR", "DGRAPH_USERNAME", "DGRAPH_PASSWORD"])
async def mutate(
    context: ToolContext,
    nquads: Annotated[list[str] | None, "List of NQuad mutations to execute."] = None,
    json_data: Annotated[dict | None, "Json mutations."] = None,
    is_delete: Annotated[bool, "If true, perform deletions instead of insertions."] = False,
    namespace: Annotated[str | None, "Optional namespace for the mutation."] = None,
) -> dict[str, str]:
    """
    Execute a list of NQuad mutations.

    Returns a dict of node labels -> assigned UIDs.
    """
    async with DGraphClient.create(
        addr=context.get_secret("DGRAPH_ADDR"),
        user=context.get_secret("DGRAPH_USERNAME"),
        password=context.get_secret("DGRAPH_PASSWORD"),
        namespace=namespace,
    ) as client:
        uids = await client.mutate(nquads=nquads, json_data=json_data, is_delete=is_delete)
        return uids

@tool(requires_secrets=["DGRAPH_ADDR", "DGRAPH_USERNAME", "DGRAPH_PASSWORD"])
async def query(
    context: ToolContext,
    query: Annotated[str, "DQL query string to execute."],
    namespace: Annotated[str | None, "Optional namespace for the query."] = None,
) -> dict:
    """
    Execute a DQL query.

    Returns the query result as a dictionary.
    """
    async with DGraphClient.create(
        addr=context.get_secret("DGRAPH_ADDR"),
        user=context.get_secret("DGRAPH_USERNAME"),
        password=context.get_secret("DGRAPH_PASSWORD"),
        namespace=namespace,
    ) as client:
        result = await client.query(query)
        return result
    
@tool(requires_secrets=["DGRAPH_ADDR", "DGRAPH_USERNAME", "DGRAPH_PASSWORD"])
async def alter_schema(
    context: ToolContext,
    schema_: Annotated[str, "The new schema to set."],
    namespace: Annotated[str | None, "Optional namespace for the schema."] = None,
) -> dict:
    """
    Alter or extend the DGraph schema.
    """
    async with DGraphClient.create(
        addr=context.get_secret("DGRAPH_ADDR"),
        user=context.get_secret("DGRAPH_USERNAME"),
        password=context.get_secret("DGRAPH_PASSWORD"),
        namespace=namespace,
    ) as client:
        await client.set_schema(schema_)
    return {} # None breaks stuff?

@tool(requires_secrets=["DGRAPH_ADDR", "DGRAPH_USERNAME", "DGRAPH_PASSWORD"])
async def get_Schema_(
    context: ToolContext,
    namespace: Annotated[str | None, "Optional namespace for the schema."] = None,
) -> dict[str, Any]:
    """
    Retrieve the current DGraph schema.
    """
    async with DGraphClient.create(
        addr=context.get_secret("DGRAPH_ADDR"),
        user=context.get_secret("DGRAPH_USERNAME"),
        password=context.get_secret("DGRAPH_PASSWORD"),
        namespace=namespace,
    ) as client:
        schema = await client.get_schema()
        return schema