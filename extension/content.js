// ============================================
// 智能文章內容擷取
// ============================================

// 提取標題
function extractTitle() {
  const selectors = [
    'h1',
    '.article-title',
    '.post-title',
    '.entry-title',
    '[class*="headline"]',
    '[class*="title"]',
    'header h1',
    'article h1'
  ];
  
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element && element.textContent.trim().length > 10) {
      return element.textContent.trim();
    }
  }
  
  // 備用：使用頁面標題
  return document.title.split('|')[0].split('-')[0].trim();
}

// 提取作者
function extractAuthor() {
  const selectors = [
    '[rel="author"]',
    '.author',
    '.byline',
    '.author-name',
    '[class*="author"]',
    '[itemprop="author"]',
    'meta[name="author"]'
  ];
  
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) {
      const content = element.getAttribute('content') || element.textContent;
      if (content && content.trim().length > 0) {
        return content.trim();
      }
    }
  }
  
  return null;
}

// 提取發布日期
function extractPublishDate() {
  const selectors = [
    'time[datetime]',
    '[itemprop="datePublished"]',
    '.publish-date',
    '.post-date',
    '.entry-date',
    '[class*="date"]',
    'meta[property="article:published_time"]'
  ];
  
  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) {
      const datetime = element.getAttribute('datetime') || 
                       element.getAttribute('content') ||
                       element.textContent;
      if (datetime && datetime.trim()) {
        return datetime.trim();
      }
    }
  }
  
  return null;
}

// 檢查元素是否為噪音（不修改DOM，只判斷）
function isNoiseElement(element) {
  const noiseSelectors = [
    'script', 'style', 'noscript', 'iframe',
    'nav', 'header', 'footer', 'aside',
    'advertisement', 'ad', 'sidebar', 'side-bar',
    'comments', 'comment', 'related', 'recommended',
    'social', 'share', 'newsletter', 'btn', 'subscribe'
  ];
  
  const tagName = element.tagName.toLowerCase();
  const className = element.className.toLowerCase();
  const id = element.id.toLowerCase();
  
  // 檢查標籤名
  if (['script', 'style', 'noscript', 'iframe', 'nav', 'header', 'footer', 'aside', 'button'].includes(tagName)) {
    return true;
  }
  
  // 檢查class和id是否包含噪音關鍵字
  for (const keyword of noiseSelectors) {
    if (className.includes(keyword) || id.includes(keyword)) {
      return true;
    }
  }
  
  // 檢查role屬性
  const role = element.getAttribute('role');
  if (role && ['complementary', 'banner', 'navigation'].includes(role)) {
    return true;
  }
  
  return false;
}

// 提取主要內文
function extractMainContent() {
  // 不修改原始DOM，只讀取文字
  
  // 尋找主要內容區域
  const contentSelectors = [
    'article',
    '[role="main"]',
    'main',
    '.article-content',
    '.post-content',
    '.entry-content',
    '.content',
    '[class*="article-body"]',
    '[class*="post-body"]',
    '[itemprop="articleBody"]'
  ];
  
  for (const selector of contentSelectors) {
    const element = document.querySelector(selector);
    if (element) {
      // 獲取段落文字（不修改DOM）
      const paragraphs = element.querySelectorAll('p');
      if (paragraphs.length > 2) {
        let text = '';
        paragraphs.forEach(p => {
          // 檢查段落本身或其父元素是否為噪音
          if (isNoiseElement(p) || isNoiseElement(p.parentElement)) {
            return; // 跳過噪音段落
          }
          
          const pText = p.textContent.trim();
          if (pText.length > 20) { // 過濾太短的段落
            text += pText + '\n\n';
          }
        });
        if (text.length > 200) {
          return text.trim();
        }
      }
    }
  }
  
  // 備用方案：取得所有段落
  const allParagraphs = document.querySelectorAll('p');
  let text = '';
  allParagraphs.forEach(p => {
    // 過濾噪音段落
    if (isNoiseElement(p) || isNoiseElement(p.parentElement)) {
      return;
    }
    
    const pText = p.textContent.trim();
    if (pText.length > 30) { // 只保留有意義的段落
      text += pText + '\n\n';
    }
  });
  
  return text.trim();
}

// 整合所有資訊
function extractPageText() {
  const title = extractTitle();
  const author = extractAuthor();
  const date = extractPublishDate();
  const content = extractMainContent();
  
  // 偵測頁面語言
  const htmlLang = document.documentElement.lang || "";
  let detectedLanguage = "en"; // 預設英文
  
  if (htmlLang.startsWith("zh")) {
    detectedLanguage = "zh-TW";
  } else if (htmlLang.startsWith("en")) {
    detectedLanguage = "en";
  } else {
    // 備用：檢查內容是否有中文字
    const hasChinese = /[\u4e00-\u9fa5]/.test(content);
    detectedLanguage = hasChinese ? "zh-TW" : "en";
  }
  
  // 組合成結構化文字
  let structuredText = '';
  
  if (title) {
    structuredText += `Title: ${title}\n\n`;
  }
  
  if (author) {
    structuredText += `Author: ${author}\n`;
  }
  
  if (date) {
    structuredText += `Publish Date: ${date}\n`;
  }
  
  if (author || date) {
    structuredText += '\n';
  }
  
  structuredText += `Content:\n${content}`;
  
  return {
    text: structuredText.trim(),
    language: detectedLanguage
  };
}

// Listen for popup request
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "EXTRACT_PAGE_TEXT") {
    const result = extractPageText();
    sendResponse(result);
  }
});
