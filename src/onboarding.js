// Kismoe Onboarding Wizard — 5-Step Business Setup

import { calculateHealthScore, getPriorityActions } from './healthScore.js';
import { supabase } from './supabase.js';

const STORAGE_KEY = 'kismoe-onboarding-v1';
let currentStep = 1;
const TOTAL_STEPS = 5;

export function initOnboarding() {
  const btn = document.getElementById('startJourneyBtn');
  const btn2 = document.getElementById('heroStartBtn');
  if (btn) btn.addEventListener('click', openWizard);
  if (btn2) btn2.addEventListener('click', openWizard);

  const overlay = document.getElementById('onboardingOverlay');
  if (overlay) {
    overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeWizard();
    });
  }

  // Check if already completed
  const saved = getSavedData();
  if (saved && saved.completed) {
    showHealthDashboard(saved);
  }
}

function getSavedData() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

function saveData(data) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
  } catch {}
}

export function openWizard() {
  currentStep = 1;
  const overlay = document.getElementById('onboardingOverlay');
  if (overlay) {
    overlay.classList.add('active');
    renderStep(currentStep);
  }
}

function closeWizard() {
  const overlay = document.getElementById('onboardingOverlay');
  if (overlay) overlay.classList.remove('active');
}

function renderStep(step) {
  const container = document.getElementById('wizardContent');
  if (!container) return;

  const saved = getSavedData() || {};

  const steps = {
    1: renderStep1(saved),
    2: renderStep2(saved),
    3: renderStep3(saved),
    4: renderStep4(saved),
    5: renderStep5(),
  };

  container.innerHTML = `
    <div class="wizard-header">
      <h2 class="wizard-title">Business Journey Setup</h2>
      <button class="wizard-close" id="wizardClose" aria-label="Close">&times;</button>
    </div>
    <div class="wizard-progress">
      ${Array.from({ length: TOTAL_STEPS }, (_, i) => `
        <div class="progress-step ${i + 1 < step ? 'done' : i + 1 === step ? 'active' : ''}">${i + 1}</div>
      `).join('')}
    </div>
    <div class="wizard-body">
      ${steps[step] || ''}
    </div>
    <div class="wizard-footer">
      ${step > 1 && step < 5 ? '<button class="btn ghost wizard-back" id="wizardBack">← Back</button>' : '<span></span>'}
      ${step < 4 ? '<button class="btn primary wizard-next" id="wizardNext">Continue →</button>' : ''}
      ${step === 4 ? '<button class="btn primary wizard-next" id="wizardNext">Complete Setup →</button>' : ''}
    </div>
  `;

  document.getElementById('wizardClose')?.addEventListener('click', closeWizard);
  document.getElementById('wizardBack')?.addEventListener('click', () => { currentStep--; renderStep(currentStep); });
  document.getElementById('wizardNext')?.addEventListener('click', () => handleNext(step));
}

function renderStep1(saved) {
  return `
    <div class="step-content">
      <div class="step-number">Step 1 of 4</div>
      <h3 class="step-title">Tell us about your business</h3>
      <div class="form-group">
        <label class="form-label">Business Name</label>
        <input type="text" id="s1-name" class="form-input" placeholder="e.g. Acme Solutions LLC" value="${saved.businessName || ''}">
      </div>
      <div class="form-group">
        <label class="form-label">Business Type</label>
        <div class="option-grid">
          ${['LLC', 'Corporation', 'Sole Proprietorship', 'Nonprofit', 'Partnership'].map(t => `
            <label class="option-pill ${saved.businessType === t ? 'selected' : ''}">
              <input type="radio" name="businessType" value="${t}" ${saved.businessType === t ? 'checked' : ''}>
              ${t}
            </label>
          `).join('')}
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Industry</label>
        <select id="s1-industry" class="form-input form-select">
          <option value="">Select your industry...</option>
          ${['Technology', 'Retail', 'Food & Beverage', 'Healthcare', 'Professional Services', 'Construction', 'Real Estate', 'Education', 'Finance', 'Marketing & Advertising', 'Non-Profit', 'Manufacturing', 'E-Commerce', 'Other'].map(i => `
            <option value="${i}" ${saved.industry === i ? 'selected' : ''}>${i}</option>
          `).join('')}
        </select>
      </div>
      <div class="form-group">
        <label class="form-label">Business Location (State)</label>
        <input type="text" id="s1-location" class="form-input" placeholder="e.g. Texas, California, New York" value="${saved.location || ''}">
      </div>
    </div>
  `;
}

