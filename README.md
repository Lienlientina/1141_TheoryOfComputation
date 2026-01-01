# Fake News Verification System - TOC Final Project

假新聞驗證系統，結合 Chrome Extension、Flask 後端與 LLM API，能夠自動檢測新聞文章和陳述的真實性。

## 📋 專案功能

### 核心功能
- ✅ **自動模式偵測**：支援新聞文章和一般文字兩種驗證模式
- ✅ **Chrome Extension**：一鍵檢測網頁新聞真假
- ✅ **智能提取**：從新聞中提取標題和關鍵細節
- ✅ **網路搜尋驗證**：自動搜尋外部證據
- ✅ **官方來源優先**：優先搜尋政府機構和國際組織，直接採信官方證據
- ✅ **證據立場分析**：判斷證據支持/反駁/無關
- ✅ **時間相關性檢查**：防止「舊聞當新聞」的假新聞手法
- ✅ **多語言支援**：繁體中文、英文、自動偵測
- ✅ **模組化架構**：易於擴展新功能

### 驗證模式

#### 模式 A：新聞文章驗證（Title → Details → Evidence）
```
網頁新聞
   ↓
提取 Title（主張）+ Details（支撐細節）
   ↓
對每個 Detail 搜尋外部證據
   ↓
分析證據立場（支持/反駁/無關）
   ↓
彙總判斷 Title 可信度（CREDIBLE/MISLEADING/UNCERTAIN）
```

#### 模式 B：一般文字驗證（Claim-based）
```
用戶輸入文字
   ↓
提取可驗證的 Claims
   ↓
對每個 Claim 搜尋外部證據
   ↓
統計結果（支持/反駁/證據不足）
   ↓
給出總體可信度（HIGH/LOW/UNCERTAIN）
```

---

## 🚀 快速開始

### 1. Clone 專案
```bash
git clone https://github.com/Lienlientina/1141_TheoryOfComputation.git
cd "1141_TheoryOfComputation"
```

### 2. 安裝依賴套件
```bash
pip install -r requirements.txt
```

### 3. 設置 API Key

複製 `.env.example` 為 `.env`：
```bash
copy .env.example .env
```

編輯 `.env` 檔案，填入你的 API Key：
```env
API_BASE_URL=https://api-gateway.netdb.csie.ncku.edu.tw
API_KEY=你的實際API金鑰
```

### 4. 啟動 Flask 後端
```bash
python fake_news_server.py
```

看到以下訊息表示成功：
```
 * Running on http://127.0.0.1:5000
```

### 6. 安裝 Chrome Extension

1. 開啟 Chrome，進入 `chrome://extensions/`
2. 開啟右上角「開發人員模式」
3. 點擊「載入未封裝項目」
4. 選擇專案中的 `extension` 資料夾
5. Extension 安裝完成！

### 7. 開始使用

#### 方式 A：檢測網頁新聞 ⭐
1. 瀏覽任意新聞網站（例如：聯合新聞網、自由時報）
2. 點擊瀏覽器右上角的 Extension 圖標
3. 選擇語言（Auto-detect / English / 繁體中文）
4. 點擊「Analyze Current Page」
5. 等待 30-60 秒，查看驗證結果

#### 方式 B：手動輸入文字驗證
1. 點擊 Extension 圖標
2. 在文字框輸入要驗證的陳述（例如：「台灣2024年GDP成長率5%」）
3. 選擇語言
4. 點擊「Verify Text」
5. 查看驗證結果

---

## 💻 使用方式

### Chrome Extension 使用指南

#### 1. 自動提取網頁內容
Extension 會自動提取：
- 📰 **標題**：`<h1>`, `<title>`, 或 `og:title` meta tag
- 👤 **作者**：`<meta name="author">` 或常見作者選擇器
- 📅 **發布時間**：`<time>` 標籤或日期相關 meta tag
- 📄 **內文**：過濾廣告、導航列、留言後的主要段落

#### 2. 語言選擇
- **Auto-detect**：根據 HTML `lang` 屬性或中文字符自動判斷
- **English**：強制英文回應
- **繁體中文**：強制繁體中文回應

