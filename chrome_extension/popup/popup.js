// Popup script

let eventCount = 0;
let currentResult = null;
let activeWorkflows = [];

const TEMPLATES = {
  pdf: "When I download a PDF, summarize it and email me the key points",
  email: "When I compose an email, analyze the tone, suggest improvements, and email me the analysis",
  article: "When I read a Medium article, extract 3 key takeaways and email me",
  emailRead: "When I open and read an email, summarize the key points and action items, then email me",
  file: "When I download a file, analyze its content type, suggest relevant tags, and organize it into the appropriate folder"
};

function showToast(message, type = 'success') {
  const toast = document.getElementById('toast');
  toast.textContent = message;
  toast.className = `toast ${type} show`;
  setTimeout(() => {
    toast.classList.remove('show');
  }, 3000);
}

// Check server status
async function checkServerStatus() {
  try {
    const response = await fetch('http://localhost:8000/event', {
      method: 'OPTIONS'
    });
    updateServerStatus(true);
  } catch (error) {
    updateServerStatus(false);
  }
}

function updateServerStatus(isOnline) {
  const serverStatus = document.getElementById('serverStatus');
  const statusIndicator = document.getElementById('statusIndicator');
  const statusText = document.getElementById('statusText');
  
  if (isOnline) {
    serverStatus.textContent = '🟢 Online';
    statusIndicator.className = 'indicator active';
    statusText.textContent = 'Active';
  } else {
    serverStatus.textContent = '🔴 Offline';
    statusIndicator.className = 'indicator inactive';
    statusText.textContent = 'Server Offline';
  }
}



// Load event count from server only
async function loadEvents() {
  // Reset local counters
  eventCount = 0;
  document.getElementById('eventCount').textContent = 0;
  
  // Sync with server
  try {
    const response = await fetch('http://localhost:8000/events');
    if (response.ok) {
      const data = await response.json();
      const serverCount = data.events?.length || 0;
      document.getElementById('eventCount').textContent = serverCount;
      
      if (data.events && data.events.length > 0) {
        const recentEvents = data.events.slice(-5).reverse().map(e => ({
          subject: e.payload?.title || e.payload?.email_subject || e.payload?.file_name || 'Event',
          timestamp: e.timestamp,
          type: e.payload?.event_type || 'file_event'
        }));
        displayRecentEvents(recentEvents);
        // Don't store in local storage
      }
    }
  } catch (error) {
    console.log('Could not sync with server');
  }
}

loadEvents();

function displayRecentEvents(events) {
  const eventsList = document.getElementById('eventsList');
  const activityCount = document.getElementById('activityCount');
  
  if (events.length === 0) {
    eventsList.innerHTML = `
      <div class="empty-state">
        <div class="empty-state-icon">🎯</div>
        <div class="empty-state-title">No Activity Yet</div>
        <div class="empty-state-desc">Create a workflow above to start automating tasks</div>
      </div>
    `;
    activityCount.textContent = '0';
    return;
  }
  
  activityCount.textContent = events.length;
  
  const icons = {
    'email_compose': '✉️',
    'email_read': '📬',
    'article_write': '✍️',
    'article_read': '📖',
    'file_download': '📁',
    'file_event': '📁'
  };
  
  eventsList.innerHTML = events.map(event => `
    <div class="event-item">
      <div><strong>${icons[event.type] || '📌'} ${event.subject || event.title || 'Event'}</strong></div>
      <div class="event-time">${new Date(event.timestamp).toLocaleTimeString()}</div>
      <div class="event-desc" style="font-size: 11px; margin-top: 3px; opacity: 0.8;">✅ Processed successfully</div>
    </div>
  `).join('');
}

// Open dashboard
document.getElementById('openDashboard').addEventListener('click', () => {
  chrome.tabs.create({ url: 'http://localhost:8000/dashboard' });
});