function renderStep2(saved) {
  const stages = [
    { val: 'idea', label: '💡 Idea', desc: 'Validating my concept' },
    { val: 'launch', label: '🚀 Launch', desc: 'Just starting out' },
    { val: 'operate', label: '⚙️ Operate', desc: 'Running day to day' },
    { val: 'grow', label: '📈 Grow', desc: 'Scaling up' },
    { val: 'automate', label: '⚡ Automate', desc: 'Optimizing processes' },
    { val: 'scale', label: '🏔️ Scale', desc: 'Expanding significantly' },
    { val: 'protect', label: '🛡️ Protect', desc: 'Securing what I built' },
    { val: 'exit', label: '🏁 Exit', desc: 'Planning transition' },
  ];
  return `
    <div class="step-content">
      <div class="step-number">Step 2 of 4</div>
      <h3 class="step-title">Where are you in your journey?</h3>
      <div class="form-group">
        <label class="form-label">Business Stage</label>
        <div class="stage-grid">
          ${stages.map(s => `
            <label class="stage-card ${saved.stage === s.val ? 'selected' : ''}">
              <input type="radio" name="stage" value="${s.val}" ${saved.stage === s.val ? 'checked' : ''}>
              <span class="stage-label">${s.label}</span>
              <span class="stage-desc">${s.desc}</span>
            </label>
          `).join('')}
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Team Size (including yourself)</label>
        <select id="s2-teamSize" class="form-input form-select">
          ${[['1','Just me'],['2','2 people'],['3-5','3–5 people'],['6-10','6–10 people'],['11-25','11–25 people'],['25plus','25+ people']].map(([v, l]) => `
            <option value="${v}" ${saved.teamSize === v ? 'selected' : ''}>${l}</option>
          `).join('')}
        </select>
      </div>
    </div>
  `;
}

function renderStep3(saved) {
  const toolOptions = [
    { val: 'crm', label: '📊 CRM (HubSpot, Salesforce, etc.)' },
    { val: 'accounting', label: '💼 Accounting (QuickBooks, Xero, etc.)' },
    { val: 'project-mgmt', label: '✅ Project Management (Asana, Monday, etc.)' },
    { val: 'email-marketing', label: '📧 Email Marketing (Mailchimp, ActiveCampaign, etc.)' },
    { val: 'cybersecurity', label: '🔒 Cybersecurity Tools' },
    { val: 'hr-software', label: '👥 HR Software (Gusto, BambooHR, etc.)' },
    { val: 'website', label: '🌐 Business Website' },
    { val: 'analytics', label: '📈 Analytics (Google Analytics, etc.)' },
  ];
  return `
    <div class="step-content">
      <div class="step-number">Step 3 of 4</div>
      <h3 class="step-title">Revenue & Current Tools</h3>
      <div class="form-group">
        <label class="form-label">Annual Revenue Range</label>
        <div class="option-grid">
          ${[['under50k','Under $50K'],['50k-250k','$50K–$250K'],['250k-1m','$250K–$1M'],['1m-5m','$1M–$5M'],['5mplus','$5M+']].map(([v, l]) => `
            <label class="option-pill ${saved.revenue === v ? 'selected' : ''}">
              <input type="radio" name="revenue" value="${v}" ${saved.revenue === v ? 'checked' : ''}>
              ${l}
            </label>
          `).join('')}
        </div>
      </div>
      <div class="form-group">
        <label class="form-label">Tools You Currently Use</label>
        <div class="checkbox-grid">
          ${toolOptions.map(t => `
            <label class="checkbox-item ${(saved.tools || []).includes(t.val) ? 'selected' : ''}">
              <input type="checkbox" name="tools" value="${t.val}" ${(saved.tools || []).includes(t.val) ? 'checked' : ''}>
              ${t.label}
            </label>
          `).join('')}
        </div>
      </div>
    </div>
  `;
}