#### 3. 閱讀驗證結果


### 命令列使用（開發/測試）

#### 直接運行 Agent
```bash
python fake_news_agent.py
```

#### 互動式測試
```
Input article or claim:
> Title: 測試標題
> Content: 測試內容...
```

---

## 📁 專案結構（重構後）

```
.
├── extension/                    # Chrome Extension
│   ├── manifest.json            # Extension 配置
│   ├── popup.html               # UI 介面
│   ├── popup.js                 # UI 邏輯
│   └── content.js               # 網頁內容提取
│
├── fake_news_server.py          # Flask 後端 API
├── fake_news_agent.py           # 主 Agent（協調器）⭐
│
├── llm_helpers.py               # LLM API 和 JSON 解析
├── extractors.py                # Title/Details/Claims 提取
├── evidence_processor.py        # 證據搜尋、過濾、驗證
├── temporal_checker.py          # 時間相關性檢查 ⏰
│
├── qa_tool.py                   # 網路搜尋工具
├── qa_agent.py                  # QA Agent（舊功能保留）
│
├── .env.example                 # API 配置範本
├── .gitignore                   # Git 忽略規則
├── requirements.txt             # Python 依賴套件
└── README.md                    # 本說明文件
```

### 模組說明

#### 核心模組

**`fake_news_agent.py`** (311 行) - 主控 Agent ⭐
- 自動模式偵測（新聞 vs 一般文字）
- 協調三層驗證流程
- 時間驗證整合（接收新聞發布日期）
- 彙總並判斷標題可信度
- CLI 測試介面

**`llm_helpers.py`** (86 行) - LLM 工具
- `call_llm()` - 統一的 LLM API 調用
- `parse_json_response()` - 清理 markdown 並解析 JSON
- 處理 API 錯誤和超時

**`extractors.py`** (154 行) - 提取器
- `extract_title_and_details()` - 從新聞提取標題和關鍵細節（不提取純時間資訊）
- `extract_claims()` - 從一般文字提取可驗證主張
- 強制 LLM 只從文本提取，不編造資訊

**`evidence_processor.py`** (544 行) - 證據處理器
- `get_source_credibility_tier()` - 判斷來源可信度等級（官方/一般）
- `generate_search_query()` - 優化搜尋關鍵字（保留完整地名，支援官方來源模式）
- `is_evidence_potentially_relevant()` - 預過濾不相關證據
- `analyze_evidence_stance()` - 判斷證據立場
- `verify_claim()` - 兩階段驗證流程（優先搜尋官方來源，未找到則一般搜尋）

**`temporal_checker.py`** (360 行) - 時間相關性檢查 ⏰
- `normalize_time_expression()` - LLM-based 時間標準化（支援多語言）
- `extract_time_from_claim()` - 從 claim 提取時間表達式
- `extract_time_from_evidence()` - 從證據提取時間表達式和發布日期
- `calculate_time_range()` - 計算時間範圍（specific_recent/relative_recent/relative_past）
- `is_temporally_relevant()` - 判斷證據時間是否在 claim 時間範圍內

#### Extension 模組

**`extension/content.js`** (232 行) - 內容提取
- `extractTitle()` - 提取標題（多種策略）
- `extractAuthor()` - 提取作者
- `extractPublishDate()` - 提取發布時間並標準化為 ISO 格式
- `extractMainContent()` - 提取主要內容（過濾噪音）
- `isNoiseElement()` - 判斷元素是否為廣告/導航

**`extension/popup.js`** (164 行) - UI 邏輯
- `getLanguage()` - 讀取語言選擇
- `verifyText()` - 發送驗證請求到後端（包含 publishDate）
- `renderResult()` - 根據模式顯示結果
- 處理時間警告顯示

**`fake_news_server.py`** (50 行) - Flask API
- `/verify` POST - 驗證端點
- 接收 `{text, language, publishDate}`
- 返回驗證結果 JSON（包含時間警告）

---

---

## 🏗️ 系統架構

