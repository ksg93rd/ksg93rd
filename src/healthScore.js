// Kismoe Business Health Score Calculator

export function calculateHealthScore(onboardingData) {
  const { businessType, stage, revenue, challenges = [], tools = [] } = onboardingData;

  // Normalize teamSize to a number
  const teamSizeMap = { '1': 1, '2': 2, '3-5': 4, '6-10': 8, '11-25': 18, '25plus': 30 };
  const teamSize = teamSizeMap[onboardingData.teamSize] || 1;

  // Base scores by stage
  const stageScores = {
    idea:     { legal: 20, financial: 15, operations: 10, marketing: 15, technology: 20, hr: 10, cybersecurity: 10, growth: 25 },
    launch:   { legal: 35, financial: 30, operations: 25, marketing: 30, technology: 30, hr: 20, cybersecurity: 20, growth: 40 },
    operate:  { legal: 50, financial: 50, operations: 45, marketing: 40, technology: 40, hr: 35, cybersecurity: 35, growth: 50 },
    grow:     { legal: 60, financial: 60, operations: 60, marketing: 60, technology: 55, hr: 55, cybersecurity: 45, growth: 65 },
    automate: { legal: 65, financial: 65, operations: 75, marketing: 65, technology: 75, hr: 60, cybersecurity: 60, growth: 70 },
    scale:    { legal: 70, financial: 70, operations: 70, marketing: 75, technology: 70, hr: 70, cybersecurity: 65, growth: 80 },
    protect:  { legal: 80, financial: 75, operations: 75, marketing: 70, technology: 75, hr: 70, cybersecurity: 85, growth: 70 },
    exit:     { legal: 85, financial: 80, operations: 80, marketing: 75, technology: 75, hr: 75, cybersecurity: 75, growth: 85 },
  };

  const base = stageScores[stage] || stageScores['operate'];

  // Revenue modifier (+/- points based on revenue range)
  const revenueBonus = {
    'under50k':   0,
    '50k-250k':   5,
    '250k-1m':    10,
    '1m-5m':      15,
    '5mplus':     20,
  };
  const rBonus = revenueBonus[revenue] || 0;

  // Team size modifier
  const teamBonus = teamSize > 10 ? 10 : teamSize > 5 ? 5 : teamSize > 1 ? 3 : 0;

  // Challenge deductions (each active challenge reduces relevant score)
  const challengeImpact = {
    'no-legal-docs':         { legal: -20 },
    'no-website':            { marketing: -15, growth: -10 },
    'no-crm':                { operations: -10, marketing: -10 },
    'poor-cash-flow':        { financial: -20 },
    'no-marketing-strategy': { marketing: -20, growth: -15 },
    'manual-processes':      { operations: -15, technology: -10 },
    'compliance-gaps':       { legal: -15, cybersecurity: -10 },
    'cybersecurity-risk':    { cybersecurity: -25 },
    'hard-to-hire':          { hr: -20 },
    'low-revenue':           { financial: -15, growth: -20 },
  };

  // Tool bonuses
  const toolBonus = {
    'crm':           { operations: 5, marketing: 5 },
    'accounting':    { financial: 8 },
    'project-mgmt':  { operations: 8 },
    'email-marketing':{ marketing: 8 },
    'cybersecurity': { cybersecurity: 8 },
    'hr-software':   { hr: 8 },
    'website':       { marketing: 5 },
    'analytics':     { marketing: 5, growth: 5 },
  };

  // Compute raw scores
  let scores = { ...base };

  // Apply revenue and team bonuses
  for (const key of Object.keys(scores)) {
    scores[key] = Math.min(100, scores[key] + rBonus + teamBonus);
  }

  // Apply challenge deductions
  for (const challenge of challenges) {
    const impact = challengeImpact[challenge];
    if (impact) {
      for (const [k, v] of Object.entries(impact)) {
        scores[k] = Math.max(0, (scores[k] || 50) + v);
      }
    }
  }

  // Apply tool bonuses
  for (const tool of tools) {
    const bonus = toolBonus[tool];
    if (bonus) {
      for (const [k, v] of Object.entries(bonus)) {
        scores[k] = Math.min(100, (scores[k] || 50) + v);
      }
    }
  }

  // Round all scores
  for (const key of Object.keys(scores)) {
    scores[key] = Math.round(scores[key]);
  }

  // Overall score = weighted average
  const weights = {
    legal: 0.15,
    financial: 0.20,
    operations: 0.15,
    marketing: 0.15,
    technology: 0.10,
    hr: 0.10,
    cybersecurity: 0.10,
    growth: 0.05,
  };

  let overall = 0;
  for (const [k, w] of Object.entries(weights)) {
    overall += (scores[k] || 0) * w;
  }
  scores.overall = Math.round(overall);

  return scores;
}

export function getScoreLabel(score) {
  if (score >= 80) return { label: 'Excellent', color: '#22c55e', emoji: '🟢' };
  if (score >= 60) return { label: 'Good',      color: '#84cc16', emoji: '🟡' };
  if (score >= 40) return { label: 'Fair',       color: '#f59e0b', emoji: '🟠' };
  if (score >= 20) return { label: 'Needs Work', color: '#ef4444', emoji: '🔴' };
  return                   { label: 'Critical',  color: '#dc2626', emoji: '🚨' };
}

export function getPriorityActions(scores, challenges) {
  const actions = [];

  if (scores.legal < 50) {
    actions.push({ priority: 'high', area: 'Legal', action: 'Set up your business entity and create essential contracts', service: 'legal' });
  }
  if (scores.financial < 50) {
    actions.push({ priority: 'high', area: 'Finance', action: 'Build a cash flow tracker and revenue forecast model', service: 'finance' });
  }
  if (scores.cybersecurity < 50) {
    actions.push({ priority: 'high', area: 'Security', action: 'Enable MFA on all accounts and create a security policy', service: 'cybersecurity' });
  }
  if (scores.marketing < 50) {
    actions.push({ priority: 'medium', area: 'Marketing', action: 'Build your brand messaging and start a content calendar', service: 'marketing' });
  }
  if (scores.operations < 50) {
    actions.push({ priority: 'medium', area: 'Automation', action: 'Identify your top 3 manual processes to automate', service: 'automation' });
  }
  if (scores.hr < 50) {
    actions.push({ priority: 'medium', area: 'HR', action: 'Create an employee handbook and onboarding process', service: 'hr' });
  }
  if (scores.growth < 50) {
    actions.push({ priority: 'low', area: 'Growth', action: 'Define your 90-day growth roadmap and key metrics', service: 'marketing' });
  }

  // Challenges-based actions
  if (challenges.includes('no-website')) {
    actions.unshift({ priority: 'high', area: 'Website', action: 'Build your business website — your 24/7 salesperson', service: 'website' });
  }

  return actions.slice(0, 6);
}