function renderStep4(saved) {
  const challengeOptions = [
    { val: 'no-legal-docs', label: '⚖️ No proper legal documents' },
    { val: 'no-website', label: '🌐 No professional website' },
    { val: 'no-crm', label: '📊 No CRM or customer tracking' },
    { val: 'poor-cash-flow', label: '💸 Poor or unpredictable cash flow' },
    { val: 'no-marketing-strategy', label: '📣 No clear marketing strategy' },
    { val: 'manual-processes', label: '⚙️ Too many manual processes' },
    { val: 'compliance-gaps', label: '📋 Compliance or regulatory gaps' },
    { val: 'cybersecurity-risk', label: '🔒 Cybersecurity concerns' },
    { val: 'hard-to-hire', label: '👥 Difficulty hiring good people' },
    { val: 'low-revenue', label: '📉 Revenue below target' },
  ];
  return `
    <div class="step-content">
      <div class="step-number">Step 4 of 4</div>
      <h3 class="step-title">What are your biggest challenges?</h3>
      <p class="step-subtitle">Select all that apply — we'll prioritize your roadmap accordingly.</p>
      <div class="checkbox-grid challenges-grid">
        ${challengeOptions.map(c => `
          <label class="checkbox-item ${(saved.challenges || []).includes(c.val) ? 'selected' : ''}">
            <input type="checkbox" name="challenges" value="${c.val}" ${(saved.challenges || []).includes(c.val) ? 'checked' : ''}>
            ${c.label}
          </label>
        `).join('')}
      </div>
    </div>
  `;
}

function renderStep5() {
  return `
    <div class="step-content step-complete">
      <div class="complete-icon">🎉</div>
      <h3 class="step-title">Setup Complete!</h3>
      <p class="step-subtitle">Your Business Health Score is being calculated and your personalized roadmap is ready.</p>
      <div class="complete-features">
        <div class="complete-feature">✅ Business Health Score calculated</div>
        <div class="complete-feature">✅ Priority roadmap generated</div>
        <div class="complete-feature">✅ AI advisor context loaded</div>
        <div class="complete-feature">✅ Document templates ready</div>
      </div>
      <button class="btn primary btn-large" id="viewDashboardBtn">View My Dashboard →</button>
    </div>
  `;
}

function collectStepData(step) {
  const data = {};
  if (step === 1) {
    data.businessName = document.getElementById('s1-name')?.value?.trim() || '';
    const typeEl = document.querySelector('input[name="businessType"]:checked');
    data.businessType = typeEl ? typeEl.value : '';
    data.industry = document.getElementById('s1-industry')?.value || '';
    data.location = document.getElementById('s1-location')?.value?.trim() || '';
  } else if (step === 2) {
    const stageEl = document.querySelector('input[name="stage"]:checked');
    data.stage = stageEl ? stageEl.value : '';
    data.teamSize = document.getElementById('s2-teamSize')?.value || '1';
  } else if (step === 3) {
    const revenueEl = document.querySelector('input[name="revenue"]:checked');
    data.revenue = revenueEl ? revenueEl.value : '';
    data.tools = Array.from(document.querySelectorAll('input[name="tools"]:checked')).map(el => el.value);
  } else if (step === 4) {
    data.challenges = Array.from(document.querySelectorAll('input[name="challenges"]:checked')).map(el => el.value);
  }
  return data;
}

function handleNext(step) {
  const existing = getSavedData() || {};
  const stepData = collectStepData(step);
  const merged = { ...existing, ...stepData };
  saveData(merged);

  if (step < 4) {
    currentStep = step + 1;
    renderStep(currentStep);
  } else {
    // Complete onboarding
    const finalData = { ...merged, completed: true };
    saveData(finalData);
    currentStep = 5;
    renderStep(5);

    // Save to Supabase in the background
    const scores = calculateHealthScore(finalData);
    saveToSupabase(finalData, scores);

    setTimeout(() => {
      const viewBtn = document.getElementById('viewDashboardBtn');
      if (viewBtn) {
        viewBtn.addEventListener('click', () => {
          closeWizard();
          showHealthDashboard(finalData);
        });
      }
    }, 100);
  }
}

