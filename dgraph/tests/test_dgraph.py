from arcade_tdk import ToolContext, ToolSecretItem
import pytest

from dgraph.tools.dgraph import mutate, query, alter_schema, get_schema

# TODO: Give each test an isolated DGraph instance or namespace.

@pytest.fixture()
def mock_tool_context() -> ToolContext:
    context = ToolContext()
    context.secrets = [
        ToolSecretItem(key="DGRAPH_ADDR", value="localhost:9080"),
        ToolSecretItem(key="DGRAPH_USERNAME", value="groot"),
        ToolSecretItem(key="DGRAPH_PASSWORD", value="password"),
    ]
    return context

@pytest.mark.asyncio
async def test_mutate_and_query_and_delete(mock_tool_context: ToolContext) -> None:
    uids = await mutate(
        mock_tool_context,
        nquads=[
            "_:this <is_a> \"test\" .",
        ]
    )
    assert type(uids) is dict
    assert "this" in uids

    this_uid = uids["this"]

    assert this_uid.startswith("0x")

    result = await query(
        mock_tool_context,
        f"""
        {{
            node(func: uid({this_uid})) {{
                uid is_a
            }}
        }}
        """
    )
    assert type(result) is dict
    assert "node" in result
    assert len(result["node"]) == 1
    assert result["node"][0]["uid"] == this_uid
    assert result["node"][0]["is_a"] == "test"

    uids = await mutate(
        mock_tool_context,
        json_data={"uid": this_uid, "is_a": None},
        is_delete=True,
    )

    assert type(uids) is dict
    assert len(uids) == 0

    result = await query(
        mock_tool_context,
        f"""
        {{
            node(func: uid({this_uid})) {{
                is_a
            }}
        }}
        """
    )
    assert type(result) is dict
    assert "node" in result
    assert len(result["node"]) == 0

@pytest.mark.asyncio
async def test_alter_and_get_schema(mock_tool_context: ToolContext) -> None:
    await alter_schema(
        mock_tool_context,
        schema_="""
        xid: string @index(term) .
        """,
    )

    schema = await get_schema(
        mock_tool_context,
    )
    assert type(schema) is dict
    assert "schema" in schema
    assert type(schema["schema"]) is list
    assert any(pred["predicate"].endswith(".xid") for pred in schema["schema"])