const CONTRACT_INPUT = document.getElementById("contractInput");
const JSON_OUTPUT = document.getElementById("jsonOutput");
const THEME_LABEL = document.getElementById("themeLabel");
const RISK_LABEL = document.getElementById("riskLabel");
const LAST_RUN = document.getElementById("lastRun");
const VALIDATION_STATUS = document.getElementById("validationStatus");
const PRETTY_PRINT = document.getElementById("prettyPrint");

const SAMPLE_CONTRACT = `<<<CONTRACT_TEXT_START>>>
This Software Subscription Agreement ("Agreement") is between Luna Metrics LLC ("Provider") and Finch Studios, Inc. ("Customer").

1. Term. The initial term is 12 months and will automatically renew for successive 12-month periods unless either party gives 30 days' written notice of non-renewal.
2. Fees. Customer will pay all fees within 10 days of invoice. Late payments accrue interest at 2% per month.
3. Service Levels. Provider targets 99.5% uptime each month.
4. Termination. Provider may terminate this Agreement for convenience upon 15 days' notice. Customer may terminate only for material breach with 30 days to cure.
5. Data Use. Provider may use Customer data to improve services.
<<<CONTRACT_TEXT_END>>>`;

const THEMES = [
  { name: "US_SAAS_OR_IT_SERVICES", triggers: ["saas", "subscription", "software", "api", "uptime", "service level", "platform"] },
  { name: "US_NDA", triggers: ["non-disclosure", "nda", "confidential"] },
  { name: "US_COMMERCIAL_LEASE", triggers: ["landlord", "tenant", "lease", "premises"] },
  { name: "US_EMPLOYMENT", triggers: ["employee", "employer", "salary", "at-will"] },
  { name: "US_LOAN_REFINANCE", triggers: ["loan", "lender", "borrower", "apr", "interest rate"] },
  { name: "US_REAL_ESTATE_SALE", triggers: ["purchase price", "escrow", "closing", "title"] },
  { name: "US_MUSIC_CONTRACT", triggers: ["artist", "royalties", "recording", "masters"] },
  { name: "US_HIRING_OR_STAFFING", triggers: ["recruiter", "placement fee", "staffing", "candidate"] },
  { name: "US_FAMILY_LAW_AGREEMENT", triggers: ["marital", "custody", "spousal support"] },
  { name: "US_CRIMINAL_DEFENSE_ENGAGEMENT", triggers: ["criminal", "retainer", "charges"] }
];

const VAGUE_TERMS = ["as soon as practicable", "best efforts", "commercially reasonable", "sole discretion", "subject to availability", "from time to time"];

const schemaTemplate = () => ({
  redFlags: [],
  overallRisk: "LOW",
  overallConfidence: "LOW",
  topIssuesForUser: [],
  classification: {
    contractType: "UNCLEAR",
    party1Type: "UNCLEAR",
    party2Type: "UNCLEAR",
    themeUsed: "US_GENERAL_COMMERCIAL",
    themeConfidence: "LOW"
  },
  extractedPenalties: [],
  meta: {
    analysisQuality: "LOW_CONFIDENCE",
    errors: []
  }
});

const normalize = (value) => value.toLowerCase();

const extractParties = (text) => {
  const patterns = [
    /between\s+([^\n,]+?)\s+and\s+([^\n,.]+?)(?:\.|,|\n)/i,
    /by and between\s+([^\n,]+?)\s+and\s+([^\n,.]+?)(?:\.|,|\n)/i,
    /Agreement is between\s+([^\n,]+?)\s+and\s+([^\n,.]+?)(?:\.|,|\n)/i
  ];
  for (const pattern of patterns) {
    const match = text.match(pattern);
    if (match) {
      return { party1Name: match[1].trim(), party2Name: match[2].trim() };
    }
  }
  return { party1Name: "PARTY1", party2Name: "PARTY2" };
};

const detectPartyType = (name) => {
  const lower = name.toLowerCase();
  if (/(llc|inc\.|corp|corporation|company|ltd|limited)/.test(lower)) {
    return "COMPANY";
  }
  if (/(individual|person)/.test(lower)) {
    return "INDIVIDUAL";
  }
  return "UNCLEAR";
};

