# Bailian runtime key loading design

## Goal

Make the project run against Alibaba Cloud Bailian using one private runtime config file at the repository root: `key.json`.

The runtime should no longer depend on manually exported environment variables. Instead, code that needs chat or embedding credentials should load `key.json` directly and pass the values to the corresponding client constructors.

## Scope

### In scope

1. Define a single private config source: repository-root `key.json`.
2. Add one shared runtime loader for Bailian credentials and model settings.
3. Update chat and embedding client creation to use explicit runtime parameters instead of environment variables.
4. Update independent scripts to load the same root config on their own.
5. Replace environment-variable credential checks with `key.json` validation.
6. Add one minimal connectivity test for Bailian chat and embedding.

### Out of scope

- running full RAG evaluation flows
- changing retrieval logic or chunking behavior
- adding multi-provider support
- persisting secrets anywhere except local `key.json`
- committing `key.json` to git

## Approved config shape

The repository root will contain a local-only file named `key.json` with this shape:

```json
{
  "dashscope_api_key": "...",
  "dashscope_base_url": "...",
  "chat_model_name": "qwen3-max",
  "embedding_model_name": "text-embedding-v4"
}
```

This file is the only supported credential source for this work.

## Design summary

Introduce one small runtime config module responsible for loading and validating Bailian settings from the repository root.

All runtime code that needs Bailian access should call this module and receive a structured config object. The module should not write values into `os.environ`. Client code should pass the loaded values directly to LangChain or DashScope client constructors.

This keeps credential handling private, explicit, and consistent across the app runtime and standalone scripts.

## File and component design

### Runtime config loader

#### New file: `runtime_keys.py`

This module should:

- resolve the repository-root `key.json`
- parse JSON with UTF-8
- validate that all four required fields exist and are non-empty strings
- return a structured runtime config object
- raise a clear runtime error when the file is missing, malformed, or incomplete

This module should be the only place that knows the JSON field names.

### Chat runtime integration

#### `rag.py`

`RagService` currently builds:

- `DashScopeEmbeddings(...)`
- `ChatOpenAI(...)`

After this change, `rag.py` should load runtime config once and pass values explicitly:

- `DashScopeEmbeddings(model=embedding_model_name, dashscope_api_key=dashscope_api_key)`
- `ChatOpenAI(model=chat_model_name, api_key=dashscope_api_key, base_url=dashscope_base_url)`

This keeps the current service shape but removes the hidden dependency on exported shell variables.

### Knowledge-base integration

#### `knowledge_base.py`

Any standalone embedding initialization in this file should use the same shared runtime config loader and pass `dashscope_api_key` explicitly.

This preserves current ingestion behavior while making independent execution consistent with the main runtime.

### Evaluation script integration

#### `eval_ragas.py`

This script should stop checking `OPENAI_API_KEY` from the environment. Instead, it should validate that the root `key.json` is readable and complete by using the shared loader.

The rest of the script should continue to use the normal runtime services.

#### `eval_chunking.py`

This script should stop checking both `OPENAI_API_KEY` and `DASHSCOPE_API_KEY` from the environment. It should validate `key.json` through the shared loader.

The script should remain independently runnable from the repository root without any manual export step.

### Minimal connectivity test

#### New file: `test_bailian_connectivity.py`

Add one standalone test entrypoint that:

1. loads `key.json`
2. makes one minimal chat request through the configured Bailian-compatible chat client
3. makes one minimal embedding request through the configured embedding client
4. prints success or a concise failure message

The test should never print the API key.

## Data flow

The runtime flow should be:

`key.json -> runtime_keys.py -> structured config -> explicit client constructor args -> Bailian services`

For independent scripts, the flow is the same:

`key.json -> runtime_keys.py -> script/runtime service -> Bailian services`

There should be no required shell export step in the normal path.

## Error handling

Runtime failures should be clear and local:

- missing `key.json`: explain that the root private config file is required
- invalid JSON: explain that `key.json` is malformed
- missing required field: name the missing field
- empty string field: name the empty field
- connectivity failure: surface the provider/client error without printing secrets

The loader should fail fast before any expensive runtime work begins.

## Testing strategy

### Unit-level expectations

Add or update tests around the loader to cover:

- file missing
- invalid JSON
- missing field
- empty field
- successful parse

### Minimal live verification

The user-approved success criterion for this task is a minimal live connectivity check only:

1. Bailian chat call succeeds
2. Bailian embedding call succeeds

Full RAG runs and evaluation runs are not part of this verification step.

## Security constraints

- `key.json` stays local and must not be committed
- secrets are loaded at runtime only
- secrets are passed directly to clients, not copied into tracked files
- logs and test output must not print the key value

## Recommended approach

Use one shared runtime config loader plus explicit constructor parameters.

This is better than per-script ad hoc JSON reads because it keeps validation behavior consistent. It is also cleaner than loading `key.json` and backfilling `os.environ`, because the runtime dependencies remain explicit in code.

## Implementation boundary

This is a focused runtime-config change. It should touch only the files needed to:

- load private Bailian config
- wire chat and embedding clients
- remove environment-only credential assumptions
- add the minimal connectivity test

It should not expand into provider abstraction or broader config refactoring.
