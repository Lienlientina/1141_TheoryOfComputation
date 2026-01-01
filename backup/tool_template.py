"""
工具模板 - 用於創建新功能的標準模板
遵循模組化設計原則：Pure Functions + Open WebUI Wrapper

使用說明：
1. 複製此檔案並重新命名（如 calculator_tool.py）
2. 實作核心pure function
3. 在Tools類別中新增wrapper方法
4. 編寫測試函數
5. 在qa_agent.py中匯入使用
"""

from typing import Dict, Any, List, Optional


# ============================================
# 第一層：Pure Functions（核心邏輯）
# ============================================

def core_function(input_data: str, **kwargs) -> Any:
    """
    核心功能的pure function
    
    設計原則：
    - 無副作用（不修改全域狀態）
    - 輸入輸出明確
    - 可獨立測試
    - 不依賴外部類別或物件
    
    Args:
        input_data: 主要輸入參數
        **kwargs: 可選參數
        
    Returns:
        處理結果（具體類型根據功能定義）
        
    Example:
        >>> result = core_function("test input")
        >>> print(result)
    """
    try:
        # TODO: 實作核心邏輯
        result = f"Processing: {input_data}"
        return result
    except Exception as e:
        print(f"Error in core_function: {e}")
        return None


def format_result(data: Any) -> str:
    """
    格式化輸出結果的pure function
    
    分離格式化邏輯的好處：
    - 可以獨立修改輸出格式
    - 易於新增不同的格式化方式（JSON, plain text, etc.）
    - 核心邏輯保持簡潔
    
    Args:
        data: 待格式化的資料
        
    Returns:
        格式化後的字串
    """
    if not data:
        return "No data available"
    
    # TODO: 實作格式化邏輯
    formatted = f"Result: {data}"
    return formatted


# ============================================
# 第二層：Open WebUI Compatible Tools Class
# ============================================

class Tools:
    """
    Open WebUI相容的工具包裝類別
    
    設計模式：Adapter Pattern
    - 將pure functions包裝成Open WebUI可識別的格式
    - 每個方法必須包含完整的docstring（Open WebUI會讀取）
    - 參數使用type hints
    """
    
    def __init__(self):
        """初始化工具類別（如需設定可在此新增）"""
        pass
    
    def tool_function(
        self,
        input_data: str,
        option: str = "default"
    ) -> str:
        """
        工具功能的Open WebUI介面
        
        重要：此docstring會顯示在Open WebUI中，需清楚說明功能
        
        :param input_data: 主要輸入參數的說明
        :param option: 可選參數的說明（預設值：default）
        :return: 回傳值說明
        
        Example usage in Open WebUI:
        User: "請使用工具處理這段文字"
        Agent: [呼叫此工具] -> 回傳處理結果
        """
        # 呼叫核心pure function
        result = core_function(input_data, option=option)
        
        # 格式化輸出
        formatted = format_result(result)
        
        return formatted
    
    def another_tool_function(
        self,
        query: str
    ) -> str:
        """
        另一個工具功能（可選）
        
        如果同一類功能有多個變體，可以新增多個wrapper方法
        例如：web_search_qa, wikipedia_search, get_current_info
        
        :param query: 查詢參數
        :return: 查詢結果
        """
        # TODO: 實作另一個功能
        result = f"Processing query: {query}"
        return result


# ============================================
# 第三層：獨立測試函數
# ============================================

def test_tool():
    """
    獨立測試函數
    
    好處：
    - 不依賴pytest等框架
    - 可直接執行此檔案測試
    - 快速驗證功能是否正常
    """
    print("=" * 50)
    print("Testing Pure Functions")
    print("=" * 50)
    
    # 測試核心函數
    print("\n1. Testing core_function:")
    result = core_function("test input", option="test")
    print(f"   Result: {result}")
    
    # 測試格式化函數
    print("\n2. Testing format_result:")
    formatted = format_result(result)
    print(f"   Formatted: {formatted}")
    
    print("\n" + "=" * 50)
    print("Testing Tools Class")
    print("=" * 50)
    
    # 測試Tools wrapper
    tools = Tools()
    
    print("\n3. Testing tool_function:")
    output = tools.tool_function("test data", option="custom")
    print(f"   Output: {output}")
    
    print("\n4. Testing another_tool_function:")
    output2 = tools.another_tool_function("test query")
    print(f"   Output: {output2}")
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("=" * 50)


# ============================================
# 主程式入口（用於獨立執行測試）
# ============================================

if __name__ == "__main__":
    """
    直接執行此檔案時執行測試
    
    用法：python tool_template.py
    """
    test_tool()


# ============================================
# 整合到qa_agent.py的範例程式碼
# ============================================

"""
在qa_agent.py中使用此工具：

1. 匯入pure functions（推薦）：
   from tool_template import core_function, format_result
   
   # 在agent中直接呼叫
   result = core_function(user_input)
   formatted = format_result(result)

2. 匯入Tools類別（用於Open WebUI）：
   from tool_template import Tools as TemplateTools
   
   # 建立實例
   template_tool = TemplateTools()
   output = template_tool.tool_function(user_input)

3. 工具選擇邏輯：
   def _should_use_template_tool(self, question):
       '''判斷是否需要使用此工具'''
       keywords = ['關鍵詞1', '關鍵詞2', 'keyword1']
       return any(keyword in question.lower() for keyword in keywords)
"""
