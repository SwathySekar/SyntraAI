// Background service worker

chrome.runtime.onInstalled.addListener(() => {
  console.log('Workflow Synthesizer Extension Installed');
  
  // Set default settings
  chrome.storage.sync.set({
    enabled: true,
    serverUrl: 'http://localhost:8000'
  });
});

// Listen for messages from content scripts
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'emailCaptured') {
    console.log('Email captured:', request.data);
    sendResponse({ success: true });
  }
});
