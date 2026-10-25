import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler

MAX_BODY_BYTES = 12000
ALLOWED_ORIGIN = "https://aureviacaregiveragency.vercel.app"

SYSTEM_INSTRUCTIONS = """You are the public AUREVIA AI Assistant for AUREVIA Caregiver Agency Ltd. You help website visitors understand services and find the right page.
Use a warm, clear, professional tone. Ask at most one follow-up question at a time.
Only state prices, availability, service areas, policies, or eligibility when the visitor's question is covered by the information provided here; otherwise say the team must confirm.
Public website sections and routes:
- Care Services: #services (individual service details may be reached from that page)
- Client Assessment / enquiry form: #assess
- AUREVIA Care Circle: #circle
- Care Supplies store: #store
- Careers: #careers
- Contact: #contact
- About: #about
- Blog: #blog
The agency offers caregiver support, nursing and post-hospital support, specialist support and coordination, nanny/childcare services, appointment escort, and remote care coordination. Service suitability and availability must be confirmed by the agency. Never invent prices or promise a booking, placement, or availability.
Guide people to the Client Assessment form for a care enquiry, or suggest contacting the team on WhatsApp. Do not ask visitors to send detailed medical records, passwords, payment-card details, or other sensitive information in chat. Do not access or reveal staff/client records. Do not diagnose, prescribe, or replace a clinician. For an immediate medical emergency, tell the visitor to contact local emergency services or go to the nearest emergency department.
Keep answers concise and helpful. If a question is outside AUREVIA's public services, say what you can help with and offer the relevant website page or contact route.
"""

def _json(handler, status, payload):
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        _json(self, 204, {})

    def do_POST(self):
        origin = self.headers.get("Origin")
        if origin and origin.rstrip("/") != ALLOWED_ORIGIN:
            return _json(self, 403, {"error": "Request origin not allowed."})

        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            size = 0
        if size < 2 or size > MAX_BODY_BYTES:
            return _json(self, 413, {"error": "Please send a shorter message."})

        try:
            data = json.loads(self.rfile.read(size).decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            return _json(self, 400, {"error": "Please send a valid message."})

        messages = data.get("messages", []) if isinstance(data, dict) else []
        if not isinstance(messages, list) or not messages or len(messages) > 12:
            return _json(self, 400, {"error": "Please start a new chat and try again."})

        allowed = []
        for item in messages[-10:]:
            if not isinstance(item, dict) or item.get("role") not in ("user", "assistant"):
                continue
            content = item.get("content", "")
            if not isinstance(content, str):
                continue
            content = content.strip()[:1800]
            if content:
                allowed.append({"role": item["role"], "content": content})
        if not allowed or allowed[-1]["role"] != "user":
            return _json(self, 400, {"error": "Please enter a message first."})

        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            return _json(self, 503, {"error": "The AUREVIA assistant is being configured. Please use the website enquiry form or WhatsApp for help for now."})

        payload = {
            "model": os.environ.get("OPENAI_MODEL", "gpt-5.5"),
            "instructions": SYSTEM_INSTRUCTIONS,
            "input": allowed,
            "max_output_tokens": 450,
            "store": False
        }
        req = urllib.request.Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                result = json.loads(response.read().decode("utf-8"))
            answer = result.get("output_text", "")
            if not answer:
                parts = []
                for item in result.get("output", []):
                    if item.get("type") == "message":
                        for block in item.get("content", []):
                            if block.get("type") == "output_text":
                                parts.append(block.get("text", ""))
                answer = "\n".join(parts)
            if not answer:
                return _json(self, 502, {"error": "I couldn't prepare an answer just now. Please try again or contact our team."})
            return _json(self, 200, {"answer": answer[:5000]})
        except urllib.error.HTTPError as exc:
            # Do not return provider details or secrets to the public visitor.
            return _json(self, 502, {"error": "The assistant is temporarily unavailable. Please try again or contact our team."})
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
            return _json(self, 502, {"error": "The assistant is temporarily unavailable. Please try again or contact our team."})

    def log_message(self, format, *args):
        # Avoid logging visitor messages or other personal content.
        return
