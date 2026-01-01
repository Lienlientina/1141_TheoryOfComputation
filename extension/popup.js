const output = document.getElementById("output");

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
          await verifyText(response.text);
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
  await verifyText(text);
};

// ---- Send text to local agent server ----
async function verifyText(text) {
  output.textContent = "Verifying with AI agent...";

  try {
    const res = await fetch("http://127.0.0.1:5000/verify", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    const data = await res.json();
    output.textContent = renderResult(data);
  } catch (err) {
    output.textContent = "Error connecting to local agent server.";
  }
}

// ---- Output layout ----
function renderResult(result) {
  let text = `Overall credibility: ${result.overall_credibility}\n\n`;

  text += "Claim verification:\n";
  result.claims.forEach((c, i) => {
    text += `${i + 1}. ${c.claim}\n`;
    text += `   Verdict: ${c.verdict}\n`;
    text += `   Explanation: ${c.explanation}\n\n`;
  });

  text += "Summary:\n";
  for (const [key, value] of Object.entries(result.summary)) {
    text += `- ${key}: ${value}\n`;
  }

  return text;
}