export function showHealthDashboard(data) {
  const scores = calculateHealthScore(data);
  const actions = getPriorityActions(scores, data.challenges || []);

  // Show the health section and roadmap
  const section = document.getElementById('healthSection');
  if (section) {
    section.style.display = 'block';
    section.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  const roadmap = document.getElementById('roadmap');
  if (roadmap) roadmap.style.display = 'block';

  // Render scores
  renderScoreRing(scores.overall, 'overallScoreRing', 'overallScoreText');
  renderDimensionScores(scores);
  renderPriorityRoadmap(actions);
  updateBusinessName(data.businessName);
}

function renderScoreRing(score, ringId, textId) {
  const ring = document.getElementById(ringId);
  const text = document.getElementById(textId);
  if (!text) return;

  text.textContent = score;

  if (ring) {
    const circumference = 2 * Math.PI * 54;
    const offset = circumference - (score / 100) * circumference;
    ring.style.strokeDasharray = circumference;
    ring.style.strokeDashoffset = circumference;
    setTimeout(() => {
      ring.style.transition = 'stroke-dashoffset 1.5s ease';
      ring.style.strokeDashoffset = offset;
      const color = score >= 70 ? '#22c55e' : score >= 50 ? '#f59e0b' : '#ef4444';
      ring.style.stroke = color;
    }, 100);
  }
}

function renderDimensionScores(scores) {
  const dims = ['legal', 'financial', 'operations', 'marketing', 'technology', 'hr', 'cybersecurity', 'growth'];
  const labels = {
    legal: 'Legal', financial: 'Finance', operations: 'Operations',
    marketing: 'Marketing', technology: 'Technology', hr: 'HR',
    cybersecurity: 'Security', growth: 'Growth',
  };
  const container = document.getElementById('dimensionScores');
  if (!container) return;

  container.innerHTML = dims.map(dim => {
    const score = scores[dim] || 0;
    const color = score >= 70 ? '#22c55e' : score >= 50 ? '#f59e0b' : '#ef4444';
    return `
      <div class="dimension-score">
        <div class="dim-header">
          <span class="dim-label">${labels[dim]}</span>
          <span class="dim-value" style="color: ${color}">${score}</span>
        </div>
        <div class="dim-bar">
          <div class="dim-fill" data-score="${score}" style="width: 0%; background: ${color}"></div>
        </div>
      </div>
    `;
  }).join('');

  // Animate bars
  setTimeout(() => {
    container.querySelectorAll('.dim-fill').forEach(bar => {
      const score = bar.dataset.score;
      bar.style.transition = 'width 1.2s ease';
      bar.style.width = score + '%';
    });
  }, 200);
}

function renderPriorityRoadmap(actions) {
  const container = document.getElementById('roadmapContainer');
  if (!container) return;

  const priorityConfig = {
    high:   { label: '🔴 High Priority',   class: 'priority-high' },
    medium: { label: '🟡 Medium Priority', class: 'priority-medium' },
    low:    { label: '🟢 Low Priority',    class: 'priority-low' },
  };

  if (actions.length === 0) {
    container.innerHTML = '<p class="no-actions">Great job! Your business health looks strong. Keep maintaining each area.</p>';
    return;
  }

  container.innerHTML = actions.map(a => {
    const config = priorityConfig[a.priority] || priorityConfig.medium;
    return `
      <div class="roadmap-item ${config.class}">
        <div class="roadmap-priority-badge">${config.label}</div>
        <div class="roadmap-area">${a.area}</div>
        <div class="roadmap-action">${a.action}</div>
        <button class="btn ghost roadmap-btn" data-service="${a.service}">Get Started →</button>
      </div>
    `;
  }).join('');

  container.querySelectorAll('.roadmap-btn').forEach(btn => {
    btn.addEventListener('click', () => {
      const serviceId = btn.dataset.service;
      const event = new CustomEvent('openService', { detail: { serviceId } });
      document.dispatchEvent(event);
    });
  });
}

function updateBusinessName(name) {
  const el = document.getElementById('dashboardBusinessName');
  if (el && name) el.textContent = name;
}

async function saveToSupabase(onboardingData, scores) {
  const { currentUser } = await import('./auth.js');
  if (!currentUser) return;
  try {
    const { data: biz } = await supabase.from('kismoe_businesses').upsert({
      user_id: currentUser.id,
      business_name: onboardingData.businessName,
      business_type: onboardingData.businessType,
      industry: onboardingData.industry,
      location: onboardingData.location,
      stage: onboardingData.stage,
      team_size: onboardingData.teamSize,
      revenue: onboardingData.revenue,
      tools: onboardingData.tools,
      challenges: onboardingData.challenges,
      updated_at: new Date().toISOString()
    }, { onConflict: 'user_id' }).select().single();
    if (biz) {
      await supabase.from('kismoe_health_scores').insert({
        business_id: biz.id,
        user_id: currentUser.id,
        overall_score: scores.overall,
        legal_score: scores.legal,
        financial_score: scores.financial,
        operations_score: scores.operations,
        marketing_score: scores.marketing,
        technology_score: scores.technology,
        hr_score: scores.hr,
        cybersecurity_score: scores.cybersecurity,
        growth_score: scores.growth,
      });
    }
  } catch (err) {
    console.warn('Failed to save onboarding data to Supabase:', err);
  }
}
