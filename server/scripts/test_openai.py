import os
import json
import httpx


def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("ERR: OPENAI_API_KEY not set")
        raise SystemExit(1)
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": "ping"}],
    }
    with httpx.Client(timeout=20.0) as client:
        r = client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=body)
    print(r.status_code)
    try:
        j = r.json()
        msg = (j.get("choices") or [{}])[0].get("message", {}).get("content", "")
        print((msg or "")[:200])
    except Exception:
        print((r.text or "")[:200])


if __name__ == "__main__":
    main()


