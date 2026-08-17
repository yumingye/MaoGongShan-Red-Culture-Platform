"""Deterministic checks for the OpenAI-compatible grounded generation layer."""

from __future__ import annotations

import json
from unittest.mock import patch
from urllib.error import URLError

from backend import ai_service


DOCS = [{
    "title": "毛公山资料",
    "category": "景区概况",
    "summary": "毛公山位于青岛市城阳区惜福镇街道青峰社区。",
    "content": "平台资料提示访客在出发前核验最新开放信息。",
    "source_name": "平台资料库",
    "verification_status": "已核验",
}]


class FakeResponse:
    def __init__(self, payload: dict):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def read(self, _limit: int) -> bytes:
        return json.dumps(self.payload, ensure_ascii=False).encode("utf-8")


def main() -> int:
    context = ai_service.build_context(DOCS)
    assert "毛公山资料" in context and "核验状态：已核验" in context

    configured = {
        "LLM_PROVIDER": "compatible",
        "LLM_BASE_URL": "https://example.invalid/v1",
        "LLM_API_KEY": "test-key",
        "LLM_MODEL": "test-model",
    }
    with patch.multiple(ai_service, **configured):
        assert ai_service.generate_rag_answer("未知问题", []) == "当前资源库暂未收录足够资料。"
        with patch.object(ai_service, "urlopen", return_value=FakeResponse({"choices": [{"message": {"content": "仅依据资料库回答。"}}]})) as mocked:
            answer = ai_service.generate_rag_answer("毛公山在哪里？", DOCS, [{"role": "user", "content": "请介绍毛公山"}])
            assert answer == "仅依据资料库回答。"
            request = mocked.call_args.args[0]
            body = json.loads(request.data.decode("utf-8"))
            assert body["model"] == "test-model"
            assert "知识库资料" in body["messages"][-1]["content"]

        with patch.object(ai_service, "urlopen", side_effect=URLError("timeout")):
            try:
                ai_service.generate_rag_answer("毛公山在哪里？", DOCS)
            except ai_service.LLMServiceError as error:
                assert "不可用" in str(error) or "超时" in str(error)
            else:
                raise AssertionError("provider failure must be converted to LLMServiceError")

    with patch.object(ai_service, "LLM_BASE_URL", "file:///unsafe"):
        try:
            ai_service._endpoint()
        except ai_service.LLMServiceError:
            pass
        else:
            raise AssertionError("non-HTTP model endpoint must be rejected")

    print("All AI service checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