// Template click handlers - fill textarea instead of creating directly
document.querySelectorAll('.template-card').forEach(card => {
  card.addEventListener('click', () => {
    const template = card.dataset.template;
    const query = TEMPLATES[template];
    document.getElementById('workflowQuery').value = query;
    document.getElementById('workflowQuery').focus();
    showToast('✏️ Template loaded - modify and create', 'success');
  });
});

// Add workflow
document.getElementById('addWorkflow').addEventListener('click', async () => {
  const query = document.getElementById('workflowQuery').value.trim();
  
  if (!query) {
    showToast('Please enter a workflow description', 'error');
    return;
  }
  
  await createWorkflow(query);
});

async function createWorkflow(query) {
  const button = document.getElementById('addWorkflow');
  button.disabled = true;
  button.classList.add('loading');
  
  // Get user email from storage
  const result = await chrome.storage.local.get(['userEmail']);
  const userEmail = result.userEmail || 'swathyecengg@gmail.com';
  
  // Append email to query if not already mentioned
  let finalQuery = query;
  if (!query.toLowerCase().includes('@') && !query.toLowerCase().includes('email me')) {
    finalQuery = `${query} and email results to ${userEmail}`;
  } else if (query.toLowerCase().includes('email me')) {
    finalQuery = query.replace(/email me/gi, `email ${userEmail}`);
  }
  
  try {
    const response = await fetch('http://localhost:8000/workflow', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: finalQuery, use_smart: true })
    });
    
    if (response.ok) {
      showToast('✅ Workflow created successfully!', 'success');
      document.getElementById('workflowQuery').value = '';
      
      // Add to active workflows
      const workflow = {
        id: Date.now(),
        query: finalQuery,
        active: true,
        created: new Date().toISOString()
      };
      activeWorkflows.push(workflow);
      displayWorkflows();
    } else {
      showToast('❌ Failed to create workflow', 'error');
    }
  } catch (error) {
    showToast('❌ Server not running', 'error');
  } finally {
    button.disabled = false;
    button.classList.remove('loading');
  }
}

function displayWorkflows() {
  const card = document.getElementById('workflowsCard');
  const list = document.getElementById('workflowsList');
  const count = document.getElementById('workflowCount');
  
  if (activeWorkflows.length === 0) {
    card.style.display = 'none';
    return;
  }
  
  card.style.display = 'block';
  count.textContent = activeWorkflows.length;
  
  list.innerHTML = activeWorkflows.map(wf => `
    <div class="workflow-item">
      <div class="workflow-info">
        <div class="workflow-title">${wf.query.substring(0, 40)}${wf.query.length > 40 ? '...' : ''}</div>
        <div class="workflow-meta">Created ${new Date(wf.created).toLocaleDateString()}</div>
      </div>
      <div class="workflow-toggle ${wf.active ? 'active' : ''}" data-id="${wf.id}"></div>
    </div>
  `).join('');
  
  // Add toggle listeners
  document.querySelectorAll('.workflow-toggle').forEach(toggle => {
    toggle.addEventListener('click', () => {
      const id = parseInt(toggle.dataset.id);
      const workflow = activeWorkflows.find(w => w.id === id);
      if (workflow) {
        workflow.active = !workflow.active;
        chrome.storage.local.set({ workflows: activeWorkflows });
        displayWorkflows();
        showToast(workflow.active ? 'Workflow activated' : 'Workflow paused', 'success');
      }
    });
  });
}

// Load workflows from server on startup
async function loadWorkflowsFromServer() {
  try {
    const response = await fetch('http://localhost:8000/workflows');
    if (response.ok) {
      const data = await response.json();
      if (data.workflows) {
        activeWorkflows = data.workflows.map(wf => ({
          id: wf.id,
          query: wf.query,
          active: true,
          created: wf.created_at || new Date().toISOString()
        }));
        displayWorkflows();
      }
    }
  } catch (error) {
    console.log('Could not load workflows from server');
  }
}

