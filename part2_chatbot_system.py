"""
============================================================
PART 2 — Role-Governed Conversational Automation System
============================================================
Core Logic: Multi-Agent Isolation & Intelligent Routing
Compliance: Strictly adheres to Role-Based Access Control (RBAC)
============================================================
"""

import sys
import os
import csv
import json
import time
from datetime import datetime

# FIX: Ensure global libraries are accessible for the LLM component
try:
    user_site = os.path.join(os.environ['APPDATA'], 'Python', f'Python{sys.version_info.major}{sys.version_info.minor}', 'site-packages')
    if user_site not in sys.path:
        sys.path.append(user_site)
    from duckduckgo_search import DDGS
    HAS_LLM = True
except:
    HAS_LLM = False

# --------------------------------------------------
# ROLE-BASED KNOWLEDGE SILOS (Requirement D)
# --------------------------------------------------
ROLE_CONFIG = {
    "BUYER": {
        "identity": "Residential Sales Expert",
        "description": "Expert in home pricing, luxury amenities, and booking procedures.",
        "knowledge": {
            "pricing": "Our residential units are competitively priced. 1BHK starts at ₹45 Lakhs, 2BHK at ₹75 Lakhs, and 3BHK premium units are between ₹1.1Cr and ₹1.4Cr.",
            "emi": "Multiple banking partners (HDFC, ICICI, SBI) offer interest rates starting from 8.25%. A 20% down payment is standard.",
            "project": "Aurora Heights is a sustainable 15-acre development featuring 70% open green space and a luxury clubhouse.",
            "booking": "The reservation process is simple: pay an initial ₹2 Lakhs as a booking amount and submit your KYC documents.",
            "availability": "Current availability: Tower B has limited 2BHKs remaining. Tower C has new 1BHK and 3BHK launches.",
            "location": "Located in the Tech Corridor, with a 5-minute walk to the new Metro terminal for easy city access."
        },
        "banned": ["commission", "payout", "partner portal", "slab", "brokerage fee", "incentive", "partnership term"]
    },
    "CHANNEL_PARTNER": {
        "identity": "Partner Relations Manager",
        "description": "Dedicated lead for business incentives, commissions, and partner conduct.",
        "knowledge": {
            "commission": "Our standard commission slab is 2%. 'Club Elite' partners (5+ bookings) receive 2.5% plus performance bonuses.",
            "payout": "Commissions are processed within 21 days of the buyer's first 10% payment clearance and registration.",
            "partnership": "We offer a 1-year renewable RERA-registered partnership with dedicated relationship manager support.",
            "registration": "Onboarding requires a valid RERA certificate, GST details, and a company profile via the partner portal.",
            "referral": "Lead protection is active for 60 days. All leads must be logged in the PartnerConnect app before arrival.",
            "terms": "Partners must adhere to our zero-tolerance policy for misrepresentation and follow RERA guidelines strictly."
        },
        "banned": ["pricing", "cost", "personal discount", "end-user discount", "booking form", "emi rates", "loan interest"]
    },
    "SITE_VISIT": {
        "identity": "Site Visit Coordinator",
        "description": "Logistics lead for site tours, directions, and scheduling.",
        "knowledge": {
            "location": "Aurora Heights Site Office is located at ITPL Main Road junction. Search 'Aurora Heights' on Maps.",
            "schedule": "Site visits are open 7 days a week from 9:30 AM to 6:30 PM. We recommend early morning slots.",
            "slots": "Currently available slots: 11:00 AM, 2:30 PM, and 4:30 PM today. Shall I reserve one for you?",
            "contact": "Site Tour Lead: Vikram (+91 99000-11223). Reception Desk: +91 80-4555-6677.",
            "shuttle": "A complimentary luxury shuttle runs from the Metro station Gate 2 every 20 minutes for visitors.",
            "amenities": "The tour includes a walk through the sample 2BHK flat, the viewing gallery, and properties Phase 1."
        },
        "banned": ["pricing", "cost", "commission", "payout", "partnership", "emi", "booking", "financing", "loan"]
    },
    "ENQUIRY": {
        "identity": "General Enquiry Specialist",
        "description": "Expert in project overview, developer legacy, and general project features.",
        "knowledge": {
            "project": "Aurora Heights is a flagship 15-acre residential development featuring smart homes and sustainable living.",
            "developer": "Global Realty is an award-winning developer with a legacy of 25 years and over 40 million sq. ft. of space delivered.",
            "location": "Located at the heart of the IT corridor, we offer seamless connectivity to the airport and major business hubs.",
            "features": "Our project includes a 50,000 sq. ft. clubhouse, organic gardens, and a futuristic security system.",
            "contact": "For general queries, you can reach us at 1800-AURORA-INFO or email contact@auroraheights.com.",
            "legacy": "We are known for 'Quality First' construction and have been rated 5-star by independent realty auditors."
        },
        "banned": ["commission", "payout", "partner portal", "slab", "brokerage fee", "incentive", "partnership term", "pricing", "cost", "discount", "emi", "booking", "loan"]
    }
}

