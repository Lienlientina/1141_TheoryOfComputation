"""
Evidence Processor
處理證據搜尋、過濾、分析和驗證
"""
from llm_helpers import call_llm, parse_json_response
from qa_tool import web_search
from temporal_checker import (
    extract_time_from_claim,
    extract_time_from_evidence,
    normalize_time_expression,
    is_temporally_relevant
)
from datetime import datetime
from urllib.parse import urlparse

# 官方來源域名列表
OFFICIAL_DOMAINS = {
    # 政府域名（各國）
    '.gov',         # 美國政府
    '.gov.tw',      # 台灣政府
    '.gov.uk',      # 英國政府
    '.go.jp',       # 日本政府
    '.gov.cn',      # 中國政府
    '.gov.au',      # 澳洲政府
    '.gouv.fr',     # 法國政府
    '.gc.ca',       # 加拿大政府
    '.gob.mx',      # 墨西哥政府
    '.gob.es',      # 西班牙政府
    '.gov.sg',      # 新加坡政府
    '.go.kr',       # 韓國政府
    
    # 教育機構
    '.edu',         # 美國教育機構
    '.edu.tw',      # 台灣教育機構
    '.ac.uk',       # 英國學術機構
    '.ac.jp',       # 日本學術機構
    '.edu.au',      # 澳洲教育機構
}

INTERNATIONAL_ORGS = [
    'un.org',           # 聯合國
    'who.int',          # 世界衛生組織
    'imf.org',          # 國際貨幣基金
    'worldbank.org',    # 世界銀行
    'wto.org',          # 世界貿易組織
    'oecd.org',         # 經濟合作暨發展組織
    'unesco.org',       # 聯合國教科文組織
]


