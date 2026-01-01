import os
import json
import re
import requests
from dotenv import load_dotenv
from qa_tool import web_search

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
API_KEY = os.getenv("API_KEY")
MODEL = "gpt-oss:20b"


class FakeNewsAgent:
    def __init__(self):
        if not API_KEY:
            raise RuntimeError("API_KEY not set")
        self.headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json",
        }

    # ---------- LLM helper ----------
    def call_llm(self, system_prompt, user_prompt):
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "stream": False,
        }
        r = requests.post(
            f"{API_BASE_URL}/api/chat",
            headers=self.headers,
            json=payload,
            timeout=120,
        )
        r.raise_for_status()
        return r.json()["message"]["content"]

    # ---------- Step 1: Claim extraction ----------
    def extract_claims(self, text, max_claims=5):
        system = (
            "Extract factual, checkable claims from the text.\n"
            "Return ONLY a JSON array of strings.\n"
            "Ignore opinions or emotional language."
        )
        out = self.call_llm(system, text)

        try:
            claims = json.loads(out)
            return claims[:max_claims]
        except Exception:
            sentences = re.split(r"(?<=[.!?])\s+", text)
            return sentences[:max_claims]

    # ---------- Step 2: Verify one claim ----------
    def verify_claim(self, claim):
        search_results = web_search(claim, max_results=5)

        context = ""
        for r in search_results:
            context += f"- {r.get('title','')}: {r.get('body','')}\n"

        system = (
            "You are verifying a factual claim using provided evidence.\n"
            "Classify the claim as one of:\n"
            "- Supported\n"
            "- Contradicted\n"
            "- Insufficient evidence\n\n"
            "Explain briefly why.\n"
            "Return JSON with fields: verdict, explanation."
        )

        user = f"Claim:\n{claim}\n\nEvidence:\n{context}"

        out = self.call_llm(system, user)

        try:
            return json.loads(out)
        except Exception:
            return {
                "verdict": "Insufficient evidence",
                "explanation": "Unable to parse verification result.",
            }

    # ---------- Step 3: Aggregate ----------
    def aggregate_results(self, results):
        counts = {"Supported": 0, "Contradicted": 0, "Insufficient evidence": 0}
        for r in results:
            counts[r["verdict"]] += 1

        if counts["Contradicted"] > 0:
            credibility = "LOW"
        elif counts["Supported"] > 0 and counts["Insufficient evidence"] == 0:
            credibility = "HIGH"
        else:
            credibility = "UNCERTAIN"

        return credibility, counts

    # ---------- Main ----------
    def run(self, text):
        claims = self.extract_claims(text)

        results = []
        for claim in claims:
            verification = self.verify_claim(claim)
            results.append({
                "claim": claim,
                "verdict": verification["verdict"],
                "explanation": verification["explanation"]
            })

        credibility, counts = self.aggregate_results(results)
        
        return {
            "overall_credibility": credibility,
            "summary": counts,
            "claims": results
        }


# ---------- For testing in terminal ----------
def main():
    agent = FakeNewsAgent()
    print("Fake News Verification Agent (Terminal Mode)")
    print("Type 'quit' to exit.")
    print("-" * 50)

    while True:
        text = input("\nInput article or claim:\n> ")
        if text.lower() in {"quit", "exit"}:
            break

        result = agent.run(text)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
