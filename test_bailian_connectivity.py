from runtime_keys import load_bailian_runtime_config


def run_chat_check() -> str:
    from langchain_openai import ChatOpenAI

    runtime_config = load_bailian_runtime_config()
    chat_model = ChatOpenAI(
        model=runtime_config.chat_model_name,
        api_key=runtime_config.dashscope_api_key,
        base_url=runtime_config.dashscope_base_url,
    )
    response = chat_model.invoke("Reply with exactly: BAILIAN_CHAT_OK")
    return response.content if hasattr(response, "content") else str(response)


def run_embedding_check() -> int:
    from langchain_community.embeddings import DashScopeEmbeddings

    runtime_config = load_bailian_runtime_config()
    embeddings = DashScopeEmbeddings(
        model=runtime_config.embedding_model_name,
        dashscope_api_key=runtime_config.dashscope_api_key,
    )
    vector = embeddings.embed_query("Bailian embedding connectivity check")
    return len(vector)


def main() -> int:
    try:
        chat_result = run_chat_check()
        embedding_length = run_embedding_check()
    except Exception as exc:
        print(f"Bailian connectivity check failed: {exc}")
        return 1

    print(f"Bailian chat check succeeded: {chat_result}")
    print(f"Bailian embedding check succeeded: vector_length={embedding_length}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
