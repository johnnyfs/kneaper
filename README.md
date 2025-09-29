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
poetry run python app/main.py
```


