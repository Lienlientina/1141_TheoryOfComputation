// Get all text content from the tab
function extractPageText() {
  const elementsToRemove = document.querySelectorAll(
    "script, style, noscript"
  );
  elementsToRemove.forEach(el => el.remove());

  const text = document.body.innerText || "";
  return text.trim();
}

// Listen for popup request
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "EXTRACT_PAGE_TEXT") {
    const text = extractPageText();
    sendResponse({ text });
  }
});
