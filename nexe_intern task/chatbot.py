"""Simple Python chatbot using Ollama API.

Features:
- Reads user input from the console.
- Sends the conversation (including history) to Ollama running locally on port 11434.
- Uses the model `gpt-oss:120b-cloud`.
- Handles connection errors, non-200 responses and JSON parsing errors.
- Maintains an in-memory conversation history for the session.
"""

import json
import sys
from typing import List, Dict

import requests

# Ollama endpoint configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "gpt-oss:120b-cloud"


def send_message(messages: List[Dict[str, str]]) -> str:
    payload = {
        "model": MODEL,
        "messages": messages,
    }
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=30)
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(f"Failed to connect to Ollama at {OLLAMA_URL}: {exc}") from exc

    if response.status_code != 200:
        raise RuntimeError(
            f"Ollama returned status {response.status_code}: {response.text}"
        )

    full_response = ""
    for line in response.text.strip().split("\n"):
        if line.strip():
            try:
                data = json.loads(line)
                if "message" in data:
                    full_response += data["message"].get("content", "")
            except json.JSONDecodeError:
                continue

    if not full_response:
        raise RuntimeError("No response received from Ollama")
    return full_response


def main() -> None:
    print("Chatbot ready. Type your message and press Enter. Empty line to quit.")
    history: List[Dict[str, str]] = []
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting.")
            break
        if not user_input:
            print("Goodbye!")
            break

        history.append({"role": "user", "content": user_input})

        try:
            assistant_reply = send_message(history)
        except RuntimeError as err:
            print(f"Error: {err}")
            history.pop()
            continue

        history.append({"role": "assistant", "content": assistant_reply})
        print(f"Assistant: {assistant_reply}")


if __name__ == "__main__":
    main()