### 整體架構
```
Chrome Extension (UI)
        ↓ HTTP POST
Flask Server (:5000)
        ↓
fake_news_agent.py (主控)
        ↓
   ┌────┴────┐
   ↓         ↓
extractors  evidence_processor
   ↓         ↓
   └─→ llm_helpers ←─┘
        ↓
   LLM API (gpt-oss:20b)
        ↓
   DuckDuckGo Search
```

### 流程圖
![System Workflow DAG](DAG.png)

### 三層驗證流程（新聞模式）

```
1. 提取層 (Extraction)
   ├─ 輸入：網頁新聞全文
   ├─ 處理：extractors.extract_title_and_details()
   └─ 輸出：Title + 2-4 個 Details

2. 驗證層 (Verification)
   ├─ 對每個 Detail：
   │   ├─ 生成搜尋查詢 (generate_search_query)
   │   ├─ 搜尋外部證據 (web_search)
   │   ├─ 預過濾不相關證據 (is_evidence_potentially_relevant)
   │   ├─ 分析證據立場 (analyze_evidence_stance)
   │   └─ 判定 Detail 結果 (Supported/Contradicted/Insufficient)
   └─ 輸出：每個 Detail 的驗證結果

3. 判斷層 (Judgment)
   ├─ 輸入：所有 Detail 的驗證結果
   ├─ 處理：judge_title_from_details()
   └─ 輸出：Title 可信度 (CREDIBLE/MISLEADING/UNCERTAIN)
```


## 🔧 技術細節

### LLM Prompt 設計

#### 提取器 Prompt 策略
```python
# 強制只從文本提取，不編造資訊
"CRITICAL: Extract ONLY from the provided text"
"DO NOT add information from your knowledge"
"Details must be EXACT quotes or paraphrases from the CONTENT section"
```

#### 驗證器 Prompt 策略
```python
# 多語言支援
"CRITICAL: You MUST respond in Traditional Chinese (繁體中文)"

# 證據分類
"- Supported: If supporting evidence is strong"
"- Contradicted: If refuting evidence is strong"
"- Insufficient evidence: If evidence is too weak"
```

### 證據過濾機制

**預過濾（Pre-filtering）**：
```python
# 快速過濾明顯不相關的證據（減少 LLM API 調用）
if "台北" in claim and "San Diego" in evidence:
    return False  # 過濾掉
```

**LLM 立場分析**：
```python
# 對保留的證據進行深度分析
stance = analyze_evidence_stance(claim, evidence)
# 返回：support / refute / irrelevant
```

### 搜尋查詢優化

```python
# 原始 claim
"台北市跨年晚會動員警民力超過3,000人"

# 經過 generate_search_query() 優化
"台北 跨年晚會 警民力 3000"  # 去除贅字，保留關鍵詞

# 自動加入地域關鍵字
if "台北" in claim and "台北" not in query:
    query = "台北 " + query
```

---

## 🛠️ 開發指南

### 添加新功能範例

#### 1. 官方來源優先搜尋（已實作）✅

**功能說明**：優先搜尋並採信政府機構和國際組織的證據

**實作細節**：
```python
# evidence_processor.py

# 1. 官方來源定義
OFFICIAL_DOMAINS = {
    '.gov', '.gov.tw', '.go.jp', '.gov.uk',  # 各國政府
    '.edu', '.edu.tw', '.ac.uk',              # 教育機構
}
INTERNATIONAL_ORGS = ['un.org', 'who.int', 'imf.org', 'worldbank.org']

# 2. 判斷來源可信度
get_source_credibility_tier(url)  # → "official" 或 "standard"

# 3. 兩階段搜尋策略
# 階段1: 官方來源搜尋（使用 site: 過濾器）
official_query = "台灣GDP (site:.gov.tw OR site:.gov OR site:who.int)"
# 找到官方來源 → 直接採信，結束
# 階段2: 未找到官方來源 → 進行一般搜尋
```

**支援的官方來源**：
- 政府機構：`.gov.tw` (台灣), `.go.jp` (日本), `.gov.uk` (英國) 等
- 教育機構：`.edu.tw`, `.ac.uk`, `.edu.au` 等
- 國際組織：UN, WHO, IMF, World Bank, OECD 等

