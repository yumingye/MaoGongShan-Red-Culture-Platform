"""Offline checks for the DeepSeek-only streaming chat provider."""
from __future__ import annotations

import json
from unittest.mock import patch

from backend import ai_service


class Response:
    def __init__(self, status: int = 200, lines: list[str] | None = None):
        self.status_code, self._lines = status, lines or []
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def iter_lines(self): yield from self._lines


class Client:
    def __init__(self, response): self.response = response
    def __enter__(self): return self
    def __exit__(self, *_): return False
    def stream(self, *_args, **_kwargs): return self.response


def main() -> None:
    configured = {"LLM_PROVIDER": "deepseek", "LLM_BASE_URL": "https://api.deepseek.com", "LLM_API_KEY": "test-key", "LLM_MODEL": "deepseek-chat"}
    delta = 'data: ' + json.dumps({"choices": [{"delta": {"content": "**流式**回答"}}]})
    with patch.multiple(ai_service, **configured):
        assert ai_service._endpoint() == "https://api.deepseek.com/chat/completions"
        messages = ai_service._messages("它在哪里？", [{"role": "user", "content": "介绍毛公山"}] * 12)
        assert len(messages) == 12 and messages[-1]["content"] == "它在哪里？"
        with patch.object(ai_service.httpx, "Client", return_value=Client(Response(lines=[delta, "data: [DONE]"]))):
            assert "".join(ai_service.stream_answer("测试", [])) == "**流式**回答"
        # 429 is retried before the first token, and no local answer is produced.
        clients = [Client(Response(429)), Client(Response(429)), Client(Response(429))]
        with patch.object(ai_service.httpx, "Client", side_effect=clients), patch.object(ai_service.time, "sleep"):
            try: list(ai_service.stream_answer("测试", []))
            except ai_service.LLMServiceError as error: assert ai_service.user_error_message(error) == "AI 服务当前繁忙，请稍后重新提问。"
            else: raise AssertionError("429 must not become a local answer")
        clients = [Client(Response(503)), Client(Response(503)), Client(Response(503))]
        with patch.object(ai_service.httpx, "Client", side_effect=clients), patch.object(ai_service.time, "sleep"):
            try: list(ai_service.stream_answer("测试", []))
            except ai_service.LLMServiceError as error: assert ai_service.user_error_message(error) == "AI 服务暂时不可用，请稍后再试。"
            else: raise AssertionError("503 must not become a local answer")
    print("All DeepSeek streaming checks passed.")


if __name__ == "__main__": main()