const detectContractType = (party1Type, party2Type) => {
  if (party1Type === "COMPANY" && party2Type === "COMPANY") return "B2B";
  if ((party1Type === "COMPANY" && party2Type === "INDIVIDUAL") || (party2Type === "COMPANY" && party1Type === "INDIVIDUAL")) {
    return "B2C";
  }
  if (party1Type === "INDIVIDUAL" && party2Type === "INDIVIDUAL") return "C2C";
  return "UNCLEAR";
};

const detectTheme = (text) => {
  const lower = normalize(text);
  for (const theme of THEMES) {
    if (theme.triggers.some((trigger) => lower.includes(trigger))) {
      return { themeUsed: theme.name, themeConfidence: "HIGH" };
    }
  }
  return { themeUsed: "US_GENERAL_COMMERCIAL", themeConfidence: "LOW" };
};

const findPenaltyClauses = (text, party1Name, party2Name) => {
  const penalties = [];
  const lines = text.split(/\n|\./).map((line) => line.trim()).filter(Boolean);

  const findParty = (line) => {
    const lower = line.toLowerCase();
    if (party1Name && lower.includes(party1Name.toLowerCase())) return "PARTY1";
    if (party2Name && lower.includes(party2Name.toLowerCase())) return "PARTY2";
    return "BOTH";
  };

  const addPenalty = (line, type, ratePerDay, ratePerYearApprox) => {
    penalties.push({
      party: findParty(line),
      type,
      ratePerDay,
      ratePerYearApprox,
      capDescription: null,
      location: "Detected clause",
      quote: line.slice(0, 220)
    });
  };

  lines.forEach((line) => {
    const lower = line.toLowerCase();
    const percentMatch = line.match(/(\d+(?:\.\d+)?)\s*%/);
    if (!percentMatch) return;
    const rate = Number(percentMatch[1]);
    if (lower.includes("per day") || lower.includes("daily")) {
      addPenalty(line, "PER_DAY_PENALTY", rate / 100, (rate / 100) * 365);
    } else if (lower.includes("per month") || lower.includes("monthly")) {
      addPenalty(line, "LATE_PAYMENT_INTEREST", null, (rate / 100) * 12);
    } else if (lower.includes("per year") || lower.includes("per annum") || lower.includes("annual")) {
      addPenalty(line, "LATE_PAYMENT_INTEREST", null, rate / 100);
    }
  });

  return penalties;
};