# --------------------------------------------------
# SYSTEM ENGINES (Requirement B, C)
# --------------------------------------------------

class BaseAgent:
    def __init__(self, role):
        self.role = role
        self.config = ROLE_CONFIG.get(role, {})
        self.identity = self.config.get("identity", "Assistant")
        self.kb = self.config.get("knowledge", {})
        self.banned = self.config.get("banned", [])

    def guard_query(self, query):
        q = query.lower()
        for word in self.banned:
            if word in q:
                return (
                    f"🛡️ **SECURITY ALERT:** I am authorized to share details only regarding **{', '.join(self.kb.keys())}**. "
                    f"I am strictly restricted from providing information on '{word}'.",
                    True, # violation
                    word
                )
        return None, False, None

    def explain(self, query):
        q = query.lower()
        
        # 1. Exact Match Check
        for topic, info in self.kb.items():
            if topic in q:
                return f"**[{self.identity}]**: {info}"

        # 2. Intelligent AI Expansion (Llama-3 via DuckDuckGo)
        if HAS_LLM:
            try:
                with DDGS() as ddgs:
                    # Inject strict role context
                    system_context = (
                        f"You are the {self.identity} for Aurora Heights. "
                        f"Your expertise is ONLY: {', '.join(self.kb.keys())}. "
                        f"Base your answer on this knowledge: {str(self.kb)}. "
                        f"DO NOT mention anything about {', '.join(self.banned)}. "
                        f"Be professional and clear."
                    )
                    prompt = f"System Context: {system_context}\n\nUser Question: {query}"
                    response = ddgs.chat(prompt, model='llama-3-70b')
                    if response:
                        return f"**[{self.identity}]**: {response}"
            except Exception as e:
                pass

        # 3. Fuzzy Local Fallback
        return (
            f"**[{self.identity}]**: I can provide clear information about **{', '.join(self.kb.keys())}**. "
            "Could you please repeat your question using one of these keywords so I can assist you better?"
        )

# Agent Factories (Requirement B: Dedicated flows)
class BuyerBot(BaseAgent):
    def __init__(self): super().__init__("BUYER")

class PartnerBot(BaseAgent):
    def __init__(self): super().__init__("CHANNEL_PARTNER")

class SiteBot(BaseAgent):
    def __init__(self): super().__init__("SITE_VISIT")

class EnquiryBot(BaseAgent):
    def __init__(self): super().__init__("ENQUIRY")

# --------------------------------------------------
# MASTER ROUTER
# --------------------------------------------------

def route_and_process(role, query):
    if role == "BUYER": bot = BuyerBot()
    elif role == "CHANNEL_PARTNER": bot = PartnerBot()
    elif role == "SITE_VISIT": bot = SiteBot()
    elif role == "ENQUIRY": bot = EnquiryBot()
    else: return "Unknown Role.", False, None

    # Requirement C: Pre-response Guard
    refusal, is_violation, trigger = bot.guard_query(query)
    if is_violation:
        return refusal, True, trigger

    # Process and Return
    response = bot.explain(query)
    return response, False, None

# --------------------------------------------------
# AUDIT & LOOKUP (Requirement A, E)
# --------------------------------------------------
def lookup_role_by_phone(phone):
    if not phone: return "UNKNOWN"
    csv_path = "classified_leads_output.csv"
    if os.path.exists(csv_path):
        with open(csv_path, mode='r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get("Phone") == phone:
                    return row.get("Assigned_Role", "UNKNOWN")
    return "UNKNOWN"

def log_audit(phone, role, query, response, violation):
    log_file = "interaction_audit.json"
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "role": role,
        "query": query,
        "response": response,
        "violation_flag": violation
    }
    
    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            try: logs = json.load(f)
            except: logs = []
            
    logs.append(entry)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=4)

def log_mismatch(phone, stated_role):
    log_file = "interaction_audit.json"
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "phone": phone,
        "event": "ROLE_MISMATCH_REPORTED",
        "current_role": stated_role,
        "violation_flag": True  # Tag as priority for admin review
    }
    
    logs = []
    if os.path.exists(log_file):
        with open(log_file, "r") as f:
            try: logs = json.load(f)
            except: logs = []
            
    logs.append(entry)
    with open(log_file, "w") as f:
        json.dump(logs, f, indent=4)
