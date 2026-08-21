"""DeepSeek-only streaming provider for the AI chat module (no RAG fallback)."""
from __future__ import annotations

import json
import logging
import time
from collections.abc import Iterator
from typing import Any
from urllib.parse import urlparse

import httpx

try:
    from .config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_PROVIDER, LLM_TIMEOUT_SECONDS
except ImportError:
    from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, LLM_PROVIDER, LLM_TIMEOUT_SECONDS

logger = logging.getLogger("maogongshan.ai")
SYSTEM_PROMPT = """你是“毛公山 AI 助手”。你可以优先帮助回答毛公山、青岛城阳、红色文化、党史文化、旅游与平台使用问题，也保留通用的大模型问答能力。自然、清晰地用中文回答；根据问题复杂度控制篇幅。可以使用 Markdown 标题、列表、加粗、引用和代码块。不要声称检索了平台本地知识库，也不要将未经用户提供的信息伪装成已核验的毛公山事实。"""


class LLMServiceError(RuntimeError):
    def __init__(self, message: str, kind: str = "unavailable", status_code: int | None = None):
        super().__init__(message)
        self.kind, self.status_code = kind, status_code


def _endpoint() -> str:
    parsed = urlparse(LLM_BASE_URL)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise LLMServiceError("AI 服务地址配置无效", "configuration")
    if (parsed.hostname or "").lower() == "api.deepseek.com":
        return "https://api.deepseek.com/chat/completions"
    return LLM_BASE_URL if LLM_BASE_URL.endswith("/chat/completions") else f"{LLM_BASE_URL}/chat/completions"


def llm_status() -> dict[str, Any]:
    configured = bool(LLM_PROVIDER.lower() == "deepseek" and LLM_API_KEY and LLM_BASE_URL and LLM_MODEL)
    return {"configured": configured, "provider": "deepseek" if configured else "", "model": LLM_MODEL if configured else "", "mode": "deepseek_chat" if configured else "unavailable"}


def _messages(question: str, history: list[dict[str, str]]) -> list[dict[str, str]]:
    result = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Bound the context: the latest five turns (ten messages), up to 1,800 chars each.
    for turn in history[-10:]:
        role, content = turn.get("role"), str(turn.get("content") or "").strip()
        if role in {"user", "assistant"} and content:
            result.append({"role": role, "content": content[:1800]})
    result.append({"role": "user", "content": question})
    return result


def _provider_error(response: httpx.Response) -> LLMServiceError:
    code = response.status_code
    if code == 429:
        return LLMServiceError("AI 服务当前繁忙", "busy", code)
    if code in {408, 500, 502, 503, 504}:
        return LLMServiceError("AI 服务暂时不可用", "transient", code)
    if code in {401, 403}:
        logger.error("[AI] DeepSeek authentication rejected status=%s", code)
        return LLMServiceError("AI 服务暂时不可用", "configuration", code)
    logger.warning("[AI] DeepSeek HTTP status=%s", code)
    return LLMServiceError("AI 服务暂时不可用", "unavailable", code)


def stream_answer(question: str, history: list[dict[str, str]]) -> Iterator[str]:
    """Yield DeepSeek SSE deltas; retry 1s/2s only before the first token."""
    if not llm_status()["configured"]:
        raise LLMServiceError("DeepSeek 未配置", "configuration")
    payload = {"model": LLM_MODEL, "messages": _messages(question, history), "temperature": 0.7, "stream": True}
    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json", "Accept": "text/event-stream", "User-Agent": "MaoGongShan-AI/2.0"}
    for attempt, delay in enumerate((0, 1, 2), start=1):
        if delay:
            logger.info("[AI] retry=%s wait_seconds=%s", attempt - 1, delay)
            time.sleep(delay)
        emitted, started = False, time.monotonic()
        try:
            logger.info("[AI] request started provider=deepseek model=%s attempt=%s", LLM_MODEL, attempt)
            timeout = httpx.Timeout(LLM_TIMEOUT_SECONDS, connect=min(10, LLM_TIMEOUT_SECONDS))
            with httpx.Client(timeout=timeout, follow_redirects=False) as client:
                with client.stream("POST", _endpoint(), headers=headers, json=payload) as response:
                    if response.status_code != 200:
                        raise _provider_error(response)
                    for line in response.iter_lines():
                        if not line or not line.startswith("data:"):
                            continue
                        data = line[5:].strip()
                        if data == "[DONE]":
                            logger.info("[AI] success elapsed_ms=%s", round((time.monotonic() - started) * 1000))
                            return
                        try:
                            delta = json.loads(data).get("choices", [{}])[0].get("delta", {}).get("content", "")
                        except (json.JSONDecodeError, AttributeError, IndexError, TypeError) as exc:
                            raise LLMServiceError("AI 服务返回格式异常") from exc
                        if delta:
                            emitted = True
                            yield str(delta)
            if emitted:
                return
            raise LLMServiceError("AI 服务未返回有效内容")
        except httpx.TimeoutException:
            error = LLMServiceError("AI 响应超时", "timeout")
        except httpx.NetworkError:
            error = LLMServiceError("AI 服务网络连接失败", "network")
        except LLMServiceError as exc:
            error = exc
        if emitted or attempt == 3 or error.kind not in {"busy", "transient", "timeout", "network"}:
            logger.warning("[AI] failed after attempt=%s kind=%s", attempt, error.kind)
            raise error


def user_error_message(error: LLMServiceError) -> str:
    if error.kind == "busy":
        return "AI 服务当前繁忙，请稍后重新提问。"
    if error.kind == "timeout":
        return "AI 响应超时，请重新发送。"
    return "AI 服务暂时不可用，请稍后再试。"
