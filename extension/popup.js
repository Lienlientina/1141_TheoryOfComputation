const output = document.getElementById("output");

// ---- Get selected language ----
function getLanguage() {
  const select = document.getElementById("languageSelect");
  return select.value;
}

// ---- Analyze current tab ----
document.getElementById("analyzePage").onclick = async () => {
  output.textContent = "Reading page content...";

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

  chrome.scripting.executeScript(
    {
      target: { tabId: tab.id },
      files: ["content.js"]
    },
    () => {
      chrome.tabs.sendMessage(
        tab.id,
        { action: "EXTRACT_PAGE_TEXT" },
        async (response) => {
          if (!response || !response.text) {
            output.textContent = "Failed to extract page text.";
            return;
          }
          
          output.textContent = "Extracting claims...\nSearching for evidence...\nAnalyzing credibility...\n\nThis may take 30-60 seconds...";
          
          // 自動偵測語言
          let language = getLanguage();
          if (language === "auto") {
            language = response.language || "en";
          }
          
          await verifyText(response.text, language);
        }
      );
    }
  );
};

// ---- Verify user input text ----
document.getElementById("verifyManual").onclick = async () => {
  const text = document.getElementById("manualInput").value;
  if (!text.trim()) {
    output.textContent = "Please enter some text.";
    return;
  }
  
  output.textContent = "Analyzing text...\nThis may take 30-60 seconds...";
  
  let language = getLanguage();
  if (language === "auto") {
    // 簡單判斷：有中文字就是中文，否則英文
    language = /[\u4e00-\u9fa5]/.test(text) ? "zh-TW" : "en";
  }
  
  await verifyText(text, language);
};

// ---- Send text to local agent server ----
async function verifyText(text, language = "zh-TW") {
  try {
    const res = await fetch("http://127.0.0.1:5000/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text, language })
    });

    if (!res.ok) {
      output.textContent = `Server error: ${res.status}\n\nPlease check if fake_news_server.py is running.`;
      return;
    }

    const data = await res.json();
    
    if (data.error) {
      output.textContent = `Error: ${data.error}`;
      return;
    }
    
    output.textContent = renderResult(data);
  } catch (err) {
    output.textContent = `Cannot connect to server.\n\nPlease make sure:\n1. fake_news_server.py is running\n2. Server is on http://127.0.0.1:5000\n\nError: ${err.message}`;
  }
}

// ---- Output layout ----
function renderResult(result) {
  let text = `Overall credibility: ${result.overall_credibility}\n\n`;

  text += "Claim verification:\n";
  text += "=".repeat(50) + "\n\n";
  
  result.claims.forEach((c, i) => {
    text += `${i + 1}. ${c.claim}\n`;
    text += `   Search query: ${c.search_query || 'N/A'}\n`;
    text += `   Evidence count: ${c.evidence_count || 0} 個來源\n`;
    text += `   Verdict: ${c.verdict}\n`;
    text += `   Explanation:\n`;
    
    // 確保 explanation 是字串
    const explanation = String(c.explanation || 'No explanation provided');
    text += `      ${explanation.replace(/\n/g, '\n      ')}\n\n`;
  });

  text += "=".repeat(50) + "\n";
  text += "Summary:\n";
  for (const [key, value] of Object.entries(result.summary)) {
    text += `- ${key}: ${value}\n`;
  }

  return text;
}