chrome.storage.local.get(['userEmail'], (result) => {
  if (result.userEmail) {
    document.getElementById('userEmail').value = result.userEmail;
  }
  loadWorkflowsFromServer();
});

// Save email configuration
document.getElementById('saveEmail').addEventListener('click', () => {
  const email = document.getElementById('userEmail').value.trim();
  if (!email) {
    showToast('Please enter a valid email', 'error');
    return;
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showToast('Invalid email format', 'error');
    return;
  }
  chrome.storage.local.set({ userEmail: email });
  showToast('✅ Email saved successfully', 'success');
});

// Toggle extension
document.getElementById('toggleExtension').addEventListener('click', async () => {
  const button = document.getElementById('toggleExtension');
  const result = await chrome.storage.sync.get(['enabled']);
  const newState = !result.enabled;
  
  await chrome.storage.sync.set({ enabled: newState });
  button.textContent = newState ? 'Pause' : 'Resume';
});

// Check for new results
async function checkForResults() {
  try {
    const response = await fetch('http://localhost:8000/results');
    if (response.ok) {
      const data = await response.json();
      if (data.results && data.results.length > 0) {
        const latestResult = data.results[data.results.length - 1];
        
        // Store result in extension storage for persistence
        chrome.storage.local.set({ 
          latestResult: latestResult,
          hasNewResult: true 
        });
        
        chrome.storage.local.get(['lastResultId'], (stored) => {
          if (stored.lastResultId !== latestResult.id) {
            showResultChoice(latestResult);
            chrome.storage.local.set({ lastResultId: latestResult.id });
          }
        });
      }
    }
  } catch (error) {
    console.log('Could not check results');
  }
}

// Check for stored results on popup open
function checkStoredResults() {
  chrome.storage.local.get(['latestResult', 'hasNewResult'], (stored) => {
    if (stored.hasNewResult && stored.latestResult) {
      showResultChoice(stored.latestResult);
    }
  });
}

function showResultChoice(result) {
  currentResult = result;
  const card = document.getElementById('resultsCard');
  const preview = document.getElementById('resultPreview');
  let previewText = '';
  if (result.type === 'result') {
    const content = (result.content || '').replace(/\*\*(.*?)\*\*/g, '$1').replace(/\n/g, ' ');
    previewText = content.substring(0, 80) + (content.length > 80 ? '...' : '');
  } else if (result.type === 'notification') {
    previewText = `File processed: ${result.title}`;
  } else {
    previewText = `Result ready`;
  }
  preview.textContent = previewText;
  card.style.display = 'block';
  document.getElementById('eventsCard').style.display = 'none';
}

function showResultInPopup() {
  if (!currentResult) return;
  const resultView = document.getElementById('resultView');
  const resultContent = document.getElementById('resultContent');
  const resultsCard = document.getElementById('resultsCard');
  const mainButtons = document.getElementById('mainButtons');
  let html = '';
  if (currentResult.type === 'result') {
    const formattedContent = (currentResult.content || '').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>');
    html = `<div style="margin-bottom: 15px;"><div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 6px; font-size: 13px; line-height: 1.6;">${formattedContent}</div></div>`;
  } else if (currentResult.type === 'notification') {
    const fileName = currentResult.title || 'Unknown file';
    const fileSize = currentResult.file_size || 0;
    const filePath = currentResult.file_path || 'Downloads';
    html = `<div style="margin-bottom: 15px;"><div style="font-size: 16px; font-weight: 600; margin-bottom: 10px;">📁 ${fileName}</div><div style="font-weight: 600; margin-bottom: 8px;">📄 File Details:</div><div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 6px; margin-bottom: 15px;"><div style="margin-bottom: 5px;">• File: ${fileName}</div><div style="margin-bottom: 5px;">• Size: ${(fileSize / 1024).toFixed(1)} KB</div><div>• Path: ${filePath}</div></div><div style="font-weight: 600; margin-bottom: 8px;">📝 Message:</div><div style="background: rgba(255,255,255,0.1); padding: 10px; border-radius: 6px; font-size: 12px; line-height: 1.5;">${currentResult.message}</div></div>`;
  }
  resultContent.innerHTML = html;
  resultsCard.style.display = 'none';
  resultView.style.display = 'block';
  mainButtons.style.display = 'none';
}

