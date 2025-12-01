// Gmail Content Script - Captures email composition and reading events

const SERVER_URL = 'http://localhost:8000/event';
let lastEmailData = {};
let lastReadEmail = {};
let composeObserver = null;

// Debounce function to avoid too many requests
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

// Extract email data from Gmail compose window
function extractEmailData() {
  const composeWindow = document.querySelector('[role="dialog"]') || document.querySelector('.nH.aHU');
  
  if (!composeWindow) return null;
  
  // Extract recipient
  const toField = composeWindow.querySelector('[name="to"]') || 
                  composeWindow.querySelector('[aria-label*="To"]');
  const to = toField ? toField.value || toField.textContent : '';
  
  // Extract subject
  const subjectField = composeWindow.querySelector('[name="subjectbox"]') ||
                       composeWindow.querySelector('input[aria-label*="Subject"]');
  const subject = subjectField ? subjectField.value || subjectField.textContent : '';
  
  // Extract body
  let body = '';
  const editables = Array.from(composeWindow.querySelectorAll('[contenteditable="true"]'));
  
  if (editables.length > 0) {
    const bodyField = editables[editables.length - 1];
    body = bodyField.textContent || bodyField.innerText || '';
  }
  
  return {
    to: to.trim(),
    subject: subject.trim(),
    body: body.trim(),
    url: window.location.href,
    timestamp: new Date().toISOString()
  };
}

// Send event to local server
async function sendEventToServer(emailData) {
  console.log('🚀 Attempting to send to:', SERVER_URL);
  console.log('📦 Payload:', emailData);
  
  try {
    const response = await fetch(SERVER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event_type: 'email_compose',
        url: emailData.url,
        email_to: emailData.to,
        email_subject: emailData.subject,
        email_body: emailData.body,
        timestamp: emailData.timestamp
      })
    });
    
    console.log('📊 Response status:', response.status);
    
    if (response.ok) {
      console.log('✅ Email event sent to Syntra');
      showNotification('⚡ Syntra is analyzing your email...');
      
      // Update extension storage
      if (typeof chrome !== 'undefined' && chrome.storage) {
        chrome.storage.local.get(['eventCount', 'recentEvents'], (result) => {
          const count = (result.eventCount || 0) + 1;
          const events = result.recentEvents || [];
          events.unshift({
            subject: emailData.subject || 'No subject',
            timestamp: emailData.timestamp,
            type: 'email_compose'
          });
          chrome.storage.local.set({ 
            eventCount: count, 
            recentEvents: events.slice(0, 5) 
          });
        });
      }
    } else {
      console.log('❌ Server responded with error:', response.status);
    }
  } catch (error) {
    console.log('❌ Error sending event:', error);
    console.log('⚠️ Workflow Synthesizer server not running');
  }
}

// Show notification in Gmail
function showNotification(message) {
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
  
  notification.textContent = message;
  
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
  
  setTimeout(() => {
    notification.style.animation = 'slideIn 0.3s ease-out reverse';
    setTimeout(() => notification.remove(), 300);
  }, 3000);
}



// Initialize
console.log('🚀 Syntra Extension Active');
console.log('📧 Monitoring Gmail for compose and read events...');
console.log('👉 Type in Gmail compose or open emails to capture events');



