import asyncio
from typing import Any
import pydgraph
import json


class DGraphClient:
    def __init__(
        self,
        addr: str = "localhost:9080",
        user: str | None = None,
        password: str | None = None,
        namespace: str | None = None,
    ):
        """Initialize the DGraph client.

        Args:
            addr (str): The address of the DGraph server. Defaults to "localhost:9080".
            user (str | None): The username for authentication. Defaults to None.
            password (str | None): The password for authentication. Defaults to None.
        """
        self._stub = pydgraph.DgraphClientStub(addr)
        self._client = pydgraph.DgraphClient(self._stub)
        if user and password:
            if namespace:
                self._client.login_into_namespace(user, password, namespace)
            else:
                self._client.login(user, password)

    async def __aenter__(self) -> 'DGraphClient':
        """Enter the context manager."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Close the DGraph client connection."""
        self._stub.close()


    def alter(self, schema: str) -> None:
        """Alter or extend the DGraph schema.

        Args:
            schema (str): The new schema to set.
        """
        op = pydgraph.Operation(schema=schema)
        self._client.alter(op)


    async def mutate(self, nquads: list[str] | None = None, json_data: dict | None = None, is_delete: bool = False) -> dict:
        """
        nquads: bytes containing RDF/N-Quads.

        delete: if True, perform a deletion mutation instead of an insertion.
        """
        txn = self._client.txn()
        try:
            nquads_str = "\n".join(nquads) if nquads else None
            res = await asyncio.to_thread(
                txn.mutate,
                set_nquads=nquads_str if not is_delete else None,
                del_nquads=nquads_str if is_delete else None,
                set_obj=json_data if not is_delete else None,
                del_obj=json_data if is_delete else None,
                commit_now=True
            )
            return dict(res.uids) if res.uids else {}
        finally:
            txn.discard()


    async def query(self, query: str) -> dict:
        """
        query: str containing a DQL query.
        """
        txn = self._client.txn(read_only=True)
        try:
            res = await asyncio.to_thread(txn.query, query)
            return json.loads(res.json) if res.json else {}
        finally:
            txn.discard()

    # schema handling
    async def set_schema(self, schema: str) -> None:
        op = pydgraph.Operation(schema=schema)
        await asyncio.to_thread(self._client.alter, op)


    async def get_schema(self) -> dict[str, Any]:
        """
        Query the current schema from Dgraph and return it as a dict.
        """
        query = """
        schema {
            predicate
            type
            index
            tokenizer
            reverse
            count
            upsert
        }
        """

        txn = self._client.txn(read_only=True)
        try:
            res = await asyncio.to_thread(txn.query, query)
            return json.loads(res.json) if res.json else {}
        finally:
            txn.discard()

    @classmethod
    def create(
            cls,
            addr: str = "localhost:9080",
            user: str | None = None,
            password: str | None = None,
            namespace: str | None = None,
    ) -> 'DGraphClient':
        return cls(addr=addr, user=user, password=password, namespace=namespace)