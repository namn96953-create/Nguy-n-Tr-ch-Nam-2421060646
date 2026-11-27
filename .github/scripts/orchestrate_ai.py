import os
import requests

ISSUE_TITLE = os.environ.get("ISSUE_TITLE", "")
ISSUE_BODY = os.environ.get("ISSUE_BODY", "")
REPO = os.environ.get("GITHUB_REPOSITORY", "")
ISSUE_NUMBER = os.environ.get("ISSUE_NUMBER", "")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN", "")

shared_context = ""
if os.path.exists("AGENTS.md"):
    with open("AGENTS.md", "r", encoding="utf-8") as f:
        shared_context = f.read()

prompt_base = f"Ngữ cảnh dự án:\n{shared_context}\n\nYêu cầu công việc:\n{ISSUE_TITLE}\n{ISSUE_BODY}"

try:
    gemini_res = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={os.environ.get('GEMINI_API_KEY', '')}",
        json={"contents": [{"parts": [{"text": f"Hãy lập kế hoạch triển khai ngắn gọn, rõ ràng:\n{prompt_base}"}]}]},
        timeout=60,
    ).json()
    plan = gemini_res["candidates"][0]["content"]["parts"][0]["text"]
except Exception as e:
    plan = f"⚠️ Lỗi gọi Gemini API: {e} | Chi tiết: {gemini_res if 'gemini_res' in locals() else 'Không có phản hồi'}"

try:
    claude_res = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""),
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 2000,
            "messages": [{"role": "user", "content": f"Dựa trên kế hoạch sau, hãy viết mã nguồn và cấu hình chi tiết:\n{plan}\n\n{prompt_base}"}],
        },
        timeout=60,
    ).json()
    solution = claude_res["content"][0]["text"]
except Exception as e:
    solution = f"⚠️ Lỗi gọi Claude API: {e} | Chi tiết: {claude_res if 'claude_res' in locals() else 'Không có phản hồi'}"

try:
    openai_res = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {os.environ.get('OPENAI_API_KEY', '')}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4.1",
            "messages": [
                {"role": "system", "content": "Bạn là Tech Lead chuyên về ROS và robot tự hành SLAM, hãy review giải pháp, tìm lỗi logic, TF và đề xuất tối ưu."},
                {"role": "user", "content": f"Review giải pháp sau:\n{solution}"},
            ],
        },
        timeout=60,
    ).json()
    review = openai_res["choices"][0]["message"]["content"]
except Exception as e:
    review = f"⚠️ Lỗi gọi ChatGPT API: {e} | Chi tiết: {openai_res if 'openai_res' in locals() else 'Không có phản hồi'}"

comment_body = (
    f"### 1. Kiến trúc & Kế hoạch (Gemini)\n{plan}\n\n"
    f"---\n### 2. Mã nguồn & Cấu hình (Claude)\n{solution}\n\n"
    f"---\n### 3. Review & Tối ưu thực tế (ChatGPT)\n{review}"
)

requests.post(
    f"https://api.github.com/repos/{REPO}/issues/{ISSUE_NUMBER}/comments",
    headers={"Authorization": f"Bearer {GITHUB_TOKEN}", "Accept": "application/vnd.github+json"},
    json={"body": comment_body},
    timeout=30,
)
