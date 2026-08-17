"""Deterministic checks for the OpenAI-compatible grounded generation layer."""

from __future__ import annotations

import json
from email.message import Message
from io import BytesIO
from unittest.mock import patch
from urllib.error import HTTPError, URLError

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


def redirect_error(url: str, location: str, status: int = 307) -> HTTPError:
    headers = Message()
    headers["Location"] = location
    return HTTPError(url, status, "redirect", headers, BytesIO(b""))


def provider_error(url: str, status: int, body: str) -> HTTPError:
    return HTTPError(url, status, "provider error", Message(), BytesIO(body.encode("utf-8")))


def main() -> int:
    context = ai_service.build_context(DOCS)
    assert "毛公山资料" in context and "核验状态：已核验" in context
    assert ai_service._looks_incomplete("这是一段被截断的讲解", "guide")
    assert not ai_service._looks_incomplete("这是一段长度足够、能够完整结束的导游讲解。" * 8, "guide")
    assert ai_service._origin("https://API.DeepSeek.com/chat/completions") == ai_service._origin(
        "https://api.deepseek.com:443/chat/completions"
    )

    configured = {
        "LLM_PROVIDER": "compatible",
        "LLM_BASE_URL": "https://example.invalid/v1",
        "LLM_API_KEY": "test-key",
        "LLM_MODEL": "test-model",
    }
    with patch.multiple(ai_service, **configured):
        assert ai_service.llm_status()["transport"] == "urllib-safe-redirect-error-v2"
        assert ai_service._endpoint() == "https://example.invalid/v1/chat/completions"
        with patch.object(ai_service._HTTP_OPENER, "open", return_value=FakeResponse({"choices": [{"message": {"content": "可说明的部分会继续回答。"}}]})) as mocked_empty:
            assert ai_service.generate_rag_answer("未知问题", [], persona="guide", retrieval_quality="none") == "可说明的部分会继续回答。"
            assert mocked_empty.call_count == 2
            empty_body = json.loads(mocked_empty.call_args.args[0].data.decode("utf-8"))
            assert "未检索到可用" in empty_body["messages"][-1]["content"]
            assert "数字讲解员" in empty_body["messages"][0]["content"]
        with patch.object(ai_service._HTTP_OPENER, "open", return_value=FakeResponse({"choices": [{"message": {"content": "仅依据资料库回答。"}}]})) as mocked:
            answer = ai_service.generate_rag_answer("毛公山在哪里？", DOCS, [{"role": "user", "content": "请介绍毛公山"}])
            assert answer == "仅依据资料库回答。"
            request = mocked.call_args.args[0]
            body = json.loads(request.data.decode("utf-8"))
            assert body["model"] == "test-model"
            assert "知识库与联网资料" in body["messages"][-1]["content"]

        redirect = redirect_error(
            "https://example.invalid/v1/chat/completions",
            "/v1/chat/completions/",
        )
        success = FakeResponse({"choices": [{"message": {"content": "重定向后回答成功。"}}]})
        with patch.object(ai_service._HTTP_OPENER, "open", side_effect=[redirect, success]) as mocked:
            with patch.object(ai_service.logger, "warning") as warning:
                answer = ai_service.generate_rag_answer("毛公山在哪里？", DOCS)
            assert answer == "重定向后回答成功。"
            assert mocked.call_count == 2
            assert mocked.call_args_list[0].args[0].full_url == "https://example.invalid/v1/chat/completions"
            assert mocked.call_args_list[1].args[0].full_url == "https://example.invalid/v1/chat/completions/"
            assert "test-key" not in " ".join(map(str, warning.call_args.args))

        unsafe_redirect = redirect_error(
            "https://example.invalid/v1/chat/completions",
            "https://attacker.invalid/collect?token=secret",
        )
        with patch.object(ai_service._HTTP_OPENER, "open", side_effect=unsafe_redirect):
            try:
                ai_service.generate_rag_answer("毛公山在哪里？", DOCS)
            except ai_service.LLMServiceError as error:
                assert "其他域名" in str(error)
            else:
                raise AssertionError("cross-origin redirect must be rejected")

        with patch.object(ai_service._HTTP_OPENER, "open", side_effect=URLError("timeout")):
            try:
                ai_service.generate_rag_answer("毛公山在哪里？", DOCS)
            except ai_service.LLMServiceError as error:
                assert "不可用" in str(error) or "超时" in str(error)
            else:
                raise AssertionError("provider failure must be converted to LLMServiceError")

        secret = "sk-test-secret-that-must-not-appear"
        bad_request = provider_error(
            "https://example.invalid/v1/chat/completions",
            400,
            '{"error":{"message":"invalid model","api_key":"' + secret + '"}}',
        )
        with patch.object(ai_service._HTTP_OPENER, "open", side_effect=bad_request):
            with patch.object(ai_service.logger, "warning") as warning:
                try:
                    ai_service.generate_rag_answer("毛公山在哪里？", DOCS)
                except ai_service.LLMServiceError as error:
                    safe_error = str(error)
                else:
                    raise AssertionError("provider HTTP failure must be converted to LLMServiceError")
            log_text = " ".join(map(str, warning.call_args.args))
            assert "invalid model" in safe_error
            assert secret not in safe_error and secret not in log_text

        transient_success = FakeResponse({"choices": [{"message": {"content": "瞬时失败重试后回答成功。"}}]})
        with patch.object(ai_service._HTTP_OPENER, "open", side_effect=[URLError("timeout"), transient_success]) as mocked_retry:
            assert ai_service.generate_rag_answer("毛公山在哪里？", DOCS) == "瞬时失败重试后回答成功。"
            assert mocked_retry.call_count == 2

    with patch.object(ai_service, "LLM_BASE_URL", "file:///unsafe"):
        try:
            ai_service._endpoint()
        except ai_service.LLMServiceError:
            pass
        else:
            raise AssertionError("non-HTTP model endpoint must be rejected")

    with patch.multiple(ai_service, LLM_PROVIDER="deepseek", LLM_BASE_URL="https://api.deepseek.com"):
        assert ai_service._endpoint() == "https://api.deepseek.com/chat/completions"
    with patch.multiple(ai_service, LLM_PROVIDER="deepseek", LLM_BASE_URL="http://api.deepseek.com"):
        assert ai_service._endpoint() == "https://api.deepseek.com/chat/completions"

    print("All AI service checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
