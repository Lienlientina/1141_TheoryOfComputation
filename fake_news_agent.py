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
    def extract_claims(self, text, max_claims=5, language="zh-TW"):
        # 根據語言設定回應語言
        language_instruction = ""
        if language == "zh-TW":
            language_instruction = "請用繁體中文提取並表達這些主張。"
        elif language == "en":
            language_instruction = "Please extract and express these claims in English."
        else:
            language_instruction = "請用繁體中文提取並表達這些主張。"
        
        system = (
            "Extract factual, checkable claims from the text.\n"
            "Return ONLY a JSON array of strings.\n"
            "Ignore opinions or emotional language.\n"
            f"{language_instruction}"
        )
        out = self.call_llm(system, text)

        try:
            claims = json.loads(out)
            return claims[:max_claims]
        except Exception:
            sentences = re.split(r"(?<=[.!?])\s+", text)
            return sentences[:max_claims]

    # ---------- Step 2a: Generate search query ----------
    def generate_search_query(self, claim):
        """從claim中提取最佳搜尋關鍵字"""
        system = (
            "Extract the most important keywords for fact-checking this claim.\n"
            "Return ONLY 2-4 key terms that would help find relevant evidence.\n"
            "Focus on:\n"
            "- Names of people, organizations, places\n"
            "- Specific events or policies\n"
            "- Dates or time periods\n"
            "- Core factual assertions\n\n"
            "Remove: opinions, adjectives, unnecessary words.\n"
            "Return as a simple search query string (not JSON)."
        )
        
        try:
            query = self.call_llm(system, f"Claim: {claim}")
            # 清理回應，移除引號和多餘空白
            query = query.strip().strip('"').strip("'")
            return query if len(query) > 0 else claim
        except Exception:
            # 備用：直接使用claim
            return claim

    # ---------- Step 2b: Verify one claim ----------
    def verify_claim(self, claim, language="zh-TW"):
        # 初始化預設值，避免變數未定義
        search_query = claim
        valid_results = []
        
        try:
            # 先生成更精準的搜尋查詢
            search_query = self.generate_search_query(claim)
            print(f"  → 搜尋關鍵字: {search_query}")
        except Exception as e:
            print(f"  警告: 搜尋關鍵字生成失敗 ({e})，使用原claim")
            search_query = claim
        
        try:
            # 搜尋至少10個結果
            search_results = web_search(search_query, max_results=10)
            
            # 過濾有效結果
            valid_results = [r for r in search_results if r.get('title') and r.get('body')]
        except Exception as e:
            print(f"  錯誤: 搜尋失敗 ({e})")
            return {
                "verdict": "Insufficient evidence",
                "explanation": f"搜尋過程發生錯誤：{str(e)}",
                "evidence_count": 0,
                "search_query": search_query
            }
        
        # 即使少於3個也繼續分析，但會在結果中註明
        evidence_warning = ""
        if len(valid_results) < 3:
            evidence_warning = f"[警告] 僅找到{len(valid_results)}個證據來源（建議至少3個），判斷可能不夠全面。"
        
        if len(valid_results) == 0:
            return {
                "verdict": "Insufficient evidence",
                "explanation": "完全找不到相關證據，無法驗證此主張。",
                "evidence_count": 0,
                "search_query": search_query
            }

        # 建立證據列表
        context = ""
        for i, r in enumerate(valid_results, 1):
            context += f"{i}. [{r.get('title','')}]\n   {r.get('body','')}\n\n"

        # 根據語言設定回應語言
        language_instruction = ""
        if language == "zh-TW":
            language_instruction = "請用繁體中文回答。"
        elif language == "en":
            language_instruction = "Please respond in English."
        else:
            language_instruction = "請用繁體中文回答。"  # 預設

        system = (
            "You are verifying a factual claim using provided evidence.\n"
            f"You have {len(valid_results)} sources of evidence.\n"
            "Analyze ALL provided evidence carefully and comprehensively.\n\n"
            "Classify the claim as one of:\n"
            "- Supported: 證據明確支持此主張\n"
            "- Contradicted: 證據明確反駁此主張\n"
            "- Insufficient evidence: 證據不足、互相矛盾、或與主張無關\n\n"
            "In your explanation, include:\n"
            "1. 有幾個證據支持/反駁/無關\n"
            "2. 主要發現是什麼\n"
            "3. 為何做出此判斷\n\n"
            f"{evidence_warning}\n\n"
            f"{language_instruction}\n"
            "Return JSON with fields: verdict, explanation."
        )

        user = f"Claim to verify:\n{claim}\n\nEvidence from {len(valid_results)} sources:\n{context}"

        out = self.call_llm(system, user)

        try:
            result = json.loads(out)
            result['evidence_count'] = len(valid_results)
            result['search_query'] = search_query
            if evidence_warning:
                result['explanation'] = evidence_warning + "\n\n" + result['explanation']
            return result
        except Exception as e:
            return {
                "verdict": "Insufficient evidence",
                "explanation": f"無法解析驗證結果。{evidence_warning}",
                "evidence_count": len(valid_results),
                "search_query": search_query
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
    def run(self, text, language="zh-TW"):
        print("Step 1: 提取Claims...")
        claims = self.extract_claims(text, language=language)
        print(f"找到 {len(claims)} 個claims\n")

        results = []
        for i, claim in enumerate(claims, 1):
            print(f"Step 2.{i}: 驗證 Claim {i}/{len(claims)}")
            print(f"  Claim: {claim[:80]}...")
            verification = self.verify_claim(claim, language=language)
            results.append({
                "claim": claim,
                "verdict": verification["verdict"],
                "explanation": verification["explanation"],
                "evidence_count": verification.get("evidence_count", 0),
                "search_query": verification.get("search_query", "")
            })
            print(f"  Verdict: {verification['verdict']} ({verification.get('evidence_count', 0)} 個證據)\n")

        credibility, counts = self.aggregate_results(results)
        
        print(f"Step 3: 彙整結果")
        print(f"  整體可信度: {credibility}")
        print(f"  統計: {counts}\n")
        
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