const buildRedFlags = (text, penalties, party1Name, party2Name) => {
  const flags = [];
  const lower = normalize(text);

  penalties.forEach((penalty) => {
    if (penalty.type === "PER_DAY_PENALTY" && penalty.ratePerDay !== null) {
      if (penalty.ratePerDay >= 0.01) {
        flags.push({
          flag: "Very aggressive per-day penalty",
          description: "A per-day penalty at or above 1% per day is unusually aggressive compared to common US commercial practice.",
          plainLanguageImpact: "Daily penalties could grow extremely quickly and create outsized exposure for the paying party.",
          danger: "CRITICAL",
          confidence: "MEDIUM",
          affectedParty: penalty.party,
          favoredParty: penalty.party === "PARTY1" ? "PARTY2" : "PARTY1",
          location: penalty.location,
          quote: penalty.quote,
          category: "penalties",
          legalReference: "liquidated damages reasonableness",
          suggestion: "Discuss a lower daily rate or a reasonable cap with legal counsel."
        });
      } else if (penalty.ratePerDay > 0.005) {
        flags.push({
          flag: "Aggressive per-day penalty",
          description: "Per-day penalties above roughly 0.5% per day can be high compared to standard commercial norms.",
          plainLanguageImpact: "Even short delays could result in large penalty amounts.",
          danger: "HIGH",
          confidence: "MEDIUM",
          affectedParty: penalty.party,
          favoredParty: penalty.party === "PARTY1" ? "PARTY2" : "PARTY1",
          location: penalty.location,
          quote: penalty.quote,
          category: "penalties",
          legalReference: "liquidated damages reasonableness",
          suggestion: "Ask whether the penalty can be reduced or capped."
        });
      }
    }

    if (penalty.type === "LATE_PAYMENT_INTEREST" && penalty.ratePerYearApprox !== null) {
      if (penalty.ratePerYearApprox > 0.24) {
        flags.push({
          flag: "High late payment interest",
          description: "Annualized late payment interest above 24% can be aggressive compared to common US commercial ranges.",
          plainLanguageImpact: "Late payments could accumulate interest quickly, increasing the cost of delays.",
          danger: "HIGH",
          confidence: "MEDIUM",
          affectedParty: penalty.party,
          favoredParty: penalty.party === "PARTY1" ? "PARTY2" : "PARTY1",
          location: penalty.location,
          quote: penalty.quote,
          category: "penalties",
          legalReference: "interest rate reasonableness",
          suggestion: "Consider negotiating a lower annualized rate or a grace period."
        });
      }
    }
  });

  if (VAGUE_TERMS.some((term) => lower.includes(term))) {
    flags.push({
      flag: "Vague or discretionary obligations",
      description: "The contract uses language like " +
        "\"sole discretion\" or \"subject to availability\" which can make obligations less enforceable.",
      plainLanguageImpact: "You may not be able to rely on the other party to deliver specific outcomes on a fixed timeline.",
      danger: "MEDIUM",
      confidence: "LOW",
      affectedParty: "BOTH",
      favoredParty: "UNCLEAR",
      location: "General obligations",
      quote: VAGUE_TERMS.find((term) => lower.includes(term)) || "Vague obligations",
      category: "performance",
      legalReference: null,
      suggestion: "Ask for clearer deliverables, timelines, and acceptance criteria."
    });
  }

  if (lower.includes("auto") && lower.includes("renew")) {
    flags.push({
      flag: "Auto-renewal with notice burden",
      description: "Automatic renewal clauses can require careful tracking of notice deadlines to avoid unintended extensions.",
      plainLanguageImpact: "If you miss the notice window, the agreement may renew for another term.",
      danger: "MEDIUM",
      confidence: "MEDIUM",
      affectedParty: "BOTH",
      favoredParty: "UNCLEAR",
      location: "Term and renewal",
      quote: "automatic renew",
      category: "termination",
      legalReference: null,
      suggestion: "Confirm renewal notice periods and consider calendar reminders or shorter renewal terms."
    });
  }

  const party1Terminate = party1Name && new RegExp(`${party1Name}.*terminate`, "i").test(text);
  const party2Terminate = party2Name && new RegExp(`${party2Name}.*terminate`, "i").test(text);
  if (party1Terminate && !party2Terminate) {
    flags.push({
      flag: "Termination asymmetry",
      description: "Only one party appears to have an express termination right, which can create lock-in for the other party.",
      plainLanguageImpact: "You may be unable to exit the agreement without breach or extended notice.",
      danger: "HIGH",
      confidence: "LOW",
      affectedParty: "PARTY2",
      favoredParty: "PARTY1",
      location: "Termination",
      quote: `${party1Name} ... terminate`,
      category: "termination",
      legalReference: null,
      suggestion: "Seek mutual termination rights or a clear exit path for both sides."
    });
  } else if (party2Terminate && !party1Terminate) {
    flags.push({
      flag: "Termination asymmetry",
      description: "Only one party appears to have an express termination right, which can create lock-in for the other party.",
      plainLanguageImpact: "You may be unable to exit the agreement without breach or extended notice.",
      danger: "HIGH",
      confidence: "LOW",
      affectedParty: "PARTY1",
      favoredParty: "PARTY2",
      location: "Termination",
      quote: `${party2Name} ... terminate`,
      category: "termination",
      legalReference: null,
      suggestion: "Seek mutual termination rights or a clear exit path for both sides."
    });
  }

  const mentionsUptime = ["uptime", "service level", "sla"].some((term) => lower.includes(term));
  const mentionsRemedy = ["credit", "refund", "service credit"].some((term) => lower.includes(term));
  if (mentionsUptime && !mentionsRemedy) {
    flags.push({
      flag: "SLA without remedies",
      description: "The agreement references service levels or uptime without specifying credits or remedies for missed targets.",
      plainLanguageImpact: "You may have limited recourse if service performance falls below expectations.",
      danger: "MEDIUM",
      confidence: "LOW",
      affectedParty: "PARTY2",
      favoredParty: "PARTY1",
      location: "Service levels",
      quote: "uptime/service levels",
      category: "service_levels",
      legalReference: null,
      suggestion: "Ask for service credits or termination rights tied to missed SLAs."
    });
  }

  return flags;
};

