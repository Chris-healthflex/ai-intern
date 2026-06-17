from langchain_groq import ChatGroq

from app.config import settings


def get_llm() -> ChatGroq:
    print("KEY:", settings.groq_api_key[:10])
    return ChatGroq(
        api_key=settings.groq_api_key,
        model=settings.groq_model,
        temperature=0.1,
    )
print("Model:", settings.groq_model)
print("Key prefix:", settings.groq_api_key[:10])
print("Key length:", len(settings.groq_api_key))