from langchain.chat_models import ChatOpenAI # type: ignore

llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0,
    openai_api_key=""  

)