const summarizeIssues = (flags) => {
  return flags.slice(0, 5).map((flag) => `${flag.flag}: ${flag.plainLanguageImpact}`);
};

const calculateOverallRisk = (flags) => {
  const severity = { LOW: 1, MEDIUM: 2, HIGH: 3, CRITICAL: 4 };
  const max = flags.reduce((acc, flag) => Math.max(acc, severity[flag.danger]), 1);
  if (max === 4) return "CRITICAL";
  if (max === 3) return "HIGH";
  if (max === 2) return "MEDIUM";
  return "LOW";
};

const calculateConfidence = (flags, text) => {
  if (!text || text.length < 200) return "LOW";
  if (flags.length >= 3) return "HIGH";
  return "MEDIUM";
};

const validateSchema = (data) => {
  const requiredKeys = ["redFlags", "overallRisk", "overallConfidence", "topIssuesForUser", "classification", "extractedPenalties", "meta"];
  return requiredKeys.every((key) => Object.prototype.hasOwnProperty.call(data, key));
};

const runAnalysis = () => {
  const text = CONTRACT_INPUT.value.trim();
  const { party1Name, party2Name } = extractParties(text);
  const party1Type = detectPartyType(party1Name);
  const party2Type = detectPartyType(party2Name);
  const contractType = detectContractType(party1Type, party2Type);
  const theme = detectTheme(text);
  const penalties = findPenaltyClauses(text, party1Name, party2Name);
  const flags = buildRedFlags(text, penalties, party1Name, party2Name);

  const result = schemaTemplate();
  result.redFlags = flags;
  result.extractedPenalties = penalties;
  result.classification = {
    contractType,
    party1Type,
    party2Type,
    themeUsed: theme.themeUsed,
    themeConfidence: theme.themeConfidence
  };
  result.overallRisk = calculateOverallRisk(flags);
  result.overallConfidence = calculateConfidence(flags, text);
  result.topIssuesForUser = summarizeIssues(flags);
  result.meta.analysisQuality = text.length < 200 ? "LOW_CONFIDENCE" : "OK";
  if (party1Name === "PARTY1" || party2Name === "PARTY2") {
    result.meta.errors.push("Could not reliably identify both parties from the preamble.");
  }

  const isValid = validateSchema(result);
  const output = PRETTY_PRINT.checked ? JSON.stringify(result, null, 2) : JSON.stringify(result);
  JSON_OUTPUT.textContent = output;
  VALIDATION_STATUS.textContent = isValid ? "Schema valid" : "Schema invalid";
  VALIDATION_STATUS.style.background = isValid ? "#d1fae5" : "#fee2e2";
  VALIDATION_STATUS.style.color = isValid ? "#065f46" : "#991b1b";

  THEME_LABEL.textContent = `${theme.themeUsed} (${theme.themeConfidence})`;
  RISK_LABEL.textContent = result.overallRisk;
  LAST_RUN.textContent = new Date().toLocaleString();
};

const copyJson = async () => {
  try {
    await navigator.clipboard.writeText(JSON_OUTPUT.textContent);
    VALIDATION_STATUS.textContent = "Copied!";
  } catch (error) {
    VALIDATION_STATUS.textContent = "Copy failed";
  }
};

const downloadJson = () => {
  const blob = new Blob([JSON_OUTPUT.textContent], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = "contract-review.json";
  link.click();
  URL.revokeObjectURL(link.href);
};

const clearAll = () => {
  CONTRACT_INPUT.value = "";
  JSON_OUTPUT.textContent = "{}";
  THEME_LABEL.textContent = "—";
  RISK_LABEL.textContent = "—";
  LAST_RUN.textContent = "—";
  VALIDATION_STATUS.textContent = "Awaiting analysis";
};

const loadSample = () => {
  CONTRACT_INPUT.value = SAMPLE_CONTRACT;
};

PRETTY_PRINT.addEventListener("change", runAnalysis);

document.getElementById("analyze").addEventListener("click", runAnalysis);
document.getElementById("copyJson").addEventListener("click", copyJson);
document.getElementById("downloadJson").addEventListener("click", downloadJson);
document.getElementById("loadSample").addEventListener("click", loadSample);
document.getElementById("clearAll").addEventListener("click", clearAll);