function hideResultView() {
  document.getElementById('resultView').style.display = 'none';
  document.getElementById('resultsCard').style.display = 'block'; // Keep results card visible
  document.getElementById('eventsCard').style.display = 'block';
  document.getElementById('mainButtons').style.display = 'block';
  // Don't clear currentResult to keep it available
}

async function emailResult() {
  if (!currentResult) return;
  
  try {
    // Send email via server
    const response = await fetch('http://localhost:8000/send-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        result: currentResult,
        recipient: 'swathyecengg@gmail.com'
      })
    });
    
    if (response.ok) {
      alert('✅ Email sent successfully to swathyecengg@gmail.com!');
    } else {
      throw new Error('Server error');
    }
  } catch (error) {
    // Fallback to clipboard
    let emailContent = '';
    if (currentResult.type === 'result') {
      const cleanContent = (currentResult.content || 'No content available').replace(/\*\*(.*?)\*\*/g, '$1');
      emailContent = `Subject: Syntra Result\n\n${cleanContent}`;
    } else if (currentResult.type === 'notification') {
      const fileName = currentResult.title || 'Unknown file';
    const fileSize = currentResult.file_size || 0;
    const filePath = currentResult.file_path || 'Downloads';
    emailContent = `Subject: File Notification - ${fileName}\n\nFile: ${fileName}\nSize: ${(fileSize / 1024).toFixed(1)} KB\nPath: ${filePath}\n\nMessage: ${currentResult.message}`;
    }
    
    navigator.clipboard.writeText(emailContent).then(() => {
      alert('✅ Email content copied to clipboard! Paste into your email client.');
    }).catch(() => {
      alert('✅ Result ready for email! (Copy manually from the display)');
    });
  }
  
  // Mark result as handled
  chrome.storage.local.set({ hasNewResult: false });
}

function copyResult() {
  if (!currentResult) return;
  let text = '';
  if (currentResult.type === 'result') {
    text = (currentResult.content || 'No content available').replace(/\*\*(.*?)\*\*/g, '$1');
  } else if (currentResult.type === 'notification') {
    const fileName = currentResult.title || 'Unknown file';
    const fileSize = currentResult.file_size || 0;
    const filePath = currentResult.file_path || 'Downloads';
    text = `${fileName}\n\nFile: ${fileName}\nSize: ${(fileSize / 1024).toFixed(1)} KB\nPath: ${filePath}\n\nMessage: ${currentResult.message}`;
  }
  navigator.clipboard.writeText(text).then(() => {
    alert('✅ Copied to clipboard!');
  });
}

document.getElementById('showInPopup').addEventListener('click', showResultInPopup);
document.getElementById('emailResult').addEventListener('click', emailResult);
document.getElementById('backBtn').addEventListener('click', hideResultView);
document.getElementById('copyResult').addEventListener('click', copyResult);
document.getElementById('emailFromView').addEventListener('click', emailResult);

// Add clear result functionality
function clearResult() {
  chrome.storage.local.set({ hasNewResult: false, latestResult: null });
  hideResultView();
  document.getElementById('resultsCard').style.display = 'none';
  document.getElementById('eventsCard').style.display = 'block';
}

// Add event listener if clear button exists
setTimeout(() => {
  const clearBtn = document.getElementById('clearResult');
  if (clearBtn) clearBtn.addEventListener('click', clearResult);
}, 100);

// Clear old workflows on startup to sync with server
chrome.storage.local.remove(['workflows', 'lastResultId']);

checkServerStatus();
checkForResults();
setInterval(() => {
  checkServerStatus();
  loadEvents();
  checkForResults();
}, 3000);
