// Kismoe AI Demo Response Engine — keyword-matched responses

const LEGAL_DISCLAIMER = '\n\n⚠️ **Disclaimer:** This is general information for educational purposes only and does not constitute legal advice. Please consult a qualified attorney for your specific situation.';
const FINANCIAL_DISCLAIMER = '\n\n⚠️ **Disclaimer:** This is general financial information and does not constitute financial or tax advice. Please consult a licensed CPA or financial advisor for guidance tailored to your situation.';
const HR_DISCLAIMER = '\n\n⚠️ **Disclaimer:** Employment laws vary by state and jurisdiction. This information is general in nature. Consult an HR professional or employment attorney for specific guidance.';
const SECURITY_DISCLAIMER = '\n\n⚠️ **Disclaimer:** Cybersecurity needs vary by industry and risk profile. This is general guidance only. Engage a qualified security professional for a comprehensive assessment.';

const RESPONSES = [
  // ── Greetings
  {
    keywords: ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'howdy', 'greetings', 'start'],
    response: `👋 Welcome to **Kismoe Business Services AI**!

I'm your AI business advisor — here to help you launch, manage, automate, and grow your business.

Here are some things I can help you with today:

🏛️ **Business Formation** — Choose the right entity type (LLC, Corp, etc.)
⚖️ **Legal Documents** — Contracts, NDAs, Privacy Policies
💰 **Finance** — Budgeting, forecasting, cash flow
👥 **HR & Hiring** — Job descriptions, handbooks, onboarding
📣 **Marketing** — Brand strategy, SEO, social media
⚡ **Automation** — Workflows, CRM, tools
🔒 **Cybersecurity** — Risk assessment, data protection
🌐 **Website** — Planning, copy, SEO

What would you like help with today?`,
  },

  // ── Business Formation
  {
    keywords: ['llc', 'limited liability', 'corporation', 'incorporate', 'nonprofit', 'sole prop', 'partnership', 'register', 'entity', 'business structure', 'formation', 'start a business', 'starting a business'],
    response: `🏛️ **Choosing the Right Business Entity**

Here's a quick comparison of the most common business structures:

**Sole Proprietorship**
- Simplest to set up, no formal registration required
- Owner personally liable for all debts
- Best for: freelancers, early-stage testing

**LLC (Limited Liability Company)**
- Protects personal assets from business debts
- Flexible taxation (pass-through or corporate)
- Best for: most small businesses and startups
- Cost: $50–$500 state filing fee

**S-Corporation**
- Can reduce self-employment taxes above ~$40K profit
- More administrative overhead (payroll required)
- Best for: profitable small businesses

**C-Corporation**
- Required for VC funding and stock options
- Double taxation at entity and dividend level
- Best for: high-growth startups seeking investment

**Nonprofit (501c3)**
- Tax-exempt status for qualifying organizations
- Strict rules on governance and revenue use
- Best for: charitable, educational, religious organizations

**My Recommendation Process:**
1. Define your liability concerns
2. Estimate first-year revenue
3. Determine if you need investors
4. Check your state's fees and requirements

Would you like a deeper dive into any specific entity type, or shall I generate a personalized entity comparison for your situation?` + LEGAL_DISCLAIMER,
  },

  // ── Legal Documents
  {
    keywords: ['nda', 'non-disclosure', 'contract', 'agreement', 'terms of service', 'privacy policy', 'legal document', 'clause', 'sign', 'attorney', 'lawyer'],
    response: `⚖️ **Essential Legal Documents for Your Business**

Here are the core legal documents every business needs:

**1. Non-Disclosure Agreement (NDA)**
- Protects confidential business information
- Use before sharing trade secrets with partners/employees
- Types: Unilateral (one-way) or Mutual (two-way)

**2. Client Service Agreement**
- Defines scope of work, payment terms, deliverables
- Includes limitation of liability clause
- Essential for every client engagement

**3. Privacy Policy**
- Required by law if you collect personal data
- Must cover: data collected, usage, storage, user rights
- Required for GDPR (EU), CCPA (California), and other laws

**4. Terms of Service**
- Governs use of your website or app
- Limits liability, defines acceptable use
- Protects intellectual property

**5. Independent Contractor Agreement**
- Distinguishes contractors from employees
- Protects against misclassification penalties
- Defines deliverables, IP ownership, payment

**6. Employment Agreement**
- Sets compensation, benefits, termination terms
- Non-compete and confidentiality provisions
- At-will employment language (varies by state)

Use the **Document Generator** tool in the Documents section to generate customized versions of any of these templates.

Which document do you need help with?` + LEGAL_DISCLAIMER,
  },

  // ── Finance
  {
    keywords: ['budget', 'forecast', 'invoice', 'cash flow', 'revenue', 'pricing', 'profit', 'loss', 'accounting', 'bookkeeping', 'tax', 'expense', 'finance', 'financial', 'break-even', 'runway'],
    response: `💰 **Building Financial Clarity for Your Business**

**Cash Flow Fundamentals:**
Cash flow = Money IN – Money OUT (per period)
- Positive cash flow: business is sustainable
- Negative cash flow: burning reserves (not always bad if investing in growth)

**Key Financial Metrics to Track:**
| Metric | What It Tells You |
|--------|------------------|
| Gross Margin | Revenue minus direct costs |
| Net Profit Margin | Profit after ALL expenses |
| Burn Rate | How fast you spend reserves |
| Runway | Months until cash runs out |
| MRR/ARR | Recurring revenue (subscriptions) |
| CAC | Cost to acquire one customer |
| LTV | Total value of a customer |

**Pricing Strategy Framework:**
1. **Cost-Plus**: Add profit margin to your costs
2. **Value-Based**: Price based on value delivered
3. **Competitive**: Benchmark against competitors
4. **Freemium**: Free tier + paid upgrades

**Revenue Forecast Formula:**
Monthly Revenue = (# Customers) × (Average Order Value) × (Purchase Frequency)

**Quick Wins:**
- Send invoices within 24 hours of delivery
- Require 25–50% deposit upfront for new clients
- Review expenses monthly and cut anything with no clear ROI
- Open a separate business bank account immediately

Would you like help building a revenue forecast or pricing model for your specific business?` + FINANCIAL_DISCLAIMER,
  },

  // ── HR
  {
    keywords: ['hire', 'employee', 'handbook', 'onboarding', 'payroll', 'job description', 'hr', 'human resources', 'interview', 'candidate', 'culture', 'benefits', 'performance', 'w-2', '1099', 'contractor', 'staff', 'team'],
    response: `👥 **Building Your HR Foundation**

**When to Hire:**
- You're turning down work due to capacity
- Admin tasks take more than 20% of your time
- You have consistent $5K+/month in revenue

**Employee vs. Independent Contractor:**
| Factor | Employee | Contractor |
|--------|----------|------------|
| You control HOW they work | Yes | No |
| Regular schedule | Yes | Typically No |
| Tools/equipment provided | Yes | No |
| Exclusive to you | Often | No |
⚠️ Misclassification penalties can be severe — when in doubt, classify as employee.

**Hiring Process (5 Steps):**
1. Write a clear job description with salary range
2. Post to LinkedIn, Indeed, and niche job boards
3. Structured interviews (same questions for all candidates)
4. Reference checks (call, don't just email)
5. Offer letter + employment agreement

**Day 1–30 Onboarding Checklist:**
- [ ] Hardware/software access set up
- [ ] Employee handbook signed
- [ ] Benefits enrollment
- [ ] Introduction to team and tools
- [ ] 30-day goals set with manager
- [ ] Payroll added

**Employee Handbook Must-Haves:**
- Code of conduct
- PTO and leave policies
- Anti-discrimination policy
- Remote work policy
- Social media policy
- Termination procedures

Use the **Document Generator** to generate a custom Employee Handbook template.` + HR_DISCLAIMER,
  },

  // ── Marketing
  {
    keywords: ['brand', 'social media', 'seo', 'funnel', 'email', 'content', 'marketing', 'leads', 'customers', 'audience', 'ad', 'campaign', 'instagram', 'facebook', 'google', 'tiktok', 'blog', 'website traffic'],
    response: `📣 **Marketing Strategy for Business Growth**

**Brand Foundation (Do This First):**
1. Define your ideal customer (demographics + psychographics)
2. Clarify your Unique Value Proposition (UVP)
3. Choose your brand voice (professional, casual, bold, nurturing?)
4. Establish brand colors, fonts, and logo

**Marketing Channel Priority (by ROI):**
🥇 **Email Marketing** — $36 return per $1 spent average
🥈 **SEO / Content** — Compounds over time, free traffic
🥉 **Referrals / Word of Mouth** — Highest trust, lowest cost
4. **Social Media** — Brand awareness, community building
5. **Paid Ads** — Fast but requires budget and testing

**90-Day Marketing Quick-Start:**
- Month 1: Nail your brand messaging, set up Google Business Profile, start email list
- Month 2: Create content calendar, post 3x/week on 1-2 platforms
- Month 3: Launch first email sequence, request 5 testimonials

**SEO Basics That Actually Work:**
- Optimize Google Business Profile (free, high ROI)
- Target long-tail keywords (3–5 word phrases)
- Create 1 in-depth blog post per week
- Get listed in relevant directories
- Build backlinks through guest posts and partnerships

**Email Funnel Sequence:**
1. Welcome email (deliver lead magnet)
2. Value email (tip or insight)
3. Story email (your journey / customer success)
4. Offer email (soft pitch)
5. Follow-up (answer objections)

What aspect of marketing would you like to go deeper on?`,
  },

  // ── Automation
  {
    keywords: ['automation', 'n8n', 'workflow', 'chatbot', 'crm', 'zapier', 'integrate', 'automate', 'manual', 'system', 'tool', 'software', 'app', 'process', 'efficient'],
    response: `⚡ **Business Automation — Work Smarter, Not Harder**

**Top 10 Automations for Small Businesses:**
1. **Lead capture → CRM** — Auto-add form submissions to your CRM
2. **Invoice automation** — Trigger invoices after project milestones
3. **Email follow-up sequences** — Nurture leads while you sleep
4. **Appointment scheduling** — Calendly/Acuity eliminates back-and-forth
5. **Social media posting** — Schedule a week of content in 1 hour
6. **Customer onboarding** — Welcome email + doc delivery + meeting booking
7. **Expense tracking** — Auto-categorize transactions via bank feed
8. **Review requests** — Send automated ask after delivery
9. **Inventory alerts** — Notify when stock is low
10. **Weekly reporting** — Auto-generate metrics dashboard

**Recommended Tool Stack (by budget):**

🆓 **Free / Low Cost:**
- CRM: HubSpot Free or Notion
- Email: Mailchimp (up to 500 contacts free)
- Scheduling: Calendly free
- Automation: n8n (self-hosted free) or Zapier (free tier)

💼 **Growing Business ($50–200/month):**
- CRM: HubSpot Starter or Pipedrive
- Email: ActiveCampaign
- Automation: Make (formerly Integromat) or Zapier Starter
- Project Mgmt: ClickUp or Asana

**n8n Workflow Ideas:**
- New contact form → Send welcome email + add to CRM + notify Slack
- New invoice paid → Update spreadsheet + send receipt + start fulfillment
- Daily sales report → Pull data + format → Send to email

What process do you want to automate first?`,
  },

  // ── Cybersecurity
  {
    keywords: ['security', 'risk', 'password', 'data protection', 'compliance', 'hack', 'breach', 'cyber', 'gdpr', 'hipaa', 'encrypt', 'vpn', 'phishing', 'backup', 'firewall'],
    response: `🔒 **Cybersecurity for Small Business — Essential Protection**

**The Small Business Threat Reality:**
- 43% of cyberattacks target small businesses
- Average cost of a data breach for SMBs: $108,000
- 60% of small businesses close within 6 months of a major breach

**Your Top 10 Security Actions (Priority Order):**

🔴 **Critical (Do Today):**
1. Enable Multi-Factor Authentication (MFA) on ALL accounts
2. Use a password manager (1Password, Bitwarden, Dashlane)
3. Enable automatic OS and software updates
4. Back up data with 3-2-1 rule: 3 copies, 2 media types, 1 offsite

🟡 **Important (This Month):**
5. Train employees to spot phishing emails
6. Implement least-privilege access (people only see what they need)
7. Encrypt sensitive files and drives
8. Use a business VPN for remote work

🟢 **Ongoing:**
9. Conduct quarterly security audits
10. Create and test an incident response plan

**Compliance Basics by Industry:**
| Industry | Key Regulations |
|----------|----------------|
| Healthcare | HIPAA |
| Finance | SOX, PCI-DSS |
| Any EU customers | GDPR |
| California customers | CCPA |
| E-commerce | PCI-DSS |

**Incident Response Plan (5 Steps):**
1. Identify — detect and confirm the incident
2. Contain — isolate affected systems
3. Eradicate — remove the threat
4. Recover — restore systems and data
5. Learn — document and improve

Would you like help building a security policy or incident response plan?` + SECURITY_DISCLAIMER,
  },

  // ── Website
  {
    keywords: ['website', 'landing page', 'domain', 'sitemap', 'design', 'web', 'online', 'digital', 'seo', 'page', 'host', 'wordpress', 'wix', 'squarespace', 'shopify', 'convert'],
    response: `🌐 **Building a Business Website That Converts**

**5-Page Website Blueprint:**

📄 **Homepage**
- Clear headline answering "What do you do + who do you serve?"
- 3–5 value propositions above the fold
- Social proof (testimonials, logos, numbers)
- Single strong CTA button

📄 **About Page**
- Your story and mission
- Team photos and bios
- Why you're different
- Trust signals (press, awards, certifications)

📄 **Services/Products**
- Clear description of each offering
- Pricing or "start from" pricing
- FAQs for each service
- Testimonials relevant to each service

📄 **Case Studies / Portfolio**
- Before/after results
- Client quotes
- Specific metrics (revenue increased by 40%)

📄 **Contact / Book a Call**
- Simple contact form
- Direct email and phone
- Booking widget (Calendly)
- Address if relevant

**Platform Recommendations:**
| Platform | Best For | Cost |
|----------|----------|------|
| Webflow | Custom design, no code | $14+/mo |
| Framer | Modern, fast builds | $10+/mo |
| WordPress | Full control, SEO | $5+/mo hosting |
| Squarespace | Easy, beautiful | $16+/mo |
| Shopify | E-commerce | $29+/mo |

**SEO Must-Haves:**
- Title tags with target keyword + brand name
- Meta descriptions under 160 characters
- H1 on every page
- Alt text on all images
- Mobile-responsive design
- Page speed under 3 seconds

Use the **Website Builder** section to generate a complete website brief for your business!`,
  },

  // ── General business advice
  {
    keywords: ['help', 'advice', 'grow', 'scale', 'profit', 'business plan', 'strategy', 'goal', 'revenue', 'success', 'fail', 'challenge', 'problem', 'issue', 'plan'],
    response: `🚀 **Business Growth Strategy Framework**

**The Kismoe Business Operating System — 8 Pillars:**

Every successful business operates across these 8 dimensions:

1. 🏛️ **Legal Foundation** — Entity, contracts, compliance
2. 💰 **Financial Health** — Cash flow, pricing, forecasting
3. 👥 **Team & HR** — Hiring, culture, performance
4. 📣 **Marketing Engine** — Brand, leads, conversion
5. ⚡ **Operations & Automation** — Efficiency, tools, workflows
6. 🔒 **Security & Risk** — Data, compliance, resilience
7. 🌐 **Digital Presence** — Website, SEO, online reputation
8. 📈 **Growth Strategy** — Roadmap, goals, partnerships

**Common Business Challenges and Solutions:**

| Challenge | Root Cause | Solution |
|-----------|-----------|----------|
| Not enough leads | No marketing engine | Content + SEO + referrals |
| Cash flow problems | Poor pricing or slow invoicing | Raise prices, require deposits |
| Can't scale | Everything depends on you | Automate + document processes |
| Legal exposure | No contracts or entity | Formation + legal docs |
| Tech overwhelm | Too many tools | Audit + consolidate stack |

**Your Next 3 Moves (Priority Framework):**
1. Fix your biggest risk first (legal, financial, or security)
2. Build your most impactful growth lever (usually marketing or website)
3. Automate your most time-consuming task

What specific business challenge can I help you solve today?`,
  },
];

