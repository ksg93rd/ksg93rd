// Kismoe Business Services — Main App Orchestration

import { SERVICES, getServiceById } from './services.js';
import { initChat, openChat, setChatContext } from './chat.js';
import { initOnboarding, openWizard, showHealthDashboard } from './onboarding.js';
import { DOCUMENT_TEMPLATES, generateDocument, downloadDocument } from './documents.js';
import { initAuth, bindAuthEvents } from './auth.js';

// ── Init ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initAuth();
  bindAuthEvents();
  initChat();
  initOnboarding();
  renderServiceCards();
  initNavigation();
  initIntersectionObserver();
  initServicePanel();
  initWebsiteBuilder();
  initDocumentGenerator();
  initPricing();

  // Listen for openService events from roadmap buttons
  document.addEventListener('openService', (e) => {
    openServicePanel(e.detail.serviceId);
  });
});

// ── Navigation ──────────────────────────────────────────────────────────────
function initNavigation() {
  // Smooth scroll nav links
  document.querySelectorAll('a[href^="#"]').forEach(link => {
    link.addEventListener('click', (e) => {
      const href = link.getAttribute('href');
      if (href && href.startsWith('#')) {
        e.preventDefault();
        const target = document.querySelector(href);
        if (target) {
          target.scrollIntoView({ behavior: 'smooth', block: 'start' });
          document.getElementById('navMenu')?.classList.remove('open');
        }
      }
    });
  });

  // Mobile nav toggle
  const navToggle = document.getElementById('navToggle');
  const navMenu = document.getElementById('navMenu');
  navToggle?.addEventListener('click', () => {
    navMenu?.classList.toggle('open');
  });

  // Navbar scroll effect
  window.addEventListener('scroll', () => {
    const nav = document.getElementById('mainNav');
    if (nav) {
      nav.classList.toggle('scrolled', window.scrollY > 50);
    }
  });

  // CTA buttons
  document.getElementById('heroStartBtn')?.addEventListener('click', openWizard);
  document.getElementById('heroExploreBtn')?.addEventListener('click', () => {
    document.getElementById('services')?.scrollIntoView({ behavior: 'smooth' });
  });
  document.getElementById('startJourneyBtn')?.addEventListener('click', openWizard);
  document.getElementById('ctaStartBtn')?.addEventListener('click', openWizard);
  document.getElementById('heroChatBtn')?.addEventListener('click', openChat);
}

// ── Service Cards ───────────────────────────────────────────────────────────
function renderServiceCards() {
  const grid = document.getElementById('servicesGrid');
  if (!grid) return;

  grid.innerHTML = SERVICES.map(service => `
    <article class="service-card fade-in" data-service-id="${service.id}" role="button" tabindex="0" aria-label="View ${service.title} service">
      <div class="service-card-icon">${service.icon}</div>
      <h3 class="service-card-title">${service.title}</h3>
      <p class="service-card-tagline">${service.tagline}</p>
      <div class="service-card-badges">
        ${service.doneForYou ? '<span class="badge badge-blue">Done-For-You</span>' : ''}
        ${service.expertReview ? '<span class="badge badge-purple">Expert Review</span>' : ''}
      </div>
      <div class="service-card-footer">
        <span class="service-includes">${service.includes.length} included items</span>
        <span class="service-arrow">→</span>
      </div>
    </article>
  `).join('');

  // Click handlers
  grid.querySelectorAll('.service-card').forEach(card => {
    const open = () => openServicePanel(card.dataset.serviceId);
    card.addEventListener('click', open);
    card.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); open(); }
    });
  });
}

// ── Service Panel ───────────────────────────────────────────────────────────
function initServicePanel() {
  document.getElementById('panelClose')?.addEventListener('click', closePanel);
  document.getElementById('panelOverlay')?.addEventListener('click', closePanel);

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closePanel();
  });
}

function openServicePanel(serviceId) {
  const service = getServiceById(serviceId);
  if (!service) return;

  const panel = document.getElementById('servicePanel');
  const overlay = document.getElementById('panelOverlay');
  if (!panel || !overlay) return;

  document.getElementById('panelIcon').textContent = service.icon;
  document.getElementById('panelTitle').textContent = service.title;
  document.getElementById('panelTagline').textContent = service.tagline;
  document.getElementById('panelForWho').textContent = service.forWho;

  document.getElementById('panelIncludes').innerHTML = service.includes.map(i =>
    `<li class="panel-list-item">✓ ${i}</li>`
  ).join('');

  document.getElementById('panelDeliverables').innerHTML = service.aiDeliverables.map(d =>
    `<li class="panel-list-item deliverable">🤖 ${d}</li>`
  ).join('');

  const chatBtn = document.getElementById('panelChatBtn');
  if (chatBtn) {
    // Remove old handler
    const clone = chatBtn.cloneNode(true);
    chatBtn.parentNode.replaceChild(clone, chatBtn);
    clone.addEventListener('click', () => {
      const context = { title: service.title, chatPrompt: service.chatPrompt };
      document.dispatchEvent(new CustomEvent('setChatContext', { detail: context }));
      closePanel();
    });
  }

  panel.classList.add('open');
  overlay.classList.add('active');
  document.body.classList.add('panel-open');
}

