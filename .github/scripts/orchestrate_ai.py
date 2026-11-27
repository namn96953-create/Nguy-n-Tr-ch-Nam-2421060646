import os
import requests

ISSUE_TITLE = os.environ.get("ISSUE_TITLE", "")
ISSUE_BODY = os.environ.get("ISSUE_BODY", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
ISSUE_NUMBER = os.environ.get("ISSUE_NUMBER", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

with open("AGENTS.md", "r", encoding="utf-8") as f:
    shared_context = f.read()

prompt_base = f"Ngữ cảnh dự án:\n{shared_context}\n\nYêu cầu:\n{ISSUE_TITLE}\n{ISSUE_BODY}"

# 1. Gemini lập kế hoạch
gemini_res = requests.post(
    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={os.environ['GEMINI_API_KEY']}",
    json={"contents": [{"parts": [{"text": f"Hãy lập kế hoạch triển khai ngắn gọn:\n{prompt_base}"}]}]},
    timeout=60,
).json()
plan = gemini_res["candidates"][0]["content"]["parts"][0]["text"]

# 2. Claude viết giải pháp / code
claude_res = requests.post(
    "https://api.anthropic.com/v1/messages",
    headers={
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    },
    json={
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1500,
        "messages": [{"role": "user", "content": f"Dựa trên kế hoạch sau, hãy viết code chi tiết:\n{plan}\n\n{prompt_base}"}],
    },
    timeout=60,
).json()
solution = claude_res["content"][0]["text"]

# 3. ChatGPT review chéo
openai_res = requests.post(
    "https://api.openai.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {os.environ['OPENAI_API_KEY']}",
        "Content-Type": "application/json",
    },
    json={
        "model": "gpt-4.1",
        "messages": [
            {"role": "system", "content": "Bạn là Tech Lead review code, tìm lỗi logic và bảo mật."},
            {"role": "user", "content": f"Review giải pháp sau:\n{solution}"},
        ],
    },
    timeout=60,
).json()
review = openai_res["choices"][0]["message"]["content"]

# Đăng kết quả lên GitHub Issue
comment_body = f"### 1. Kế hoạch (Gemini)\n{plan}\n\n---\n### 2. Giải pháp (Claude)\n{solution}\n\n---\n### 3. Review chéo (ChatGPT)\n{review}"
requests.post(
    f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}/comments",
    headers={"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"},
    json={"body": comment_body},
    timeout=30,
)
