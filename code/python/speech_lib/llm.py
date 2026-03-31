from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def chat(user_message: str, system_message: str = "You are a helpful assistant.") -> str:
    """Send a message to an Azure AI Foundry language model and return the response text.

    Requires AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and
    AZURE_OPENAI_DEPLOYMENT in environment variables.
    """
    from openai import OpenAI

    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT")

    if not endpoint or not api_key or not deployment:
        raise RuntimeError(
            "Missing environment variables. "
            "Set AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, and "
            "AZURE_OPENAI_DEPLOYMENT (or update your .env file)."
        )

    client = OpenAI(
        api_key=api_key,
        base_url=f"{endpoint.rstrip('/')}/openai/v1/",
    )

    completion = client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message},
        ],
    )

    return completion.choices[0].message.content
