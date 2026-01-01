const output = document.getElementById("output");
const modeSelect = document.getElementById("modeSelect");
const newsModeDiv = document.getElementById("newsMode");
const qaModeDiv = document.getElementById("qaMode");

// ---- Update UI based on mode ----
function updateModeUI() {
  const mode = getMode();

  if (mode === "qa") {
    newsModeDiv.classList.add("hidden");
    qaModeDiv.classList.remove("hidden");
    output.textContent = "Enter a question to get started.";
  } else {
    qaModeDiv.classList.add("hidden");
    newsModeDiv.classList.remove("hidden");
    output.textContent = "Select an article or paste text to analyze.";
  }
}

// Run once on load
updateModeUI();

// Listen for mode changes
modeSelect.addEventListener("change", updateModeUI);


// ---- Get selected mode ----
function getMode() {
  const select = document.getElementById("modeSelect");
  return select ? select.value : "news";
}


// ---- Get selected language ----
function getLanguage() {
  const select = document.getElementById("languageSelect");
  return select.value;
}

// ---- Ask question ----
document.getElementById("askQuestion").onclick = async () => {
  const question = document.getElementById("qaInput").value;

  if (!question.trim()) {
    output.textContent = "Please enter a question.";
    return;
  }

  output.textContent = "Searching and generating answer...";

  let language = getLanguage();
  if (language === "auto") {
    language = /[\u4e00-\u9fa5]/.test(question) ? "zh-TW" : "en";
  }

  await verifyText(question, language);
};


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
          const mode = getMode();
          if (mode === "qa") {
            output.textContent = "Answering question...\nSearching if needed...";
          } else {
            output.textContent = "Extracting claims...\nSearching for evidence...\nAnalyzing credibility...";
          }

          //output.textContent = "Extracting claims...\nSearching for evidence...\nAnalyzing credibility...\n\nThis may take 30-60 seconds...";
          
          // 自動偵測語言
          let language = getLanguage();
          if (language === "auto") {
            language = response.language || "en";
          }
          
          // 傳遞文本和發布日期
          await verifyText(response.text, language, response.publishDate);
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
async function verifyText(text, language = "zh-TW", publishDate = null) {
  try {
    const mode = getMode();
    const payload = { mode, text, language };
    
    // 如果有發布日期，加入 payload
    if (publishDate) {
      payload.publishDate = publishDate;
    }
    
    const res = await fetch("http://127.0.0.1:5000/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
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
    
    //output.textContent = renderResult(data);
    output.innerHTML = renderHTMLResult(data);

  } catch (err) {
    output.textContent = `Cannot connect to server.\n\nPlease make sure:\n1. fake_news_server.py is running\n2. Server is on http://127.0.0.1:5000\n\nError: ${err.message}`;
  }
}

// ---- Output layout ----
function renderResult(result) {
  // 根據不同模式渲染不同格式
  if (result.mode === "news_article") {
    // === 新聞文章模式 ===
    let text = `TITLE: ${result.title}\n`;
    text += "=".repeat(45) + "\n";
    text += `Title Verdict: ${result.title_verdict}\n\n`;
    text += `Title Explanation:\n${result.title_explanation}\n\n`;
    text += "=".repeat(45) + "\n\n";

    text += "VERIFIABLE DETAILS:\n";
    text += "-".repeat(45) + "\n\n";
    
    result.details.forEach((d, i) => {
      text += `${i + 1}. ${d.detail}\n`;
      text += `   Search query: ${d.search_query || 'N/A'}\n`;
      text += `   Evidence count: ${d.evidence_count || 0} sources\n`;
      
      // 顯示證據分類統計
      if (d.evidence_breakdown) {
        text += `   Evidence breakdown: Support ${d.evidence_breakdown.support || 0} | Refute ${d.evidence_breakdown.refute || 0} | Irrelevant ${d.evidence_breakdown.irrelevant || 0}\n`;
      }
      
      text += `   Verdict: ${d.verdict}\n`;
      text += `   Explanation:\n`;
      
      // 確保 explanation 是字串
      const explanation = String(d.explanation || 'No explanation provided');
      text += `      ${explanation.replace(/\n/g, '\n      ')}\n\n`;
    });

    text += "=".repeat(30) + "\n";
    text += "SUMMARY:\n";
    if (result.detail_summary) {
      for (const [key, value] of Object.entries(result.detail_summary)) {
        text += `- ${key}: ${value}\n`;
      }
    }

    return text;
    
  } else if (result.mode === "qa") {
    return `Q: ${result.question}\n\nA: ${result.answer}`;
  } else {
    // === 一般文字模式 (claim-based) ===
    let text = `Overall Credibility: ${result.overall_credibility}\n`;
    text += "=".repeat(45) + "\n";
    text += `Summary: ${result.summary}\n\n`;
    text += "=".repeat(45) + "\n\n";
    
    text += "CLAIMS:\n";
    text += "-".repeat(45) + "\n\n";
    
    result.claims.forEach((c, i) => {
      text += `${i + 1}. ${c.claim}\n`;
      text += `   Search query: ${c.search_query || 'N/A'}\n`;
      text += `   Evidence count: ${c.evidence_count || 0} sources\n`;
      
      // 顯示證據分類統計
      if (c.evidence_breakdown) {
        text += `   Evidence breakdown: Support ${c.evidence_breakdown.support || 0} | Refute ${c.evidence_breakdown.refute || 0} | Irrelevant ${c.evidence_breakdown.irrelevant || 0}\n`;
      }
      
      text += `   Verdict: ${c.verdict}\n`;
      text += `   Explanation:\n`;
      
      // 確保 explanation 是字串
      const explanation = String(c.explanation || 'No explanation provided');
      text += `      ${explanation.replace(/\n/g, '\n      ')}\n\n`;
    });
    
    return text;
  }
}

function renderHTMLResult(result) {

  // News Article Mode
  if (result.mode === "news_article") {
    const verdictClass =
      result.title_verdict === "CREDIBLE"
        ? "verdict-credible"
        : result.title_verdict === "MISLEADING"
        ? "verdict-misleading"
        : "verdict-uncertain";

    let html = `
      <h3>📰 News Title</h3>
      <p>${result.title}</p>

      <h3>⚖️ Title Verdict</h3>
      <p class="${verdictClass}">
        ${result.title_verdict}
      </p>

      <h3>📝 Explanation</h3>
      <p>${result.title_explanation}</p>

      <h3>🔍 Verifiable Details</h3>
    `;

    result.details.forEach((d, i) => {
      html += `
        <div class="detail-box">
          <h4>${i + 1}. ${d.detail}</h4>
          <p><b>Verdict:</b> ${d.verdict}</p>
          <p><b>Evidence:</b> ${d.evidence_count || 0} sources</p>
          <p>${d.explanation}</p>
        </div>
      `;
    });

    if (result.detail_summary) {
      html += `<h3>📊 Summary</h3><ul>`;
      for (const [key, value] of Object.entries(result.detail_summary)) {
        html += `<li>${key}: ${value}</li>`;
      }
      html += `</ul>`;
    }

    if (result.temporal_warnings) {
      html += `<h3>⚠️ Time Warnings</h3><ul>`;
      result.temporal_warnings.forEach(w => {
        html += `<li>${w}</li>`;
      });
      html += `</ul>`;
    }

    return html;
  }

  // QA Mode
  if (result.mode === "qa") {
    return `
      <h3>👤 You</h3>
      <p>${result.question}</p>

      <h3>🧠 Agent</h3>
      <p>${result.answer}</p>
    `;
  }

  // Plain text mode
  let html = `
    <h3>Overall Credibility</h3>
    <p>${result.overall_credibility}</p>

    <h3>Summary</h3>
    <p>${result.summary}</p>

    <h3>Claims</h3>
  `;

  result.claims.forEach((c, i) => {
    html += `
      <div class="detail-box">
        <h4>${i + 1}. ${c.claim}</h4>
        <p><b>Verdict:</b> ${c.verdict}</p>
        <p><b>Evidence:</b> ${c.evidence_count || 0} sources</p>
        <p>${c.explanation}</p>
      </div>
    `;
  });

  return html;
}
