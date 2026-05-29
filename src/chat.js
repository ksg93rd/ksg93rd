// Kismoe Chat Widget

import { getAIResponse } from './aiResponses.js';

const STORAGE_KEY = 'kismoe-chat-v1';
let chatHistory = [];
let chatContext = null;
let isOpen = false;

export function initChat() {
  loadHistory();

  const toggle = document.getElementById('chatToggle');
  const close = document.getElementById('chatClose');
  const sendBtn = document.getElementById('chatSend');
  const input = document.getElementById('chatInput');
  const clearBtn = document.getElementById('chatClear');

  toggle?.addEventListener('click', toggleChat);
  close?.addEventListener('click', closeChat);
  sendBtn?.addEventListener('click', sendMessage);
  clearBtn?.addEventListener('click', clearChat);

  input?.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Listen for context events from other modules
  document.addEventListener('setChatContext', (e) => {
    chatContext = e.detail;
    if (!isOpen) openChat();
    addSystemMessage(`Now focusing on: **${chatContext.title}**. Ask me anything about it!`);
  });

  renderMessages();
}

export function setChatContext(context) {
  chatContext = context;
}

export function openChat() {
  isOpen = true;
  const widget = document.getElementById('chatWidget');
  widget?.classList.add('open');
  setTimeout(() => {
    document.getElementById('chatInput')?.focus();
  }, 300);
}

function closeChat() {
  isOpen = false;
  const widget = document.getElementById('chatWidget');
  widget?.classList.remove('open');
}

function toggleChat() {
  if (isOpen) closeChat();
  else openChat();
}

function sendMessage() {
  const input = document.getElementById('chatInput');
  const text = input?.value?.trim();
  if (!text) return;

  input.value = '';
  addMessage('user', text);
  showTypingIndicator();

  const delay = 800 + Math.random() * 800;
  setTimeout(() => {
    removeTypingIndicator();
    const response = getAIResponse(text, chatContext);
    addMessage('assistant', response);
  }, delay);
}

function addMessage(role, content) {
  const msg = { role, content, timestamp: new Date().toISOString() };
  chatHistory.push(msg);
  saveHistory();
  renderMessages();
}

function addSystemMessage(content) {
  addMessage('system', content);
}

function showTypingIndicator() {
  const messages = document.getElementById('chatMessages');
  if (!messages) return;
  const div = document.createElement('div');
  div.id = 'typingIndicator';
  div.className = 'chat-message assistant typing';
  div.innerHTML = '<span class="typing-dot"></span><span class="typing-dot"></span><span class="typing-dot"></span>';
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
}

function removeTypingIndicator() {
  document.getElementById('typingIndicator')?.remove();
}

function renderMessages() {
  const container = document.getElementById('chatMessages');
  if (!container) return;

  if (chatHistory.length === 0) {
    container.innerHTML = `
      <div class="chat-welcome">
        <div class="chat-welcome-icon">🤖</div>
        <p>Hi! I'm your Kismoe AI Business Advisor.</p>
        <p>Ask me anything about starting, growing, or protecting your business!</p>
      </div>
    `;
    return;
  }

  container.innerHTML = chatHistory.map(msg => {
    if (msg.role === 'system') {
      return `<div class="chat-message system">${formatText(msg.content)}</div>`;
    }
    const time = new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    return `
      <div class="chat-message ${msg.role}">
        <div class="message-bubble">${formatText(msg.content)}</div>
        <div class="message-time">${time}</div>
      </div>
    `;
  }).join('');

  container.scrollTop = container.scrollHeight;
}

function formatText(text) {
  // Convert markdown-like syntax to HTML
  return text
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>')
    .replace(/`(.+?)`/g, '<code>$1</code>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br>')
    .replace(/^/, '<p>')
    .replace(/$/, '</p>');
}

function clearChat() {
  chatHistory = [];
  chatContext = null;
  saveHistory();
  renderMessages();
}

function loadHistory() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    chatHistory = raw ? JSON.parse(raw) : [];
  } catch {
    chatHistory = [];
  }
}

function saveHistory() {
  try {
    // Keep last 50 messages
    const trimmed = chatHistory.slice(-50);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(trimmed));
  } catch {}
}