function closePanel() {
  document.getElementById('servicePanel')?.classList.remove('open');
  document.getElementById('panelOverlay')?.classList.remove('active');
  document.body.classList.remove('panel-open');
}

// ── Intersection Observer (fade-in animations) ──────────────────────────────
function initIntersectionObserver() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

  document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
}

// ── Website Builder ─────────────────────────────────────────────────────────
function initWebsiteBuilder() {
  const form = document.getElementById('websiteBuilderForm');
  form?.addEventListener('submit', (e) => {
    e.preventDefault();
    generateWebsiteBrief();
  });
}

function generateWebsiteBrief() {
  const bizName = document.getElementById('wb-bizName')?.value || 'Your Business';
  const industry = document.getElementById('wb-industry')?.value || 'your industry';
  const targetAudience = document.getElementById('wb-audience')?.value || 'your ideal customers';
  const goal = document.getElementById('wb-goal')?.value || 'grow your business';

  const brief = `WEBSITE BRIEF — ${bizName}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BUSINESS OVERVIEW
Industry: ${industry}
Target Audience: ${targetAudience}
Primary Goal: ${goal}

RECOMMENDED SITE STRUCTURE (5 Pages)
1. Homepage — ${bizName} value proposition + CTA
2. Services/Products — What you offer + pricing
3. About — Your story + team
4. Testimonials/Results — Social proof
5. Contact/Book — Lead capture form + scheduling

HOMEPAGE HEADLINE FORMULA
"We help [${targetAudience}] [achieve specific outcome] without [main pain point]"

KEY MESSAGES
• Lead with the problem you solve
• Show proof (testimonials, case studies, numbers)
• Make the next step crystal clear
• Build trust before asking for the sale

RECOMMENDED PLATFORMS
- Webflow — Best for custom design
- Framer — Best for modern aesthetics
- WordPress — Best for SEO & flexibility
- Squarespace — Best for quick launch

SEO PRIORITIES
• Target 3–5 local/niche keywords
• Optimize Google Business Profile
• Add schema markup
• Build 10+ quality backlinks

TECH STACK RECOMMENDATION
• Analytics: Google Analytics 4 (free)
• Forms: Typeform or Google Forms
• Scheduling: Calendly (free tier)
• CRM Integration: HubSpot Free

Next Step: Open the AI Chat and say "Help me write homepage copy for ${bizName}"`;

  const output = document.getElementById('websiteBriefOutput');
  if (output) {
    output.style.display = 'block';
    output.querySelector('.brief-content').textContent = brief;
    output.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    showToast('Website brief generated!', 'success');
  }
}

// ── Document Generator ──────────────────────────────────────────────────────
function initDocumentGenerator() {
  const select = document.getElementById('docTemplateSelect');
  if (select) {
    select.innerHTML = `
      <option value="">Select a document type...</option>
      ${Object.entries(DOCUMENT_TEMPLATES).map(([id, t]) =>
        `<option value="${id}">${t.title}</option>`
      ).join('')}
    `;
    select.addEventListener('change', renderDocumentForm);
  }
}

function renderDocumentForm() {
  const templateId = document.getElementById('docTemplateSelect')?.value;
  const formContainer = document.getElementById('docFormContainer');
  if (!formContainer) return;

  if (!templateId) {
    formContainer.innerHTML = '';
    return;
  }

  const template = DOCUMENT_TEMPLATES[templateId];
  if (!template) return;

  formContainer.innerHTML = `
    <div class="doc-form-header">
      <h4 class="doc-form-title">${template.title}</h4>
      <p class="doc-form-desc">${template.description}</p>
    </div>
    <div class="doc-fields">
      ${template.fields.map(f => `
        <div class="form-group">
          <label class="form-label">${f.label}</label>
          <input type="text" class="form-input" name="${f.name}" placeholder="${f.placeholder}">
        </div>
      `).join('')}
    </div>
    <button class="btn primary" id="generateDocBtn" type="button">Generate Document →</button>
  `;

  document.getElementById('generateDocBtn')?.addEventListener('click', () => {
    const fields = {};
    formContainer.querySelectorAll('input[name]').forEach(input => {
      fields[input.name] = input.value.trim();
    });
    const content = generateDocument(templateId, fields);
    if (content) {
      const preview = document.getElementById('docPreview');
      if (preview) {
        preview.style.display = 'block';
        preview.querySelector('.doc-preview-content').textContent = content;
        preview.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
      document.getElementById('downloadDocBtn').onclick =
        () => downloadDocument(content, `${templateId}-${Date.now()}.txt`);
      showToast(`${template.title} generated!`, 'success');
    }
  });
}

// ── Pricing ─────────────────────────────────────────────────────────────────
function initPricing() {
  document.querySelectorAll('.pricing-cta').forEach(btn => {
    btn.addEventListener('click', openWizard);
  });
}

// ── Toast Notifications ─────────────────────────────────────────────────────
export function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  toast.innerHTML = `<span class="toast-icon">${icons[type] || '💬'}</span><span>${message}</span>`;
  container.appendChild(toast);

  setTimeout(() => toast.classList.add('visible'), 10);
  setTimeout(() => {
    toast.classList.remove('visible');
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