export function getAIResponse(message, context = null) {
  const lower = message.toLowerCase().trim();

  // Context-aware prefix
  let contextPrefix = '';
  if (context && context.title) {
    contextPrefix = `I'm asking about **${context.title}**.\n\n`;
  }

  // Find best matching response
  let best = null;
  let bestScore = 0;

  for (const entry of RESPONSES) {
    let score = 0;
    for (const kw of entry.keywords) {
      if (lower.includes(kw)) score++;
    }
    if (score > bestScore) {
      bestScore = score;
      best = entry;
    }
  }

  if (best && bestScore > 0) {
    return contextPrefix + best.response;
  }

  // Fallback
  return `${contextPrefix}Thank you for your question! I can help you with:

- **Business Formation** — Entity selection, registration, compliance
- **Legal Documents** — Contracts, NDAs, privacy policies
- **Finance** — Budgeting, forecasting, cash flow
- **HR & Hiring** — Job descriptions, handbooks, onboarding
- **Marketing** — Brand strategy, SEO, social media
- **Automation** — Workflows, CRM, tools
- **Cybersecurity** — Risk assessment, data protection
- **Website** — Planning, copy, SEO optimization

Try asking something like:
- "How do I choose between an LLC and Corporation?"
- "What legal documents does my business need?"
- "Help me build a marketing strategy"
- "How do I automate my invoicing?"

What specific business challenge can I help you with?`;
}
