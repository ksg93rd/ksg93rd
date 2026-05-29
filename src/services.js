export const SERVICES = [
  {
    id: "formation",
    title: "Business Formation",
    icon: "🏛️",
    tagline: "Launch your business the right way — legally, quickly, confidently.",
    forWho: "Entrepreneurs, founders, and side-hustle owners ready to go legit.",
    includes: [
      "LLC, Corporation, Sole Proprietorship, or Nonprofit setup guidance",
      "EIN (Employer ID Number) application walkthrough",
      "Registered agent selection",
      "State-specific filing checklists",
      "Operating agreement or bylaws template",
      "Business bank account checklist"
    ],
    aiDeliverables: [
      "Recommended entity type based on your goals",
      "Step-by-step state filing checklist",
      "Post-formation action plan",
      "Compliance calendar (annual filings, renewals)"
    ],
    doneForYou: true,
    expertReview: true,
    chatPrompt: "Help me choose the right business structure for my company."
  },
  {
    id: "legal",
    title: "Legal Documents",
    icon: "📜",
    tagline: "Protect your business with professionally drafted legal templates.",
    forWho: "Any business owner who needs contracts, NDAs, or policies.",
    includes: [
      "Non-Disclosure Agreement (NDA)",
      "Client Service Agreement",
      "Independent Contractor Agreement",
      "Employment Agreement",
      "Terms of Service",
      "Privacy Policy",
      "Vendor/Supplier Agreement",
      "Business Purchase Agreement"
    ],
    aiDeliverables: [
      "Customized contract templates",
      "Plain-language clause explanations",
      "Risk flags and suggested additions",
      "Document review checklist"
    ],
    doneForYou: true,
    expertReview: true,
    chatPrompt: "I need help with a legal document for my business."
  },
  {
    id: "finance",
    title: "Finance & Accounting",
    icon: "💰",
    tagline: "Know your numbers. Forecast your future. Control your cash.",
    forWho: "Startups and SMBs wanting financial clarity without a CFO.",
    includes: [
      "Financial health audit",
      "Cash flow forecasting template",
      "Profit & loss statement setup",
      "Budget planning worksheets",
      "Invoice templates",
      "Pricing strategy calculator",
      "Break-even analysis",
      "Tax preparation checklist"
    ],
    aiDeliverables: [
      "Financial health score and gap analysis",
      "Revenue projection model",
      "Pricing recommendations",
      "Monthly cash flow dashboard"
    ],
    doneForYou: false,
    expertReview: true,
    chatPrompt: "Help me understand my business finances and cash flow."
  },
  {
    id: "hr",
    title: "HR & People Operations",
    icon: "👥",
    tagline: "Build a team that stays, performs, and grows with you.",
    forWho: "Growing businesses hiring their first or next employees.",
    includes: [
      "Employee handbook template",
      "Job description library",
      "Onboarding checklist",
      "Performance review templates",
      "PTO and leave policy templates",
      "Payroll setup guidance",
      "Classification guide (W-2 vs 1099)",
      "Interview question bank"
    ],
    aiDeliverables: [
      "Customized employee handbook",
      "Hiring process flowchart",
      "Job posting that attracts top talent",
      "Onboarding checklist for day 1-90"
    ],
    doneForYou: false,
    expertReview: true,
    chatPrompt: "Help me build out my HR processes and hire my first employee."
  },
  {
    id: "marketing",
    title: "Marketing & Brand",
    icon: "📣",
    tagline: "Stand out, get found, and turn strangers into loyal customers.",
    forWho: "Business owners who want more leads, visibility, and revenue.",
    includes: [
      "Brand identity guide",
      "Marketing strategy roadmap",
      "Social media content calendar",
      "Email marketing sequences",
      "SEO keyword strategy",
      "Sales funnel design",
      "Content marketing plan",
      "Ad copy templates"
    ],
    aiDeliverables: [
      "Brand positioning statement",
      "90-day marketing plan",
      "Social media content calendar",
      "Email drip sequence (5 emails)"
    ],
    doneForYou: false,
    expertReview: false,
    chatPrompt: "Help me create a marketing strategy for my business."
  },
  {
    id: "automation",
    title: "Automation & Workflows",
    icon: "⚙️",
    tagline: "Automate the repetitive. Focus on what matters most.",
    forWho: "Business owners drowning in manual tasks and admin work.",
    includes: [
      "Business process audit",
      "Automation opportunity map",
      "CRM setup and configuration",
      "Email automation workflows",
      "Invoice and payment automation",
      "Social media scheduling",
      "Lead capture and follow-up",
      "Reporting and dashboard setup"
    ],
    aiDeliverables: [
      "Top 5 automation opportunities for your business",
      "Recommended tool stack",
      "Workflow diagram for key processes",
      "Implementation priority matrix"
    ],
    doneForYou: true,
    expertReview: false,
    chatPrompt: "Help me automate my business processes and workflows."
  },
  {
    id: "cybersecurity",
    title: "Cybersecurity",
    icon: "🔒",
    tagline: "Protect your data, customers, and business from threats.",
    forWho: "Any business handling customer data, payments, or sensitive info.",
    includes: [
      "Security risk assessment",
      "Password and access management guide",
      "Data backup strategy",
      "Employee security training checklist",
      "Incident response plan template",
      "Compliance checklist (GDPR, CCPA, HIPAA basics)",
      "Vendor security assessment",
      "Phishing awareness guide"
    ],
    aiDeliverables: [
      "Business security score",
      "Top 10 vulnerabilities to fix immediately",
      "Security policy template",
      "Incident response runbook"
    ],
    doneForYou: false,
    expertReview: true,
    chatPrompt: "Help me assess and improve my business cybersecurity."
  },
  {
    id: "website",
    title: "Website & Digital Presence",
    icon: "🌐",
    tagline: "Your 24/7 salesperson — built fast, ranked well, converting always.",
    forWho: "Businesses without a website or with one that doesn't convert.",
    includes: [
      "Website brief and sitemap",
      "Domain name selection guide",
      "Landing page copy templates",
      "SEO setup checklist",
      "Google Business Profile optimization",
      "Website performance checklist",
      "Conversion rate optimization tips",
      "Analytics setup guide"
    ],
    aiDeliverables: [
      "Complete website brief (5 pages)",
      "Homepage copy draft",
      "SEO-optimized meta descriptions",
      "Site architecture and navigation map"
    ],
    doneForYou: true,
    expertReview: false,
    chatPrompt: "Help me build or improve my business website."
  }
];

export function getServiceById(id) {
  return SERVICES.find(s => s.id === id);
}
