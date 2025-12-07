# Agent 基礎設置指南

## 快速開始

### 1. 安裝依賴
```bash
pip install -r requirements.txt
```

### 2. 設置 API Key
編輯 `.env` 檔案，將 `your-api-key-here` 替換為你的實際 API key：
```
API_KEY=你的實際API金鑰
```

### 3. 測試基礎 Agent
```bash
python basic_agent.py
```

## 方法一：使用 Python Agent（最簡單）

運行 `basic_agent.py` 來測試 API 連接：
- 會先檢查可用模型
- 發送測試訊息
- 進入互動模式與 AI 對話

## 方法二：使用 Open WebUI（功能完整）

### 啟動 Open WebUI

**方式 A: 使用環境變數**
```bash
$env:OPENAI_API_BASE_URL="https://api-gateway.netdb.csie.ncku.edu.tw"; $env:OPENAI_API_KEY="你的API金鑰"; open-webui serve
```

**方式 B: 使用配置檔**
確保 `.env` 檔案正確設置後：
```bash
open-webui serve --env-file .env
```

### 訪問介面
打開瀏覽器訪問：`http://localhost:8080`

### 設置 API 連接
1. 進入 Settings > Connections
2. 添加 OpenAI API:
   - API Base URL: `https://api-gateway.netdb.csie.ncku.edu.tw`
   - API Key: 你的 API 金鑰

### 添加自定義工具
1. 進入 Settings > Tools
2. 點擊 "+" 創建新工具
3. 貼上 `openwebui_tools.py` 中的程式碼
4. 保存並在對話中啟用工具

## API 端點說明

根據 Ollama API 文檔，你的 API 支援以下端點：

### 聊天 (Chat)
```
POST /api/chat
Authorization: Bearer <your-api-key>
{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "Hello"}]
}
```

### 生成 (Generate)
```
POST /api/generate
Authorization: Bearer <your-api-key>
{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?"
}
```

### 列出模型 (List Models)
```
GET /api/tags
Authorization: Bearer <your-api-key>
```

## 檔案說明

- `.env` - 環境變數配置（包含 API key）
- `basic_agent.py` - 基礎 Python agent 實作
- `openwebui_tools.py` - Open WebUI 自定義工具範例
- `requirements.txt` - Python 依賴套件

## 進階功能

### 創建更複雜的工具
參考 Open WebUI 文檔：https://docs.openwebui.com/features/plugin/tools/

工具必須實作：
- 類別名稱：`Tools`
- 方法需要有清楚的 docstring
- 參數需要有型別註解

### 串流回應
將 `stream=True` 傳給 chat 方法以獲得即時回應。

## 故障排除

### 連接錯誤
- 確認 API URL 是否正確
- 確認 API key 是否有效
- 檢查網路連接

### 模型不可用
- 使用 `list_models()` 檢查可用模型
- 在請求中使用正確的模型名稱

## 注意事項

⚠️ **不要將 `.env` 檔案提交到版本控制系統**
建議在 `.gitignore` 中添加：
```
.env
__pycache__/
*.pyc
```
