import json
import os
import re
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler

SYSTEM_INSTRUCTIONS = """
You are the public-facing AUREVIA AI Assistant for AUREVIA Caregiver Agency Ltd. in Nigeria.
Help visitors understand the public website, services and next steps. Be warm, clear, respectful, concise and never pressure people.
Approved website links:
[Home](#home) [Care Services](#services) [Client Assessment](#assess) [Aurevia Care Circle](#circle) [Care Supplies](#store) [Careers](#careers) [Cost & Rates](#rates) [Contact Us](#contact) [Blog](#blog) [Placement Options](#placement) [Appointment Escort](#escort) [Download Brochure](#brochure)
Never invent prices, availability, phone numbers, email addresses, qualifications, service promises, coverage areas, or policies. If not sure, direct the visitor to Contact Us or Client Assessment. Do not diagnose, prescribe, recommend medicines or claim to be a clinician. For emergencies, advise contacting local emergency services or a qualified healthcare professional immediately. Never claim to book, submit, purchase or contact staff for the visitor. Do not ask for private medical records, passwords, bank details or government ID numbers. Only use approved links above and public information.
"""

def send_json(handler, status, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("X-Content-Type-Options", "nosniff")
    handler.send_header("Content-Length", str(len(data)))
    handler.end_headers()
    handler.wfile.write(data)

def matches(q, terms):
    return any(term in q for term in terms)

def prepared_answer(message):
    """Free rule-based visitor guidance; no paid AI API is required."""
    q = re.sub(r"\s+", " ", message.lower()).strip()
    if not q:
        return "Please type your question. I can help you explore AUREVIA's website and services.\n\n[Care Services](#services) · [Contact Us](#contact)"

    # Emergency/safety questions must take priority over general service keywords.
    if matches(q, ("emergency", "can't breathe", "cannot breathe", "unconscious", "severe bleeding", "chest pain", "urgent medical", "medical emergency")):
        return "If someone may be in immediate danger or has urgent symptoms, contact local emergency services or a qualified healthcare professional now. I cannot assess emergencies through this chat. For non-emergency care arrangements, contact AUREVIA.\n\n[Contact Us](#contact)"

    if matches(q, ("hello", "hi", "hey", "good morning", "good afternoon", "good evening", "how are you", "who are you", "what can you do", "help me")):
        return ("Hello and welcome to AUREVIA Caregiver Agency Ltd. 💚 I can help you find information about home-care support, remote care, assessments, costs, placements, appointment escort, careers, care supplies, and website resources. "
                "What would you like help with?\n\n[Care Services](#services) · [Client Assessment](#assess) · [Contact Us](#contact)")

    if matches(q, ("whatsapp", "contact", "phone", "telephone", "email", "call you", "talk to someone", "speak to a person", "human", "staff", "team member", "customer service", "reach you", "address", "location", "where are you")):
        return ("You can contact AUREVIA using the official Contact Us section or WhatsApp option displayed on the website. Please use the website's own contact details; I won't guess a phone number, email address or office address.\n\n[Contact Us](#contact)")

    if matches(q, ("price", "prices", "cost", "costs", "rate", "rates", "how much", "fee", "fees", "payment", "pay", "afford", "cheap", "expensive", "quote", "quotation", "budget")):
        return ("Costs can depend on the service and the family's needs. I don't have verified live pricing, so I don't want to give you an incorrect amount. Ask AUREVIA for a current quote through the enquiry or contact page.\n\n[Cost & Rates](#rates) · [Client Assessment](#assess) · [Contact Us](#contact)")

    if matches(q, ("assessment", "assess", "enquiry", "inquiry", "application form", "form", "register for care", "registration", "sign up for care", "how do i start", "next step", "request care", "book a consultation")):
        return ("The Client Assessment/enquiry page is a good starting point to tell AUREVIA what support you are looking for. Complete the website form with the information it requests; please do not post private medical records in this chat. Submitting an enquiry does not mean a service is confirmed—the team must follow up.\n\n[Client Assessment](#assess) · [Care Services](#services) · [Contact Us](#contact)")

    if matches(q, ("caregiver", "care giver", "elderly", "older parent", "old age", "mother", "father", "family member", "home care", "care at home", "nursing", "need care", "find care", "personal care", "support at home", "dementia", "disability", "mobility", "companionship", "senior care", "parent lives alone", "help my parent")):
        return ("AUREVIA can help you explore personalised home-care support and caregiver services. The right arrangement depends on the person's needs and what the team can provide. Start with the service information and submit an enquiry so AUREVIA can discuss suitable next steps. Please do not share sensitive medical records here.\n\n[Care Services](#services) · [Client Assessment](#assess) · [Placement Options](#placement) · [Contact Us](#contact)")

    if matches(q, ("remote care", "care circle", "abroad", "distance", "family overseas", "check on my parent", "i live in another country", "overseas", "outside nigeria", "monitor my parent", "long distance", "video call")):
        return ("AUREVIA Care Circle is the website section to explore remote-care coordination for families who want to stay involved from a distance. The exact support available should be confirmed with the team.\n\n[Aurevia Care Circle](#circle) · [Client Assessment](#assess) · [Contact Us](#contact)")

    if matches(q, ("nanny", "placement", "live-in", "live in", "domestic staff", "staff placement", "hire a nanny", "hire caregiver", "recruit a caregiver", "find a nurse", "hire a nurse", "care worker")):
        return ("Explore AUREVIA's Placement Options for information about placement services. The team will need to confirm suitability, requirements and current availability for your request.\n\n[Placement Options](#placement) · [Care Services](#services) · [Contact Us](#contact)")

    if matches(q, ("appointment escort", "escort", "hospital visit", "doctor visit", "hospital appointment", "accompany me", "accompany my parent", "clinic visit", "medical appointment transport")):
        return ("For help related to attending appointments, explore AUREVIA's Appointment Escort information and contact the team to confirm what support is available. I cannot confirm a booking or transport arrangement through chat.\n\n[Appointment Escort](#escort) · [Contact Us](#contact)")

    if matches(q, ("supply", "supplies", "product", "buy", "shop", "equipment", "store", "catalogue", "catalog", "incontinence", "walking aid", "wheelchair", "care item", "delivery", "order product")):
        return ("You can explore AUREVIA's Care Supplies section for listed items. Check the website for current descriptions, prices, stock and ordering details; availability and delivery must be confirmed from the information provided there.\n\n[Care Supplies](#store) · [Contact Us](#contact)")

    if matches(q, ("job", "career", "work", "vacancy", "employment", "apply as", "caregiver role", "recruitment", "cv", "resume", "job application", "become a caregiver", "join aurevia", "staff opening")):
        return ("Thank you for your interest in working with AUREVIA. Visit the Careers section for the available recruitment information and next steps. I cannot confirm vacancies or hiring outcomes in chat.\n\n[Careers](#careers) · [Contact Us](#contact)")

    if matches(q, ("brochure", "download", "company profile", "information pack", "pdf", "service list", "what services", "list your services", "services do you offer", "what do you offer")):
        return ("You can explore the website's service information and brochure for an overview of AUREVIA. For details that are not listed or need confirmation, contact the team.\n\n[Download Brochure](#brochure) · [Care Services](#services) · [Contact Us](#contact)")

    if matches(q, ("blog", "article", "safety", "fall prevention", "advice", "tips", "read", "resources", "information", "learn about", "health article")):
        return ("Explore AUREVIA's blog for care-related articles and general information. Articles are for general guidance and do not replace assessment or advice from a qualified healthcare professional.\n\n[Blog](#blog) · [Care Services](#services)")

    if matches(q, ("policy", "policies", "terms", "conditions", "privacy", "data protection", "refund", "cancellation", "complaint", "feedback", "review", "report a problem")):
        return ("For AUREVIA's current policies, privacy information, complaints or feedback process, please check the relevant information published on the website or ask the team directly. I don't want to invent a policy that may not match the current terms.\n\n[Contact Us](#contact) · [Home](#home)")

    if matches(q, ("about aurevia", "about you", "company", "agency", "who is aurevia", "mission", "vision", "values", "why choose", "trust", "reliable", "licensed", "certified", "qualification", "experience")):
        return ("AUREVIA Caregiver Agency Ltd. provides information about its care services on this website. For verified details about qualifications, registration, service coverage, experience or policies, please check the published website information or contact the team; I won't guess or make unsupported claims.\n\n[Home](#home) · [Care Services](#services) · [Download Brochure](#brochure) · [Contact Us](#contact)")

    if matches(q, ("where do you operate", "coverage area", "areas do you cover", "do you serve", "available in", "outside lagos", "in lagos", "in abuja", "service area", "location do you cover", "do you come to")):
        return ("Service coverage can depend on the type of support requested. Please contact AUREVIA to confirm whether your location is covered before making arrangements.\n\n[Client Assessment](#assess) · [Contact Us](#contact)")

    if matches(q, ("thank you", "thanks", "that helps", "great", "okay", "ok")):
        return ("You're welcome! If you'd like, I can help you find the right AUREVIA page or explain the next step.\n\n[Care Services](#services) · [Client Assessment](#assess) · [Contact Us](#contact)")

    return ("Thank you for your question. I can help with common questions about AUREVIA's care services, assessments, remote care, placements, appointment escort, care supplies, careers, costs and website resources. I don't have a verified answer to this exact question, so I won't guess. Please contact the AUREVIA team for confirmation.\n\n"
            "[Care Services](#services) · [Client Assessment](#assess) · [Aurevia Care Circle](#circle) · [Care Supplies](#store) · [Placement Options](#placement) · [Careers](#careers) · [Cost & Rates](#rates) · [Contact Us](#contact)")

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        send_json(self, 405, {"error": "Method not allowed."})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length <= 0 or length > 18000:
                send_json(self, 413 if length > 18000 else 400, {"error": "Please send a valid, shorter message."})
                return
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            messages = body.get("messages", [])
            if not isinstance(messages, list):
                send_json(self, 400, {"error": "Invalid chat messages."})
                return
            cleaned = []
            for item in messages[-12:]:
                if not isinstance(item, dict):
                    continue
                role, content = item.get("role"), item.get("content")
                if role not in ("user", "assistant") or not isinstance(content, str):
                    continue
                content = content.strip()[:1200]
                if content:
                    cleaned.append({"role": role, "content": content})
            if not cleaned or cleaned[-1]["role"] != "user":
                send_json(self, 400, {"error": "Please enter a question first."})
                return

            api_key = os.environ.get("OPENAI_API_KEY", "").strip()
            if not api_key:
                send_json(self, 200, {"reply": prepared_answer(cleaned[-1]["content"]), "mode": "prepared"})
                return

            model = os.environ.get("OPENAI_MODEL", "gpt-6-astra").strip()
            api_payload = {"model": model, "instructions": SYSTEM_INSTRUCTIONS, "input": cleaned, "max_output_tokens": 650, "store": False}
            req = urllib.request.Request("https://api.openai.com/v1/responses", data=json.dumps(api_payload).encode("utf-8"), headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=25) as response:
                result = json.loads(response.read().decode("utf-8"))
            reply = result.get("output_text", "")
            if not reply:
                parts = []
                for item in result.get("output", []):
                    if item.get("type") == "message":
                        for content in item.get("content", []):
                            if content.get("type") == "output_text":
                                parts.append(content.get("text", ""))
                reply = "\n".join(part for part in parts if part).strip()
            if not reply:
                send_json(self, 502, {"error": "I couldn't prepare an answer. Please try again or contact AUREVIA."})
                return
            send_json(self, 200, {"reply": reply[:5000]})
        except urllib.error.HTTPError as exc:
            if exc.code == 429:
                send_json(self, 503, {"error": "The assistant is busy right now. Please try again shortly or contact AUREVIA."})
            else:
                send_json(self, 503, {"error": "The assistant is temporarily unavailable. Please contact AUREVIA directly for now."})
        except Exception:
            send_json(self, 500, {"error": "The assistant is temporarily unavailable. Please use the website contact options."})

    def log_message(self, format, *args):
        return
