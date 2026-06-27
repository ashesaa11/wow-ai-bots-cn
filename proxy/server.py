"""
Ollama → DeepSeek API Proxy
============================
Receives Ollama /api/generate requests from mod-ollama-chat,
translates them to DeepSeek API format, and returns Ollama-format responses.
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

CONFIG = {}


def load_config():
    global CONFIG
    with open("config.json", "r", encoding="utf-8") as f:
        CONFIG = json.load(f)


def call_deepseek(prompt, model, options):
    """Send prompt to DeepSeek API and return the response text."""
    messages = [{"role": "user", "content": prompt}]

    body = {
        "model": CONFIG["deepseek_model"],
        "messages": messages,
        "temperature": options.get("temperature", CONFIG["temperature"]),
        "top_p": options.get("top_p", CONFIG["top_p"]),
        "max_tokens": options.get("num_predict", CONFIG["max_tokens"]) or CONFIG["max_tokens"],
        "stream": False,
    }

    url = f"{CONFIG['deepseek_api_base']}/v1/chat/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {CONFIG['deepseek_api_key']}",
    }

    req = Request(url, data=json.dumps(body).encode("utf-8"), headers=headers)
    
    try:
        with urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data["choices"][0]["message"]["content"]
    except HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"DeepSeek HTTP {e.code}: {error_body}")
    except URLError as e:
        raise RuntimeError(f"DeepSeek connection failed: {e.reason}")


class ProxyHandler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]}")

    def do_GET(self):
        if self.path == "/api/tags":
            # Ollama health check - return fake model list
            self._json_response(200, {
                "models": [{"name": CONFIG["deepseek_model"], "modified_at": "", "size": 0}]
            })
        else:
            self._json_response(404, {"error": "not found"})

    def do_POST(self):
        if self.path != "/api/generate":
            self._json_response(404, {"error": "only /api/generate is supported"})
            return

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)
        
        try:
            request_data = json.loads(body)
        except json.JSONDecodeError:
            self._json_response(400, {"error": "invalid JSON"})
            return

        model = request_data.get("model", CONFIG["deepseek_model"])
        prompt = request_data.get("prompt", "")
        options = request_data.get("options", {})

        if not prompt:
            self._json_response(400, {"error": "empty prompt"})
            return

        print(f"[{time.strftime('%H:%M:%S')}] Prompt ({len(prompt)} chars) → DeepSeek...")

        try:
            response_text = call_deepseek(prompt, model, options)

            # Strip quotes and markdown that LLMs sometimes add
            response_text = response_text.strip().strip('"').strip("'")

            self._json_response(200, {
                "model": CONFIG["deepseek_model"],
                "response": response_text,
                "done": True,
                "total_duration": 0,
                "prompt_eval_count": 0,
                "eval_count": 0,
            })

            print(f"[{time.strftime('%H:%M:%S')}] Response: {response_text[:80]}...")

        except Exception as e:
            print(f"[ERROR] {e}")
            self._json_response(500, {
                "error": str(e),
                "done": True,
            })

    def _json_response(self, status, data):
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)


def main():
    load_config()
    host = CONFIG["listen_host"]
    port = CONFIG["listen_port"]
    server = HTTPServer((host, port), ProxyHandler)
    print(f"Ollama→DeepSeek proxy running on http://{host}:{port}")
    print(f"Model: {CONFIG['deepseek_model']}")
    print(f"Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
        server.server_close()


if __name__ == "__main__":
    main()
