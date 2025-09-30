# kneaper knowledge graph manager

A simple cl agent repl that manages graphs in a dgraph instance.

## Set up dgraph

From project root, to start the db

```
docker-compose up
```

Create a tcp tunnel to the database.

```
ngrok tcp 9080
```

Note: This requires a paid ngrok account.

You will see an ngrok url like `tcp://8.tcp.ngrok.io:14163` Save everything after the `tcp://`.

## Set up the tools

```
cd dgraph
uv venv --seed -p 3.13 ~/.arcade-dgraph
source ~/.arcade-dgraph/bin/activate
make install
make test
uv run arcade login
uv run arcade deploy -d ../worker.toml
```

Note: do not put the venv in the project's local directory or it will break tool deployment.

Note: I was unable to get `arcade evals --cloud` to recognize the tools. Same issue as with `chat` (see below).

## Set up secrets

Visit the Arcade dev [secrets manager](https://api.arcade.dev/dashboard/auth/secrets) and set up the following

```
DGRAPH_ADDR {NGROK_URL_NOT_INCLUDING_THE_PROTOCOL}
DGRAPH_USERNAME groot
DGRAPH_PASSWORD password
```

Note: namespace support has not yet been tested.

## Run the repl

I was unable to get the built-in Arcade chat testing to recognize my tools. (They were visible with /show but the model claimed they did not exist. Same behavior in the webapp.) So instead here's an incredibly bare-bones repl:

Set the following env variables to your personal keys:
```
export ARCADE_API_KEY={YOUR_KEY}
export OPENAI_API_KEY={YOUR_KEY}
```

From the project root:

```
cd backend
poetry env use 3.13.7
poetry install
poetry run pytest tests
poetry run python app/main.py
```

## Example interaction

**Create several nodes of type Person, each with a unique name. make some hooligans and some tattletales. create arbitrary knowing relations between them (Mary knows John, for example). Make some of them reciprocal**

> ...
> Assistant: Done. I created six Person nodes with names and roles, and added directed and some reciprocal knows edges:
>- Mary (hooligan) — knows —> John (tattletale) [reciprocal]
>- John (tattletale) — knows —> Mary (hooligan) [reciprocal]
>- Alice (hooligan) — knows —> Bob (tattletale) [reciprocal]
>- Bob (tattletale) — knows —> Alice (hooligan) [reciprocal]
>- Carol (hooligan) — knows —> Dave (tattletale)
>- Dave (tattletale) — knows —> Alice (hooligan)
>- Bob (tattletale) — knows —> Mary (hooligan)
>- Carol (hooligan) — knows —> Mary (hooligan)
>
>UIDs assigned:
>- Mary: 0x4e46
>- John: 0x4e41
>- Alice: 0x4e42
>- Bob: 0x4e43
>- Carol: 0x4e44
>- Dave: 0x4e45
>
>Would you like me to run a query to show the graph, or add/remove any > relations?

**query the graph for every tattletale who knows a hooligan**

>...
>Assistant: I ran a query and found these tattletales who know at least one hooligan:
>
>- John (uid: 0x4e41)
>   - knows: Mary (hooligan, uid: 0x4e46)
>
>- Bob (uid: 0x4e43)
>   - knows: Alice (hooligan, uid: 0x4e42)
>   - knows: Mary (hooligan, uid: 0x4e46)
>
>- Dave (uid: 0x4e45)
>   - knows: Alice (hooligan, uid: 0x4e42)
>
>Note: I fetched all Person nodes and filtered by role client-side because the predicate "role" is not indexed. If you want a DGraph-side filter, I can add an exact/string index to the role predicate and rerun a query that directly selects tattletales. Would you like me to do that?

**go for it**
>...
>What I changed
>- Schema: role: string @index(exact) .
>
>Query run
>- DQL: { tattletales(func: eq(role, "tattletale")) { uid name role } }
>
>Results (tattletales)
>- uid 0x4e41 — John
>- uid 0x4e43 — Bob
>- uid 0x4e45 — Dave
>- uid 0x4e49 — John
>- uid 0x4e4b — Bob
>- uid 0x4e4d — Diana
>
>Notes / next steps
>- You can now use eq(role, "<value>") to filter by role in DQL.
>- eq is case-sensitive and matches the exact string. If you need case-insensitive matching or partial/token matches (e.g., substring search), I can add a different index type (term, trigram) or maintain a normalized lowercase predicate for role.
>- If you want, I can also remove duplicate-name nodes, dedupe by some other predicate, or run further queries (counts, relationships, etc.).
>
>Would you like any of the above (case-insensitive index, trigram index, dedupe, or additional queries)?

## LLMs consulted

I used GPT5 to resolve questions about DGraph usage and VS Code copilot with Sonnet to write the code. (Not Cursor because it is dead to me since they disabled move refactors.)