def get_source_credibility_tier(url):
    """
    判斷來源可信度等級
    
    Args:
        url: 證據來源 URL
    
    Returns:
        "official": 政府機構或國際組織
        "standard": 一般來源
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # 移除 www. 前綴
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # 檢查政府域名後綴
        for suffix in OFFICIAL_DOMAINS:
            if domain.endswith(suffix):
                return "official"
        
        # 檢查國際組織
        for org in INTERNATIONAL_ORGS:
            if org in domain:
                return "official"
        
        return "standard"
    except:
        return "standard"


def generate_search_query(claim, search_mode='general'):
    """
    從claim中提取最佳搜尋關鍵字
    
    Args:
        claim: 待驗證的主張
        search_mode: 'official' (官方來源) 或 'general' (一般搜尋)
    
    Returns:
        優化後的搜尋查詢字串
    """
    system = (
        "Extract the most important keywords for fact-checking this claim.\n"
        "CRITICAL: Keep the query in the SAME LANGUAGE as the claim.\n"
        "- If claim is in Chinese → return Chinese keywords\n"
        "- If claim is in English → return English keywords\n\n"
        "Return ONLY 2-4 key terms that would help find relevant evidence.\n"
        "Focus on:\n"
        "- Names of people, organizations, places\n"
        "- Specific events or policies\n"
        "- Dates or time periods\n"
        "- Core factual assertions\n\n"
        "CRITICAL for location keywords:\n"
        "- Keep COMPLETE place names with country/region prefix (e.g., '日本東北' not just '東北', 'Taiwan Taipei' not just 'Taipei')\n"
        "- NEVER drop the country/region name before a location\n"
        "- Examples: '日本岩手縣' ✓, '岩手縣' ✗ | 'Japan Iwate' ✓, 'Iwate' ✗\n\n"
        "Remove: opinions, adjectives, unnecessary words.\n"
        "Return as a simple search query string (not JSON)."
    )
    
    try:
        query = call_llm(system, f"Claim: {claim}")
        # 清理回應，移除引號和多餘空白
        query = query.strip().strip('"').strip("'")
        
        # 強制加入地域關鍵字（如果claim中有但query中沒有）
        location_keywords = ['台北', '臺北', '台中', '臺中', '台南', '臺南', '高雄', '台灣', '臺灣', 'Taipei', 'Taichung', 'Tainan', 'Kaohsiung', 'Taiwan']
        for loc in location_keywords:
            if loc in claim and loc not in query:
                query = f"{loc} {query}"
                break
        
        # 官方來源模式：添加 site: 過濾器
        if search_mode == 'official':
            official_sites = [
                "site:.gov", "site:.gov.tw", "site:.gov.uk", "site:.go.jp",
                "site:.edu", "site:.edu.tw", "site:.ac.uk",
                "site:who.int", "site:un.org", "site:imf.org", "site:worldbank.org"
            ]
            site_filter = " OR ".join(official_sites)
            query = f"{query} ({site_filter})"
        
        return query if len(query) > 0 else claim
    except Exception:
        # 備用：直接使用claim
        return claim


def is_evidence_potentially_relevant(claim, evidence_title, evidence_body):
    """
    快速預過濾：只過濾明顯錯誤地點的證據
    
    Args:
        claim: 待驗證的主張
        evidence_title: 證據標題
        evidence_body: 證據內容
    
    Returns:
        True 保留，False 過濾掉
    """
    evidence_text = (evidence_title + " " + evidence_body)
    
    # 檢測claim中的台灣相關地點
    taiwan_locations = ['台北', '臺北', '台中', '臺中', '台南', '臺南', '高雄', '台灣', '臺灣', '新北']
    has_taiwan_location = any(loc in claim for loc in taiwan_locations)
    
    # 如果claim提到台灣地點，但證據提到明顯不相關的國外地點，則過濾
    if has_taiwan_location:
        irrelevant_locations = [
            'San Diego', 'Beijing', '北京', 'Shanghai', '上海', 
            'Hong Kong', '香港', 'Tokyo', '東京', 'Seoul', '首爾',
            'Singapore', '新加坡', 'London', 'New York', 'Paris'
        ]
        # 檢查是否有明顯衝突的地點（同時出現在證據中但不在claim中）
        for irrelevant_loc in irrelevant_locations:
            if irrelevant_loc in evidence_text and irrelevant_loc not in claim:
                return False
    
    # 預設：保留證據給LLM分析（寬鬆策略）
    return True


def analyze_evidence_stance(claim, evidence_title, evidence_body):
    """
    判斷單個證據與claim的關係：支持/反駁/無關
    
    Args:
        claim: 待驗證的主張
        evidence_title: 證據標題
        evidence_body: 證據內容
    
    Returns:
        "support" | "refute" | "irrelevant"
    """
    system = (
        "Analyze if the evidence supports, refutes, or is irrelevant to the claim.\n"
        "Return ONLY one word: support / refute / irrelevant\n"
        "Do not explain, just return the single word."
    )
    
    user = f"Claim: {claim}\n\nEvidence:\nTitle: {evidence_title}\nContent: {evidence_body}"
    
    try:
        result = call_llm(system, user).strip().lower()
        # 標準化回應
        if "support" in result:
            return "support"
        elif "refute" in result or "contradict" in result:
            return "refute"
        else:
            return "irrelevant"
    except Exception:
        return "irrelevant"


def verify_claim(claim, language="zh-TW", temporal_check=True, claim_reference_date=None):
    """
    驗證單個主張
    
    Args:
        claim: 待驗證的主張
        language: 回應語言
        temporal_check: 是否進行時間相關性檢查（預設開啟）
        claim_reference_date: claim 的發布日期（用於時間檢查），None 則使用今天
    
    Returns:
        {
            "verdict": "Supported" | "Contradicted" | "Insufficient evidence" | "Temporal mismatch",
            "explanation": str,
            "evidence_count": int,
            "search_query": str,
            "evidence_breakdown": {"support": int, "refute": int, "irrelevant": int},
            "temporal_warning": str (optional),
            "source_type": "official" | "general" (optional),
            "authoritative_override": bool (optional)
        }
    """
    # 初始化預設值，避免變數未定義
    search_query = claim
    valid_results = []
    
    # 提取 claim 中的時間資訊（如果啟用時間檢查）
    claim_time_expression = None
    claim_time_info = None
    temporal_warnings = []
    
    if temporal_check:
        try:
            claim_time_expression = extract_time_from_claim(claim)
            if claim_time_expression:
                print(f"  -> 發現時間描述: {claim_time_expression}")
                # 使用 claim 的發布日期作為參考點
                ref_date = claim_reference_date or datetime.now().isoformat()
                claim_time_info = normalize_time_expression(claim_time_expression, ref_date)
                print(f"  -> 標準化時間: {claim_time_info.get('parsed_date')} ({claim_time_info.get('time_type')})")
        except Exception as e:
            print(f"  Warning: Time extraction failed ({e})")

    # === 第一階段：搜尋官方來源 ===
    print(f"\n  [階段1] 搜尋官方來源...")
    official_query = generate_search_query(claim, search_mode='official')
    print(f"  -> 官方搜尋關鍵字: {official_query}")
    
    try:
        official_results = web_search(official_query, max_results=5)
        print(f"  -> 找到 {len(official_results)} 個搜尋結果")
        
        # 過濾出真正的官方來源
        verified_official = []
        for result in official_results:
            if get_source_credibility_tier(result.get('href', '')) == 'official':
                verified_official.append(result)
        
        if verified_official:
            print(f"  [官方來源] 找到 {len(verified_official)} 個官方來源，直接採信")
            
            # 分析第一個官方來源的立場
            first_official = verified_official[0]
            stance = analyze_evidence_stance(
                claim,
                first_official.get('title', ''),
                first_official.get('body', '')
            )
            
            official_url = first_official.get('href', 'N/A')
            
            if stance == 'support':
                return {
                    "verdict": "Supported",
                    "explanation": f"🏛️ 官方來源證實：{official_url}\n\n{first_official.get('body', '')[:300]}...",
                    "evidence_count": len(verified_official),
                    "search_query": official_query,
                    "source_type": "official",
                    "authoritative_override": True,
                    "evidence_breakdown": {
                        "support": len(verified_official),
                        "refute": 0,
                        "irrelevant": 0,
                        "official_sources": verified_official
                    }
                }
            elif stance == 'refute':
                return {
                    "verdict": "Contradicted",
                    "explanation": f"🏛️ 官方來源反駁：{official_url}\n\n{first_official.get('body', '')[:300]}...",
                    "evidence_count": len(verified_official),
                    "search_query": official_query,
                    "source_type": "official",
                    "authoritative_override": True,
                    "evidence_breakdown": {
                        "support": 0,
                        "refute": len(verified_official),
                        "irrelevant": 0,
                        "official_sources": verified_official
                    }
                }
            else:
                print(f"  [官方來源] 官方來源不相關，繼續一般搜尋")
        else:
            print(f"  [官方來源] 未找到可信官方來源")
    except Exception as e:
        print(f"  [官方來源] 搜尋失敗: {e}")
    
    # === 第二階段：一般搜尋 ===
    print(f"\n  [階段2] 進行一般搜尋...")
    valid_results = []
    
    try:
        # 先生成更精準的搜尋查詢
        search_query = generate_search_query(claim, search_mode='general')
        print(f"  -> 搜尋關鍵字: {search_query}")
    except Exception as e:
        print(f"  Warning: Search query generation failed ({e}), using original claim")
        search_query = claim
    
    try:
        # 搜尋至少10個結果
        search_results = web_search(search_query, max_results=10)
        
        # 過濾有效結果
        valid_results = [r for r in search_results if r.get('title') and r.get('body')]
    except Exception as e:
        print(f"  Error: Search failed ({e})")
        return {
            "verdict": "Insufficient evidence",
            "explanation": f"Search error: {str(e)}",
            "evidence_count": 0,
            "search_query": search_query
        }
    
    # 即使少於3個也繼續分析，但會在結果中註明
    evidence_warning = ""
    if len(valid_results) < 3:
        evidence_warning = f"[Warning] Only found {len(valid_results)} evidence source(s). Recommended: at least 3 sources."
    
    if len(valid_results) == 0:
        return {
            "verdict": "Insufficient evidence",
            "explanation": "No relevant evidence found. Cannot verify this claim.",
            "evidence_count": 0,
            "search_query": search_query,
            "evidence_breakdown": {"support": 0, "refute": 0, "irrelevant": 0}
        }

    # 分析每個證據的立場
    print(f"  → Analyzing stance of {len(valid_results)} evidence sources...")
    
    # 先預過濾明顯不相關的結果
    filtered_results = []
    filtered_out = 0
    for r in valid_results:
        if is_evidence_potentially_relevant(claim, r.get('title', ''), r.get('body', '')):
            filtered_results.append(r)
        else:
            filtered_out += 1
    
    if filtered_out > 0:
        print(f"     Pre-filtered {filtered_out} obviously irrelevant sources")
    
    # 時間相關性過濾（如果啟用）
    if temporal_check and claim_time_info and claim_time_info.get('time_type') != 'no_time_reference':
        temporally_filtered = []
        temporal_filtered_out = 0
        
        for r in filtered_results:
            # 從證據中提取時間表達式和發布日期
            evidence_time_data = extract_time_from_evidence(r.get('body', ''))
            evidence_time_expr = evidence_time_data.get('time_expression')
            evidence_pub_date = evidence_time_data.get('publish_date')
            
            if evidence_time_expr:
                # 決定參考點：優先使用證據的發布日期，否則使用今天
                if evidence_pub_date:
                    try:
                        # 嘗試標準化證據發布日期
                        normalized_pub_date = normalize_time_expression(evidence_pub_date, datetime.now().isoformat())
                        reference_date = normalized_pub_date.get('parsed_date', datetime.now().isoformat())
                        print(f"     使用證據發布日期作為參考: {reference_date}")
                    except:
                        reference_date = datetime.now().isoformat()
                        print(f"     證據發布日期標準化失敗，使用今天作為參考")
                else:
                    reference_date = datetime.now().isoformat()
                
                # 標準化證據時間（使用證據發布日期或今天作為參考點）
                evidence_time_info = normalize_time_expression(evidence_time_expr, reference_date)
                
                # 檢查時間相關性（僅標記，不過濾）
                temporal_result = is_temporally_relevant(claim_time_info, evidence_time_info)
                
                r['temporal_status'] = temporal_result['status']
                r['temporal_info'] = temporal_result
                
                # 保留所有證據，只標記時間狀態
                temporally_filtered.append(r)
                
                if not temporal_result['is_relevant']:
                    temporal_warnings.append(
                        f"⚠️ 證據 '{r.get('title', '')[:50]}...' 的時間 ({temporal_result['evidence_date']}) "
                        f"不符合 claim 的時間範圍 ({temporal_result['expected_range']})，但仍保留供分析"
                    )
            else:
                # 無法提取時間的證據保留
                r['temporal_status'] = 'no_constraint'
                temporally_filtered.append(r)
        
        # 移除 temporal_filtered_out 相關邏輯（不再過濾證據）
        filtered_results = temporally_filtered
    
    # === Step 5: 分析每個證據 ===    # 如果過濾後沒有結果，返回證據不足
    if len(filtered_results) == 0:
        return {
            "verdict": "Insufficient evidence",
            "explanation": f"All {len(valid_results)} search results were irrelevant to the claim (wrong location/topic).",
            "evidence_count": len(valid_results),
            "search_query": search_query,
            "evidence_breakdown": {"support": 0, "refute": 0, "irrelevant": len(valid_results)}
        }
    
    categorized_evidence = {
        "support": [],
        "refute": [],
        "irrelevant": []
    }
    
    for r in filtered_results:
        title = r.get('title', '')
        body = r.get('body', '')
        stance = analyze_evidence_stance(claim, title, body)
        
        evidence_item = {
            "title": title,
            "snippet": body[:200] + "..." if len(body) > 200 else body,
            "href": r.get('href', '')
        }
        
        # 加入時間資訊（如果有）
        if 'temporal_info' in r:
            evidence_item['temporal_info'] = r['temporal_info']
        
        categorized_evidence[stance].append(evidence_item)
    
    support_count = len(categorized_evidence["support"])
    refute_count = len(categorized_evidence["refute"])
    irrelevant_count = len(categorized_evidence["irrelevant"])
    
    # 加上被預過濾掉的數量
    total_irrelevant = irrelevant_count + filtered_out
    
    print(f"     Support: {support_count}, Refute: {refute_count}, Irrelevant: {total_irrelevant} (pre-filtered: {filtered_out})")
    
    # 建立分類後的證據摘要給LLM
    context = ""
    
    if categorized_evidence["support"]:
        context += "=== Supporting Evidence ===\n"
        for i, ev in enumerate(categorized_evidence["support"], 1):
            context += f"{i}. [{ev['title']}]\n   {ev['snippet']}\n\n"
    
    if categorized_evidence["refute"]:
        context += "=== Refuting Evidence ===\n"
        for i, ev in enumerate(categorized_evidence["refute"], 1):
            context += f"{i}. [{ev['title']}]\n   {ev['snippet']}\n\n"
    
    if categorized_evidence["irrelevant"]:
        context += f"=== Irrelevant Evidence ({total_irrelevant} sources total, {filtered_out} pre-filtered) ===\n(Not shown for brevity)\n\n"

    # 根據語言設定回應語言
    language_instruction = ""
    if language == "zh-TW":
        language_instruction = "CRITICAL: You MUST respond in Traditional Chinese (繁體中文). All explanations must be in Traditional Chinese."
    elif language == "en":
        language_instruction = "CRITICAL: You MUST respond in English. All explanations must be in English."
    else:
        language_instruction = "CRITICAL: You MUST respond in Traditional Chinese (繁體中文). All explanations must be in Traditional Chinese."

    system = (
        f"{language_instruction}\n\n"
        "You are verifying a factual claim using categorized evidence.\n"
        f"Evidence summary:\n"
        f"- Supporting evidence: {support_count}\n"
        f"- Refuting evidence: {refute_count}\n"
        f"- Irrelevant evidence: {total_irrelevant} (filtered out)\n\n"
        "Based on the categorized evidence, classify the claim as:\n"
        "- Supported: If supporting evidence is strong and refuting evidence is weak/absent\n"
        "- Contradicted: If refuting evidence is strong and supporting evidence is weak/absent\n"
        "- Insufficient evidence: If evidence is too weak, contradictory, or mostly irrelevant\n\n"
        "In your explanation, mention:\n"
        "1. Key supporting/refuting evidence\n"
        "2. Why you reached this conclusion\n"
        "3. Any uncertainty or conflicting information\n\n"
        f"{evidence_warning}\n"
        f"IMPORTANT: Your entire response (verdict + explanation) must be in the language specified above.\n"
        "Return JSON with fields: verdict, explanation."
    )

    user = f"Claim:\n{claim}\n\n{context}"

    out = call_llm(system, user)

    try:
        result = parse_json_response(out)
        result['evidence_count'] = len(valid_results)
        result['search_query'] = search_query
        result['evidence_breakdown'] = {
            "support": support_count,
            "refute": refute_count,
            "irrelevant": total_irrelevant
        }
        if evidence_warning:
            result['explanation'] = evidence_warning + "\n\n" + result['explanation']
        
        # 加入時間警告（如果有）
        if temporal_warnings:
            result['temporal_warning'] = temporal_warnings[0]  # 只顯示第一個警告
        
        return result
    except Exception as e:
        return {
            "verdict": "Insufficient evidence",
            "explanation": f"Unable to parse verification result. {evidence_warning}",
            "evidence_count": len(valid_results),
            "search_query": search_query,
            "evidence_breakdown": {
                "support": support_count,
                "refute": refute_count,
                "irrelevant": total_irrelevant
            }
        }
