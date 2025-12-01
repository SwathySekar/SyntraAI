console.log('🚀 Workflow Synthesizer - Medium Active');
console.log('Is a medium blog !');

const SERVER_URL = 'http://localhost:8000/event';
let lastSent = '';

async function sendEvent(title, content, eventType) {
  const data = { title, content, eventType };
  const dataStr = JSON.stringify(data);
  
  if (dataStr === lastSent) return;
  lastSent = dataStr;
  
  console.log('🚀 Sending:', eventType, { title: title.substring(0, 30), contentLen: content.length });
  
  try {
    const res = await fetch(SERVER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event_type: eventType,
        url: window.location.href,
        title: title,
        content: content.substring(0, 500),
        timestamp: new Date().toISOString()
      })
    });
    
    if (res.ok) {
      console.log('✅ Sent to server');
      chrome.storage.local.get(['eventCount', 'recentEvents'], (result) => {
        const count = (result.eventCount || 0) + 1;
        const events = result.recentEvents || [];
        events.unshift({ subject: title || 'Medium Article', timestamp: new Date().toISOString(), type: eventType });
        chrome.storage.local.set({ eventCount: count, recentEvents: events.slice(0, 5) });
      });
    }
  } catch (e) {
    console.log('⚠️ Server offline');
  }
}

function captureArticle() {
  // Get article title
  const titleEl = document.querySelector('h1, [data-testid="storyTitle"], article h1');
  const title = titleEl?.textContent?.trim() || document.title;
  
  // Get article content
  const articleEl = document.querySelector('article, [role="main"], .postArticle-content');
  const content = articleEl?.textContent?.trim() || '';
  
  console.log('📰 Article detected:', { title: title.substring(0, 50), contentLen: content.length });
  
  if (content.length > 100) {
    // Show analyzing notification
    showAnalyzingNotification();
    
    console.log('📖 Sending article_read event');
    sendEvent(title, content, 'article_read');
  } else {
    console.log('⚠️ Article too short or not found');
  }
}

function showAnalyzingNotification() {
  // Create notification
  const notification = document.createElement('div');
  notification.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 15px 20px;
    border-radius: 8px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    font-size: 14px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    z-index: 10000;
    animation: slideIn 0.3s ease-out;
  `;
  
  notification.innerHTML = '⚡ Syntra is analyzing this article...';
  
  // Add animation
  const style = document.createElement('style');
  style.textContent = `
    @keyframes slideIn {
      from { transform: translateX(100%); opacity: 0; }
      to { transform: translateX(0); opacity: 1; }
    }
  `;
  document.head.appendChild(style);
  
  document.body.appendChild(notification);
  
  // Remove after 3 seconds
  setTimeout(() => {
    notification.style.animation = 'slideIn 0.3s ease-out reverse';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}

// Capture article on page load
setTimeout(captureArticle, 2000);
setTimeout(captureArticle, 5000);
