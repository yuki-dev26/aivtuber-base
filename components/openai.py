import os
import dotenv
from pathlib import Path
from openai import OpenAI as OpenAIClient

dotenv.load_dotenv()

CHARACTER_PROMPT_PATH = (
    Path(__file__).resolve().parent.parent / "config" / "character.md"
)


def load_system_prompt() -> str:
    try:
        return CHARACTER_PROMPT_PATH.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""


class OpenAI:
    def __init__(self) -> None:
        self.api_key = os.environ.get("OPENAI_API_KEY", "")
        if self.api_key:
            self.client = OpenAIClient(api_key=self.api_key)
        else:
            self.client = None

        self.model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
        self.clear_history()

    def clear_history(self) -> None:
        self.system_prompt = load_system_prompt()
        self.previous_response_id = None

    def update_system_prompt(self) -> None:
        self.clear_history()

    def create_chat(self, question: str, temperature: float = 1.0):
        try:
            if not self.client:
                return None

            request_params = {
                "model": self.model,
                "instructions": self.system_prompt,
                "input": question,
                "temperature": temperature,
            }

            if self.previous_response_id:
                request_params["previous_response_id"] = self.previous_response_id

            res = self.client.responses.create(**request_params)

            self.previous_response_id = res.id

            response_content = res.output_text or ""
            response_content = response_content.replace("*", "")

            print("\033[32m✅ 応答を生成しました\033[0m")

            return response_content

        except Exception as e:
            print(f"\033[31mOpenAI API エラー: {str(e)}\033[0m")
            return None
