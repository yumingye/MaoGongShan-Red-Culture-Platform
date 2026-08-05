"""对公开问答的匹配度、内容长度和差异性做回归检查。"""

from __future__ import annotations

import json
from urllib import request


QUESTIONS = [
    "毛公山在哪里？",
    "毛公山有什么特色？",
    "如何规划游览路线？",
    "老年人游览需要注意什么？",
    "毛公山与红色文化有什么联系？",
    "平台有哪些功能？",
    "如何进入数字展馆？",
    "如何查看景点地图？",
    "什么是长征精神？",
    "青年学生如何传承红色基因？",
    "山东大学软件学院团队进行了哪些工作？",
    "平台为什么要建设红色数字资源库？",
    "图片或视频无法加载怎么办？",
    "如何搜索党史知识？",
    "如何查看社会实践成果？",
    "平台怎样避免编造历史信息？",
    "毛公山图片是否都是真实照片？",
    "地图没有高德密钥还能使用吗？",
    "团队怎样整理访谈记录？",
    "这个项目是谁开发的？",
]


def ask(question: str) -> dict:
    body = json.dumps({"question": question}, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        "http://127.0.0.1:8000/api/chat",
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    with request.urlopen(req, timeout=12) as response:
        return json.loads(response.read().decode("utf-8"))


def main() -> None:
    failures: list[str] = []
    normalized_answers: set[str] = set()
    for question in QUESTIONS:
        payload = ask(question)
        answer = str(payload.get("answer") or "").strip()
        sources = payload.get("sources") or []
        if len(answer) < 80:
            failures.append(f"{question}：回答过短（{len(answer)} 字）")
        if not sources:
            failures.append(f"{question}：缺少相关资料")
        normalized_answers.add(answer)
        print(f"通过：{question}（{len(answer)} 字，{len(sources)} 条资料）")
    if len(normalized_answers) < len(QUESTIONS) * 0.8:
        failures.append(f"回答差异不足：{len(normalized_answers)}/{len(QUESTIONS)}")
    if failures:
        raise SystemExit("问答检查失败：\n- " + "\n- ".join(failures))
    print(f"问答内容检查通过：{len(QUESTIONS)} 个问题，{len(normalized_answers)} 个不同回答。")


if __name__ == "__main__":
    main()
