"""
groq_classifier.py — LLM-Based Classification via Groq API
Uses few-shot prompting to classify documents into departments.

Why Groq?
- Fastest LLM inference available (GroqChip hardware)
- Free tier generous enough for this use case
- LLaMA 3.1 understands business document context very well

Why few-shot prompting?
- Zero-shot works but few-shot gives the LLM examples to anchor on
- Much better accuracy with business document terminology
- Consistent JSON output format
"""

import json
import re
from groq import Groq
from tenacity import retry, stop_after_attempt, wait_exponential
from backend.core.config import settings
from backend.core.logger import logger
from backend.core.exceptions import GroqAPIException

# Initialise Groq client
client = Groq(api_key=settings.GROQ_API_KEY)

# ── System prompt ──────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert document classification system for enterprise document management.

Your job is to classify business documents into exactly one of these departments:
1. Finance
2. Human Resources
3. Legal & Regulatory
4. Licensing & Compliance
5. IT & Technology
6. Operations

Classification rules:
- Finance: invoices, budgets, financial statements, audit reports, tax documents, purchase orders, expense reports
- Human Resources: employment contracts, payslips, leave applications, performance reviews, onboarding, job descriptions, HR policies
- Legal & Regulatory: contracts, NDAs, court orders, legal notices, regulatory submissions, dispute letters, terms of service
- Licensing & Compliance: licenses, permits, certifications, compliance checklists, policy documents, accreditations
- IT & Technology: system specifications, software agreements, security policies, incident reports, technical manuals, IT contracts
- Operations: standard operating procedures (SOPs), maintenance logs, supply chain docs, vendor agreements, logistics, facility management

You must respond with ONLY valid JSON in this exact format:
{
  "department": "Finance",
  "confidence": 0.92,
  "explanation": "This document contains invoice numbers, payment terms, and VAT calculations typical of Finance department documents."
}

Rules:
- confidence must be a float between 0.0 and 1.0
- explanation must be 1-2 sentences explaining WHY you chose this department
- department must be exactly one of the 6 listed above
- Do not include any text outside the JSON object
"""

# ── Few-shot examples ──────────────────────────────────────────
FEW_SHOT_EXAMPLES = [
    {
        "role": "user",
        "content": "Classify this document:\n\nINVOICE #INV-2024-0042\nBill To: Acme Corp\nItem: Professional Services - Q1 2024\nAmount: $15,000.00\nGST: $1,500.00\nTotal Due: $16,500.00\nPayment Terms: Net 30"
    },
    {
        "role": "assistant",
        "content": '{"department": "Finance", "confidence": 0.97, "explanation": "This is clearly an invoice with billing details, GST calculations, and payment terms, which are standard Finance department documents."}'
    },
    {
        "role": "user",
        "content": "Classify this document:\n\nEMPLOYMENT CONTRACT\nThis agreement is between TechCorp Ltd and John Smith.\nPosition: Senior Software Engineer\nSalary: $95,000 per annum\nStart Date: 1 February 2024\nProbation Period: 3 months\nAnnual Leave: 20 days"
    },
    {
        "role": "assistant",
        "content": '{"department": "Human Resources", "confidence": 0.95, "explanation": "This employment contract specifies position, salary, and leave entitlements, which are core Human Resources documents."}'
    },
    {
        "role": "user",
        "content": "Classify this document:\n\nSOFTWARE LICENSE AGREEMENT\nThis Software License Agreement is entered into between DataSoft Inc and the Licensee.\nLicense Type: Enterprise\nUsers: Up to 500\nRenewal: Annual\nCompliance: SOC2, ISO27001 required"
    },
    {
        "role": "assistant",
        "content": '{"department": "Licensing & Compliance", "confidence": 0.91, "explanation": "This software license agreement with compliance requirements falls under Licensing & Compliance department."}'
    },
]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def classify_with_groq(text: str) -> dict:
    """
    Send document text to Groq LLM for classification.
    
    Returns dict with:
    - department: str
    - confidence: float (0.0 - 1.0)
    - explanation: str
    
    Retries up to 3 times with exponential backoff on API errors.
    """
    logger.info(f"Sending {len(text)} chars to Groq for classification")

    messages = FEW_SHOT_EXAMPLES + [
        {
            "role": "user",
            "content": f"Classify this document:\n\n{text}"
        }
    ]

    try:
        response = client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[{"role": "system", "content": SYSTEM_PROMPT}] + messages,
            temperature=0.1,       # Low temp = consistent, deterministic output
            max_tokens=200,        # JSON response is short
        )

        raw_response = response.choices[0].message.content.strip()
        logger.debug(f"Groq raw response: {raw_response}")

        result = _parse_response(raw_response)
        logger.info(f"Groq classified as: {result['department']} ({result['confidence']:.2f})")
        return result

    except Exception as e:
        logger.error(f"Groq API error: {e}")
        raise GroqAPIException(f"Groq classification failed: {str(e)}")


def _parse_response(raw: str) -> dict:
    """
    Parse the JSON response from Groq.
    Handles cases where the model wraps JSON in markdown code blocks.
    """
    # Strip markdown code blocks if present
    cleaned = re.sub(r'```json\s*|\s*```', '', raw).strip()

    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError:
        # Try to extract JSON from mixed text
        match = re.search(r'\{.*\}', cleaned, re.DOTALL)
        if match:
            data = json.loads(match.group())
        else:
            raise GroqAPIException(f"Could not parse Groq response as JSON: {raw}")

    # Validate required fields
    required = ["department", "confidence", "explanation"]
    for field in required:
        if field not in data:
            raise GroqAPIException(f"Missing field '{field}' in Groq response")

    # Validate department is one of the allowed ones
    if data["department"] not in settings.DEPARTMENTS:
        logger.warning(f"Unknown department from Groq: {data['department']} — will use ML fallback")
        data["confidence"] = 0.0  # Force ML fallback

    # Clamp confidence to 0-1
    data["confidence"] = max(0.0, min(1.0, float(data["confidence"])))

    return data
