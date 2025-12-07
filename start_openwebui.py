"""
Open WebUI 配置腳本 - 通過環境變數設置 API
"""
import os
import subprocess
import sys

# API 配置
API_BASE_URL = "https://api-gateway.netdb.csie.ncku.edu.tw"
API_KEY = "e3476d6b1a370fe7f4b78bdfea9a4d75f4c2fe9166db005f651504c5a274c48e"

def setup_and_run():
    """設置環境變數並啟動 Open WebUI"""
    
    print("設置 Open WebUI 環境變數...")
    #print("=" * 60)
    
    # 設置環境變數
    env = os.environ.copy()
    
    # Ollama API 配置（Open WebUI 會自動檢測）
    env['OLLAMA_BASE_URL'] = API_BASE_URL
    
    # OpenAI API 配置
    env['OPENAI_API_BASE_URL'] = API_BASE_URL
    env['OPENAI_API_KEY'] = API_KEY
    
    # 其他配置
    env['ENABLE_OLLAMA_API'] = 'true'
    env['WEBUI_AUTH'] = 'false'  # 關閉登入要求（僅本地測試用）
    
    print(f"✅ OLLAMA_BASE_URL = {API_BASE_URL}")
    print(f"✅ OPENAI_API_BASE_URL = {API_BASE_URL}")
    print(f"✅ API Key 已設置")
    #print("=" * 60)
    print("\n啟動 Open WebUI...")
    print("訪問地址: http://localhost:8080")
    print("停止服務: 按 Ctrl+C\n")
    
    try:
        # 啟動 Open WebUI
        subprocess.run(['open-webui', 'serve'], env=env)
    except KeyboardInterrupt:
        print("\n\nOpen WebUI 已停止")
    except Exception as e:
        print(f"\n錯誤: {e}")
        print("\n請確認已安裝 open-webui: pip install open-webui")

if __name__ == "__main__":
    setup_and_run()
