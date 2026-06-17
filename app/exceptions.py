from groq import APIConnectionError, AuthenticationError, RateLimitError


def triage_error_detail(exc: Exception) -> tuple[int, str]:
    if isinstance(exc, AuthenticationError):
        return (
            503,
            "Groq API authentication failed. Set a valid GROQ_API_KEY in .env and restart the server.",
        )
    if isinstance(exc, RateLimitError):
        return 429, "Groq API rate limit exceeded. Try again later or reduce batch size."
    if isinstance(exc, APIConnectionError):
        return 503, "Could not reach Groq API. Check your network connection."
    return 500, f"Triage failed: {type(exc).__name__}"
