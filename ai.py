import os
from typing import Any, Dict
import requests
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

API_URL = "https://geovpn.2bd.net:23238"
CLIENT_API_KEY = os.getenv("CLIENT_API_KEY")

if not CLIENT_API_KEY:
    raise ValueError(
        "Критическая ошибка: Переменная окружения CLIENT_API_KEY не найдена в файле .env"
    )

headers = {"X-API-Key": CLIENT_API_KEY, "Content-Type": "application/json"}


class UserProfile(BaseModel):
    username: str
    is_premium: bool
    connections_limit: int


def test_text_request():
    print("--- Тест 1: Текстовый запрос (Groq) ---")
    payload = {
        "provider": "groq",
        "prompt": "Расскажи шутку про сисадминов в одну строку.",
        "system_instruction": "Ты остроумный технический ассистент.",
    }

    response = requests.post(
        f"{API_URL}/v1/chat/text", json=payload, headers=headers, verify=True
    )
    if response.status_code == 200:
        data = response.json()
        print(f"Использована модель: {data['model_used']}")
        print(f"Ответ: {data['content']}\n")
    else:
        print(f"Ошибка: {response.status_code}, {response.text}\n")


def test_json_request():
    print("--- Тест 2: JSON запрос со схемой шаблона (Gemini) ---")

    schema_template = {
        "username": "string",
        "is_premium": "boolean",
        "connections_limit": "integer",
    }

    payload = {
        "provider": "gemini",
        "prompt": "Сгенерируй тестовый профиль для пользователя с ником Matrix, он оплатил подписку VIP и ему доступно 5 устройств.",
        "schema_fields": schema_template,
    }

    response = requests.post(
        f"{API_URL}/v1/chat/json", json=payload, headers=headers, verify=True
    )
    if response.status_code == 200:
        data = response.json()
        print(f"Использована модель: {data['model_used']}")
        print(f"Сырой JSON от прослойки: {data['content']}")

        try:
            profile = UserProfile(**data["content"])
            print("Successfully parsed into local Pydantic model!")
            print(
                f"Username: {profile.username}, Premium: {profile.is_premium}, Limit: {profile.connections_limit}"
            )
        except Exception as e:
            print(f"Ошибка валидации Pydantic на клиенте: {e}")
    else:
        print(f"Ошибка: {response.status_code}, {response.text}")


if __name__ == "__main__":
    test_text_request()
    test_json_request()