**結果顯示**：
```
🏛️ 官方來源證實：行政院主計總處 (gov.tw)
說明：根據官方統計資料確認...

註：因找到官方來源，未進行其他來源搜尋
```

**優勢**：
- 提高驗證可信度（政府和國際組織權威性高）
- 節省搜尋時間（找到官方來源即停止）
- 減少 LLM API 調用（只分析 1-2 個官方來源）

---

#### 2. 其他擴展範例

創建 `example_module.py`：
```python
def example_function():
    """範例功能"""
    pass
```

### 測試新模組

```python
# test_example.py
from example_module import example_function

def test_example():
    result = example_function()
    assert result is not None
```

---

## 📊 效能優化

### 已實施的優化

1. **預過濾機制**
   - 在 LLM 分析前先快速過濾明顯不相關的證據
   - 減少 LLM API 調用次數（降低延遲和成本）

2. **搜尋查詢優化**
   - 提取關鍵詞，移除贅字
   - 自動加入地域關鍵字提高搜尋準確度

3. **官方來源優先**
   - 優先搜尋政府和國際組織
   - 找到官方來源即停止，節省搜尋時間

4. **模組化載入**
   - 只在需要時 import 模組
   - 減少啟動時間

### 未來可優化項目

- [ ] **並行處理**：同時驗證多個 Details
- [ ] **快取機制**：重複查詢直接返回快取結果
- [ ] **批次 LLM 請求**：一次處理多個 claim
- [ ] **漸進式回應**：先顯示部分結果，再補充完整驗證

---

## ⚠️ 注意事項與限制

### API 使用限制
- **速率限制**：LLM API 可能有 QPS 限制
- **超時設定**：目前設定 120 秒，複雜驗證可能超時
- **Token 限制**：單次請求不能超過模型的 context window

### 搜尋限制
- **DuckDuckGo 限制**：無 API Key，有速率限制
- **搜尋品質**：依賴搜尋引擎結果品質
- **語言限制**：中文查詢可能返回較少結果

### 驗證準確度
- **LLM 判斷**：立場分析依賴 LLM 理解能力
- **證據品質**：搜尋結果可能包含不可靠來源
- **時效性**：無法驗證實時事件（搜尋引擎索引延遲）

### 安全性
- **API Key 保護**：
  - ✅ `.env` 已加入 `.gitignore`
  - ❌ 不要在程式碼中硬編碼 API Key
  - ❌ 不要將 `.env` 上傳到 GitHub

- **輸入驗證**：
  - Extension 只提取 DOM 內容，不執行腳本
  - Flask 後端應加入輸入長度限制（TODO）

---

## 🎯 未來擴展計畫

### 短期目標
- [x] 模組化重構
- [x] 多語言支援
- [x] 證據立場分析
- [x] 時間相關性檢查（防止舊聞當新聞）
- [x] 官方來源優先搜尋
- [ ] 錯誤處理改進

### 中期目標
- [ ] 並行驗證提升速度
- [ ] 結果快取機制
- [ ] 用戶反饋系統（標記錯誤判斷）
- [ ] 驗證歷史記錄

### 長期目標
- [ ] 支援更多語言（日文、韓文）
- [ ] 圖片和影片事實查核
- [ ] 與事實查核組織 API 整合
- [ ] 機器學習模型輔助判斷

---

## 🔧 系統需求

- Python 3.8+
- 網路連接
- LLM API Key（由課程提供）

---

## ⚠️ 注意事項

1. **API Key 安全**
---

## 🔧 系統需求

- **Python**: 3.8+
- **網路連接**: 需要連接外網進行搜尋
- **瀏覽器**: Google Chrome 或 Chromium-based 瀏覽器
- **LLM API Key**: 由課程提供

---

## 📞 疑難排解

### 常見問題

#### Q1: Extension 無法連接後端
```
錯誤訊息：Cannot connect to server
```
**解決方案**：
1. 確認 `fake_news_server.py` 正在運行
2. 檢查 Flask 是否在 `http://127.0.0.1:5000`
3. 查看瀏覽器 Console 的錯誤訊息