// Detect when user opens/reads an email
function detectEmailRead() {
  console.log('📖 Setting up email read detection...');
  const emailView = document.querySelector('[role="main"]');
  if (!emailView) {
    console.log('❌ Email view not found');
    setTimeout(detectEmailRead, 2000);
    return;
  }
  console.log('✅ Email view found, starting observer');
  
  const observer = new MutationObserver(debounce(() => {
    console.log('🔍 Checking for email content...');
    
    // Try multiple selectors for subject
    const emailSubject = document.querySelector('h2.hP')?.textContent ||
                        document.querySelector('.hP')?.textContent ||
                        document.querySelector('h2[data-legacy-thread-id]')?.textContent ||
                        document.querySelector('[data-subject]')?.getAttribute('data-subject');
    
    // Try multiple selectors for body
    const emailBody = document.querySelector('.a3s.aiL')?.innerText ||
                     document.querySelector('.a3s')?.innerText ||
                     document.querySelector('[data-message-id]')?.innerText ||
                     document.querySelector('.ii.gt')?.innerText;
    
    // Try multiple selectors for sender
    const emailFrom = document.querySelector('.gD')?.getAttribute('email') ||
                     document.querySelector('.go')?.textContent ||
                     document.querySelector('[email]')?.getAttribute('email');
    
    console.log('📧 Found - Subject:', emailSubject?.substring(0, 30), 'Body length:', emailBody?.length);
    console.log('📧 From:', emailFrom);
    console.log('📧 Body preview:', emailBody?.substring(0, 100));
    
    if ((emailSubject || emailBody) && emailBody && emailBody.length > 20) {
      const readData = {
        from: emailFrom || 'Unknown',
        subject: emailSubject.trim(),
        body: emailBody.trim().substring(0, 500),
        url: window.location.href,
        timestamp: new Date().toISOString()
      };
      
      if (JSON.stringify(readData) !== JSON.stringify(lastReadEmail)) {
        console.log('📨 New email detected, sending to server...');
        lastReadEmail = readData;
        sendReadEventToServer(readData);
      }
    }
  }, 1000));
  
  observer.observe(emailView, { childList: true, subtree: true });
}

async function sendReadEventToServer(readData) {
  try {
    const response = await fetch(SERVER_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        event_type: 'email_read',
        url: readData.url,
        email_from: readData.from,
        email_subject: readData.subject,
        email_body: readData.body,
        timestamp: readData.timestamp
      })
    });
    
    if (response.ok) {
      console.log('✅ Email read event sent to Syntra');
      showNotification('⚡ Syntra is analyzing this email...');
    }
  } catch (error) {
    console.log('❌ Error sending read event:', error);
  }
}

// Listen for input events - capture directly from event target
let capturedBody = '';
let capturedSubject = '';
let capturedTo = '';

document.addEventListener('input', (e) => {
  console.log('⌨️ Input on:', e.target.getAttribute('aria-label') || e.target.getAttribute('name'));
  
  // Capture based on field type
  if (e.target.getAttribute('name') === 'to' || e.target.getAttribute('aria-label')?.includes('To')) {
    capturedTo = e.target.value || e.target.textContent;
    console.log('📧 To field:', capturedTo);
  }
  
  if (e.target.getAttribute('name') === 'subjectbox' || e.target.getAttribute('aria-label')?.includes('Subject')) {
    capturedSubject = e.target.value || e.target.textContent;
    console.log('📝 Subject:', capturedSubject);
  }
  
  if (e.target.getAttribute('contenteditable') === 'true' && e.target.getAttribute('role') === 'textbox') {
    capturedBody = e.target.textContent || e.target.innerText;
    console.log('📝 Body:', capturedBody.substring(0, 50));
  }
  
  // Trigger send after capturing
  if (capturedBody.length > 5) {
    handleComposeChangeDirect();
  }
});

const handleComposeChangeDirect = debounce(() => {
  const emailData = {
    to: capturedTo.trim(),
    subject: capturedSubject.trim(),
    body: capturedBody.trim(),
    url: window.location.href,
    timestamp: new Date().toISOString()
  };
  
  console.log('📦 Sending captured data:', emailData);
  
  const dataChanged = JSON.stringify(emailData) !== JSON.stringify(lastEmailData);
  
  if (dataChanged && emailData.body.length > 5) {
    lastEmailData = emailData;
    sendEventToServer(emailData);
  }
}, 2000);

// Start monitoring email reads after page loads
setTimeout(() => {
  detectEmailRead();
}, 2000);
