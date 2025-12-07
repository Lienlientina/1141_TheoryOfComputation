"""
QA Tool for Open WebUI - Web Search and Question Answering
This tool enables the LLM to search the web and retrieve relevant information.
"""

from ddgs import DDGS
from typing import Optional
import json


class Tools:
    """
    Open WebUI Tool class for web search QA functionality.
    """
    
    def __init__(self):
        """Initialize the QA Tool"""
        self.max_results = 5
        
    def web_search_qa(
        self, 
        query: str,
        max_results: Optional[int] = 5
    ) -> str:
        """
        Search the web for information related to the user's question.
        This tool uses DuckDuckGo to find relevant web pages and extracts key information.
        
        :param query: The search query or question from the user
        :param max_results: Maximum number of search results to return (default: 5)
        :return: Formatted search results with titles, snippets, and URLs
        """
        
        try:
            # Perform web search using DuckDuckGo
            print(f"🔍 Searching for: {query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    query,
                    max_results=max_results
                ))
            
            if not results:
                return f"⚠️ No search results found for: {query}"
            
            # Format search results
            formatted_results = self._format_search_results(results)
            
            return formatted_results
            
        except Exception as e:
            error_msg = f"❌ Search error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def _format_search_results(self, results: list) -> str:
        """
        Format search results into a readable string.
        
        :param results: List of search result dictionaries
        :return: Formatted string with search results
        """
        
        formatted = "📊 Web Search Results:\n\n"
        
        for idx, result in enumerate(results, 1):
            title = result.get('title', 'No title')
            snippet = result.get('body', 'No description')
            url = result.get('href', 'No URL')
            
            formatted += f"[{idx}] {title}\n"
            formatted += f"    {snippet}\n"
            formatted += f"    🔗 {url}\n\n"
        
        formatted += "\n💡 Please use the above information to answer the user's question."
        
        return formatted
    
    def wikipedia_search(
        self, 
        query: str,
        max_results: Optional[int] = 3
    ) -> str:
        """
        Search Wikipedia for information.
        
        :param query: The search query
        :param max_results: Maximum number of results (default: 3)
        :return: Wikipedia search results
        """
        
        try:
            # Add "wikipedia" to the query for better results
            wiki_query = f"{query} site:wikipedia.org"
            
            print(f"📚 Searching Wikipedia for: {query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    wiki_query,
                    max_results=max_results
                ))
            
            if not results:
                return f"⚠️ No Wikipedia results found for: {query}"
            
            formatted_results = self._format_search_results(results)
            
            return formatted_results
            
        except Exception as e:
            error_msg = f"❌ Wikipedia search error: {str(e)}"
            print(error_msg)
            return error_msg
    
    def get_current_info(self, query: str) -> str:
        """
        Get current/latest information about a topic.
        Useful for news, current events, or time-sensitive queries.
        
        :param query: The query about current information
        :return: Latest search results
        """
        
        try:
            # Add time-related keywords to get recent results
            current_query = f"{query} latest news 2025"
            
            print(f"📰 Searching for current info: {query}")
            
            with DDGS() as ddgs:
                results = list(ddgs.text(
                    current_query,
                    max_results=5
                ))
            
            if not results:
                return f"⚠️ No current information found for: {query}"
            
            formatted_results = "🆕 Latest Information:\n\n"
            
            for idx, result in enumerate(results, 1):
                title = result.get('title', 'No title')
                snippet = result.get('body', 'No description')
                url = result.get('href', 'No URL')
                
                formatted_results += f"[{idx}] {title}\n"
                formatted_results += f"    {snippet}\n"
                formatted_results += f"    🔗 {url}\n\n"
            
            formatted_results += "\n💡 This is the most recent information available."
            
            return formatted_results
            
        except Exception as e:
            error_msg = f"❌ Error getting current info: {str(e)}"
            print(error_msg)
            return error_msg


# Test function for standalone usage
def test_qa_tool():
    """Test the QA Tool functionality"""
    
    print("=" * 60)
    print("Testing QA Tool")
    print("=" * 60)
    
    tools = Tools()
    
    # Test 1: Basic web search
    print("\n🧪 Test 1: Basic Web Search")
    result1 = tools.web_search_qa("What is the capital of Taiwan?")
    print(result1)
    
    # Test 2: Wikipedia search
    print("\n🧪 Test 2: Wikipedia Search")
    result2 = tools.wikipedia_search("Machine Learning")
    print(result2)
    
    # Test 3: Current information
    print("\n🧪 Test 3: Current Information")
    result3 = tools.get_current_info("Taiwan president 2025")
    print(result3)
    
    print("\n" + "=" * 60)
    print("✅ All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    # Run tests if executed directly
    test_qa_tool()