#### Q2: LLM API 超時
```
錯誤訊息：Request timeout after 120s
```
**解決方案**：
1. 檢查網路連接
2. 確認 API Key 正確
3. 可以在 `llm_helpers.py` 中調整 timeout 參數

#### Q3: 搜尋結果全部被過濾
```
輸出：Pre-filtered 10 obviously irrelevant sources
```
**解決方案**：
1. 檢查 claim 中的地點關鍵字
2. `evidence_processor.py` 的預過濾邏輯可能太嚴格
3. 調整 `is_evidence_potentially_relevant()` 的邏輯

#### Q4: Extension 提取不到內容
```
輸出：Failed to extract page text
```
**解決方案**：
1. 某些網站有反爬蟲機制
2. 檢查網頁是否為動態載入（React/Vue SPA）
3. 嘗試在 `content.js` 中調整選擇器

#### Q5: 驗證結果全是「證據不足」
```
所有 Details 都返回：Insufficient evidence
```
**解決方案**：
1. 檢查搜尋關鍵字是否合理
2. 可能是搜尋語言不匹配（中文 claim 用英文搜）
3. 嘗試手動搜尋看是否有相關結果

---

## 📖 參考資源

### 專案相關
- [GitHub Repository](https://github.com/Lienlientina/1132_TheoryOfComputation)
- [Chrome Extension 開發文檔](https://developer.chrome.com/docs/extensions/)
- [Flask 官方文檔](https://flask.palletsprojects.com/)

### API 相關
- [Ollama API 文檔](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [DuckDuckGo Search API](https://pypi.org/project/duckduckgo-search/)

### 事實查核參考
- [台灣事實查核中心](https://tfc-taiwan.org.tw/)
- [Snopes](https://www.snopes.com/) - 國際知名事實查核網站
- [FactCheck.org](https://www.factcheck.org/)

---

## 📝 更新日誌

### Version 3.0 (2026-01-02) - 合併 QA Agent
- ✨ 整合 QA Agent 與新聞驗證 Agent 至單一系統（多 Agent 架構）
- ✨ 新增「模式切換」機制（News Verification / Question Answering）

### Version 2.2 (2026-01-02) - 官方來源優先
- ✨ 新增兩階段搜尋策略：優先搜尋官方來源
- ✨ 支援各國政府域名和國際組織（.gov.tw, .go.jp, who.int 等）
- ✨ 找到官方來源直接採信，節省搜尋時間
- ✨ `get_source_credibility_tier()` 判斷來源可信度
- ✨ `generate_search_query()` 支援官方來源模式（site: 過濾器）
- 🎯 提高驗證準確度和效率
- 📊 evidence_processor.py 擴展至 544 行

### Version 2.1 (2026-01-01) - 時間相關性檢查
- ✨ 新增 temporal_checker.py 模組（360 行）
- ✨ LLM-based 時間標準化（支援多語言相對時間）
- ✨ 時間範圍計算與相關性判斷
- ✨ Extension 提取並傳遞新聞發布日期
- ✨ 證據時間使用證據自己的發布日期作為參考點
- 🎯 防止「舊聞當新聞」的假新聞手法
- ⚙️ 時間檢查預設為標記模式（不過濾證據）

### Version 2.0 (2025-12-30) - 重構與擴展
- ✨ 模組化重構（4個獨立模組）
- ✨ 新增 Chrome Extension 支援
- ✨ 三層驗證架構（Title→Details→Evidence）
- ✨ 多語言支援（中文/英文/自動偵測）
- ✨ 證據立場分析（support/refute/irrelevant）
- 🐛 修復 LLM 回應 markdown 解析問題
- 🐛 修復預過濾過於嚴格的問題
- 🐛 修復地名關鍵字保留問題（「日本東北」vs「東北」）
- 📝 加強 prompt 防止 LLM 編造資訊
- 📝 防止提取純時間資訊作為 detail

### Version 1.0 (2025-12) - 初始版本
- ✅ 基礎 QA Agent 功能
- ✅ 網路搜尋整合
- ✅ LLM API 串接

---

**⭐ 如果這個專案對你有幫助，請給個 Star！**

