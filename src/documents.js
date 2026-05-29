// Kismoe Document Generator — Legal & Business Templates

export const DOCUMENT_TEMPLATES = {
  nda: {
    title: 'Non-Disclosure Agreement (NDA)',
    description: 'Protect your confidential business information when sharing with partners, employees, or contractors.',
    fields: [
      { name: 'DISCLOSING_PARTY', label: 'Disclosing Party (Your Business Name)', placeholder: 'e.g. Acme Solutions LLC' },
      { name: 'RECEIVING_PARTY', label: 'Receiving Party (Other Party Name)', placeholder: 'e.g. John Smith' },
      { name: 'PURPOSE', label: 'Purpose of Disclosure', placeholder: 'e.g. Evaluating a potential business partnership' },
      { name: 'DURATION', label: 'Confidentiality Duration', placeholder: 'e.g. 2 years' },
      { name: 'STATE', label: 'Governing State', placeholder: 'e.g. Texas' },
      { name: 'DATE', label: 'Agreement Date', placeholder: 'e.g. June 1, 2025' },
    ],
    template: `NON-DISCLOSURE AGREEMENT

This Non-Disclosure Agreement ("Agreement") is entered into as of {{DATE}}, between {{DISCLOSING_PARTY}} ("Disclosing Party") and {{RECEIVING_PARTY}} ("Receiving Party").

PURPOSE
The Receiving Party agrees to receive certain confidential information from the Disclosing Party for the purpose of: {{PURPOSE}}.

CONFIDENTIAL INFORMATION
"Confidential Information" means any data or information that is proprietary to the Disclosing Party and not generally known to the public, including but not limited to: business plans, financial data, customer lists, trade secrets, technical data, and business operations.

OBLIGATIONS
The Receiving Party agrees to:
1. Hold all Confidential Information in strict confidence
2. Not disclose Confidential Information to any third parties without prior written consent
3. Use Confidential Information solely for the Purpose stated above
4. Take reasonable precautions to protect the Confidential Information

DURATION
This Agreement shall remain in effect for {{DURATION}} from the date of execution.

GOVERNING LAW
This Agreement shall be governed by the laws of the State of {{STATE}}.

SIGNATURES

Disclosing Party: {{DISCLOSING_PARTY}}
Signature: _________________________
Date: _____________________________

Receiving Party: {{RECEIVING_PARTY}}
Signature: _________________________
Date: _____________________________

---
⚠️ DISCLAIMER: This template is provided for general informational purposes only and does not constitute legal advice. Please consult a qualified attorney before using this document.`,
  },

  operatingAgreement: {
    title: 'LLC Operating Agreement',
    description: 'Define ownership, management structure, and operating procedures for your LLC.',
    fields: [
      { name: 'LLC_NAME', label: 'LLC Name', placeholder: 'e.g. Acme Solutions LLC' },
      { name: 'STATE', label: 'State of Formation', placeholder: 'e.g. Texas' },
      { name: 'MEMBER_NAMES', label: 'Member Names (comma-separated)', placeholder: 'e.g. Jane Doe, John Smith' },
      { name: 'OWNERSHIP_SPLITS', label: 'Ownership Percentages', placeholder: 'e.g. Jane Doe: 60%, John Smith: 40%' },
      { name: 'EFFECTIVE_DATE', label: 'Effective Date', placeholder: 'e.g. June 1, 2025' },
      { name: 'PRINCIPAL_ADDRESS', label: 'Principal Business Address', placeholder: 'e.g. 123 Main St, Austin, TX 78701' },
    ],
    template: `LIMITED LIABILITY COMPANY OPERATING AGREEMENT
OF {{LLC_NAME}}

This Operating Agreement ("Agreement") is entered into as of {{EFFECTIVE_DATE}}, by and among the members of {{LLC_NAME}}, a limited liability company organized under the laws of the State of {{STATE}}.

ARTICLE I — FORMATION
The Members have formed a limited liability company pursuant to the LLC laws of {{STATE}}.

Principal Place of Business: {{PRINCIPAL_ADDRESS}}

ARTICLE II — MEMBERS AND OWNERSHIP
The following individuals/entities are Members of the Company:
{{MEMBER_NAMES}}

Ownership Interests:
{{OWNERSHIP_SPLITS}}

ARTICLE III — MANAGEMENT
The Company shall be managed by its Members. Decisions requiring approval shall be made by majority vote weighted by ownership percentage, unless unanimity is specified herein.

ARTICLE IV — CAPITAL CONTRIBUTIONS
Members agree to contribute capital as mutually agreed in writing. Additional capital calls require unanimous consent.

ARTICLE V — DISTRIBUTIONS
Distributions shall be made at the discretion of the Members in proportion to ownership interests.

ARTICLE VI — TRANSFERS OF MEMBERSHIP INTEREST
No Member may transfer their ownership interest without the written consent of all remaining Members.

ARTICLE VII — DISSOLUTION
The Company may be dissolved upon unanimous written agreement of all Members, or as required by law.

ARTICLE VIII — GOVERNING LAW
This Agreement shall be governed by the laws of the State of {{STATE}}.

SIGNATURES

Members of {{LLC_NAME}}:
{{MEMBER_NAMES}}

Signatures: _________________________
Date: {{EFFECTIVE_DATE}}

---
⚠️ DISCLAIMER: This template is provided for general informational purposes only and does not constitute legal advice. Consult a qualified attorney before using this document.`,
  },

  privacyPolicy: {
    title: 'Privacy Policy',
    description: 'Required by law if you collect personal data. Covers GDPR and CCPA basics.',
    fields: [
      { name: 'COMPANY_NAME', label: 'Company Name', placeholder: 'e.g. Acme Solutions LLC' },
      { name: 'WEBSITE_URL', label: 'Website URL', placeholder: 'e.g. www.acmesolutions.com' },
      { name: 'CONTACT_EMAIL', label: 'Privacy Contact Email', placeholder: 'e.g. privacy@acmesolutions.com' },
      { name: 'STATE', label: 'Primary State of Operation', placeholder: 'e.g. Texas' },
      { name: 'EFFECTIVE_DATE', label: 'Effective Date', placeholder: 'e.g. June 1, 2025' },
    ],
    template: `PRIVACY POLICY
{{COMPANY_NAME}} — {{WEBSITE_URL}}
Effective Date: {{EFFECTIVE_DATE}}

1. INTRODUCTION
{{COMPANY_NAME}} ("we," "us," or "our") respects your privacy. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website {{WEBSITE_URL}}.

2. INFORMATION WE COLLECT
- Personal Information: Name, email address, phone number, payment information
- Usage Data: Browser type, IP address, pages visited, time spent
- Cookies: We use cookies to improve your experience

3. HOW WE USE YOUR INFORMATION
We use collected information to:
- Provide and improve our services
- Process transactions
- Send promotional communications (with consent)
- Comply with legal obligations
- Analyze usage patterns

4. SHARING YOUR INFORMATION
We do not sell your personal information. We may share with:
- Service providers (payment processors, email services)
- Legal authorities when required by law
- Business partners with your consent

5. DATA SECURITY
We implement industry-standard security measures. However, no method of transmission over the internet is 100% secure.

6. YOUR RIGHTS
You have the right to:
- Access your personal data
- Request correction or deletion
- Opt out of marketing communications
- Data portability (where applicable)

7. CALIFORNIA RESIDENTS (CCPA)
California residents have additional rights under CCPA including the right to know, delete, and opt-out of sale of personal information.

8. COOKIES
You can control cookies through your browser settings. Disabling cookies may affect site functionality.

9. CONTACT US
For privacy questions, contact: {{CONTACT_EMAIL}}
{{COMPANY_NAME}}, {{STATE}}

---
⚠️ DISCLAIMER: This template is for general purposes only. Privacy laws vary by jurisdiction and industry. Consult legal counsel for a privacy policy tailored to your specific needs.`,
  },

  termsOfService: {
    title: 'Terms of Service',
    description: 'Governs how users interact with your website or application.',
    fields: [
      { name: 'COMPANY_NAME', label: 'Company Name', placeholder: 'e.g. Acme Solutions LLC' },
      { name: 'WEBSITE_URL', label: 'Website URL', placeholder: 'e.g. www.acmesolutions.com' },
      { name: 'CONTACT_EMAIL', label: 'Contact Email', placeholder: 'e.g. legal@acmesolutions.com' },
      { name: 'STATE', label: 'Governing State', placeholder: 'e.g. Texas' },
      { name: 'EFFECTIVE_DATE', label: 'Effective Date', placeholder: 'e.g. June 1, 2025' },
    ],
    template: `TERMS OF SERVICE
{{COMPANY_NAME}} — {{WEBSITE_URL}}
Effective Date: {{EFFECTIVE_DATE}}

1. ACCEPTANCE OF TERMS
By accessing and using {{WEBSITE_URL}}, you accept and agree to be bound by these Terms of Service. If you do not agree, please discontinue use immediately.

2. DESCRIPTION OF SERVICE
{{COMPANY_NAME}} provides [description of your service/product]. We reserve the right to modify or discontinue the service at any time.

3. USER OBLIGATIONS
You agree to:
- Provide accurate information
- Not use the service for unlawful purposes
- Not attempt to hack, scrape, or disrupt the service
- Not infringe on intellectual property rights

4. INTELLECTUAL PROPERTY
All content on this site is the property of {{COMPANY_NAME}}. You may not reproduce, distribute, or create derivative works without written permission.

5. LIMITATION OF LIABILITY
{{COMPANY_NAME}} shall not be liable for any indirect, incidental, special, or consequential damages arising from your use of the service.

6. DISCLAIMER OF WARRANTIES
The service is provided "as is" without warranties of any kind, express or implied.

7. GOVERNING LAW
These Terms are governed by the laws of the State of {{STATE}}.

8. CHANGES TO TERMS
We reserve the right to update these Terms. Continued use of the service constitutes acceptance of new Terms.

9. CONTACT
Questions about these Terms: {{CONTACT_EMAIL}}

---
⚠️ DISCLAIMER: This template is for general informational purposes. Consult an attorney for terms tailored to your specific business.`,
  },

  employmentAgreement: {
    title: 'Employment Agreement',
    description: 'Defines the terms of employment for new hires, including compensation and duties.',
    fields: [
      { name: 'COMPANY_NAME', label: 'Company Name', placeholder: 'e.g. Acme Solutions LLC' },
      { name: 'EMPLOYEE_NAME', label: 'Employee Full Name', placeholder: 'e.g. Jane Doe' },
      { name: 'JOB_TITLE', label: 'Job Title', placeholder: 'e.g. Marketing Manager' },
      { name: 'START_DATE', label: 'Start Date', placeholder: 'e.g. June 1, 2025' },
      { name: 'SALARY', label: 'Annual Salary', placeholder: 'e.g. $65,000' },
      { name: 'STATE', label: 'Governing State', placeholder: 'e.g. Texas' },
    ],
    template: `EMPLOYMENT AGREEMENT

This Employment Agreement ("Agreement") is entered into between {{COMPANY_NAME}} ("Employer") and {{EMPLOYEE_NAME}} ("Employee").

POSITION
Employee is hired as: {{JOB_TITLE}}
Start Date: {{START_DATE}}

COMPENSATION
Annual Salary: {{SALARY}}, payable bi-weekly/semi-monthly [choose one].
Benefits: As described in the Employee Handbook.

AT-WILL EMPLOYMENT
Employment is at-will. Either party may terminate the employment relationship at any time, with or without cause or notice.

DUTIES AND RESPONSIBILITIES
Employee agrees to perform the duties associated with the {{JOB_TITLE}} position and any additional duties reasonably assigned by Employer.

CONFIDENTIALITY
Employee agrees to maintain the confidentiality of all proprietary and confidential information of {{COMPANY_NAME}} during and after employment.

INTELLECTUAL PROPERTY
All work product created in the course of employment is the property of {{COMPANY_NAME}}.

NON-COMPETE / NON-SOLICITATION
[Add non-compete language if applicable — consult an attorney as enforceability varies by state]

GOVERNING LAW
This Agreement is governed by the laws of the State of {{STATE}}.

SIGNATURES

Employer: {{COMPANY_NAME}}
Signature: _________________________  Date: _______________

Employee: {{EMPLOYEE_NAME}}
Signature: _________________________  Date: _______________

---
⚠️ DISCLAIMER: Employment law varies significantly by state. This template is for general reference only. Consult an employment attorney before using.`,
  },

  contractorAgreement: {
    title: 'Independent Contractor Agreement',
    description: 'Define the relationship with freelancers and contractors to avoid misclassification.',
    fields: [
      { name: 'CLIENT_NAME', label: 'Client Business Name', placeholder: 'e.g. Acme Solutions LLC' },
      { name: 'CONTRACTOR_NAME', label: 'Contractor Name', placeholder: 'e.g. John Smith' },
      { name: 'SERVICES', label: 'Services to be Provided', placeholder: 'e.g. Website design and development' },
      { name: 'RATE', label: 'Rate / Payment Terms', placeholder: 'e.g. $75/hour, invoiced monthly' },
      { name: 'START_DATE', label: 'Project Start Date', placeholder: 'e.g. June 1, 2025' },
      { name: 'STATE', label: 'Governing State', placeholder: 'e.g. Texas' },
    ],
    template: `INDEPENDENT CONTRACTOR AGREEMENT

This Agreement is between {{CLIENT_NAME}} ("Client") and {{CONTRACTOR_NAME}} ("Contractor"), effective {{START_DATE}}.

SERVICES
Contractor agrees to provide: {{SERVICES}}

COMPENSATION
{{RATE}}. Client will not withhold taxes. Contractor is responsible for all self-employment taxes.

INDEPENDENT CONTRACTOR STATUS
Contractor is an independent contractor, not an employee. Contractor:
- Controls how and when the work is performed
- Uses their own tools and equipment
- May work for other clients
- Is not entitled to employee benefits

INTELLECTUAL PROPERTY
All deliverables created under this Agreement become the property of {{CLIENT_NAME}} upon full payment.

CONFIDENTIALITY
Contractor agrees to keep all Client information confidential and not disclose to third parties.

TERM AND TERMINATION
Either party may terminate this Agreement with 14 days written notice.

GOVERNING LAW
This Agreement is governed by the laws of {{STATE}}.

SIGNATURES

Client: {{CLIENT_NAME}}
Signature: _________________________  Date: _______________

Contractor: {{CONTRACTOR_NAME}}
Signature: _________________________  Date: _______________

---
⚠️ DISCLAIMER: Contractor misclassification can result in significant penalties. This template is for general reference. Consult an employment attorney for your specific situation.`,
  },

  employeeHandbook: {
    title: 'Employee Handbook',
    description: 'Comprehensive handbook covering company policies, culture, and expectations.',
    fields: [
      { name: 'COMPANY_NAME', label: 'Company Name', placeholder: 'e.g. Acme Solutions LLC' },
      { name: 'EFFECTIVE_DATE', label: 'Effective Date', placeholder: 'e.g. June 1, 2025' },
      { name: 'CEO_NAME', label: 'CEO / Owner Name', placeholder: 'e.g. Jane Doe' },
      { name: 'HR_EMAIL', label: 'HR Contact Email', placeholder: 'e.g. hr@acmesolutions.com' },
    ],
    template: `EMPLOYEE HANDBOOK
{{COMPANY_NAME}}
Effective: {{EFFECTIVE_DATE}}

A MESSAGE FROM OUR LEADERSHIP
Welcome to {{COMPANY_NAME}}! We're excited to have you on our team. This handbook outlines our policies, culture, and expectations.
— {{CEO_NAME}}, CEO

SECTION 1: OUR COMPANY
Mission: [Your mission statement]
Values: [Your core values — e.g., Integrity, Innovation, Customer Focus]

SECTION 2: EMPLOYMENT POLICIES
2.1 Equal Opportunity
{{COMPANY_NAME}} is an equal opportunity employer. We do not discriminate on the basis of race, color, religion, sex, national origin, age, disability, or any other protected characteristic.

2.2 At-Will Employment
Employment at {{COMPANY_NAME}} is at-will. Either party may end the relationship at any time.

2.3 Code of Conduct
Employees are expected to maintain professional standards, treat colleagues with respect, and uphold company values at all times.

SECTION 3: WORK SCHEDULE & REMOTE WORK
Standard hours: [Define your hours]
Remote work policy: [Define remote work rules]

SECTION 4: COMPENSATION & BENEFITS
4.1 Pay Schedule: [Bi-weekly / Semi-monthly]
4.2 Health Insurance: [Coverage details]
4.3 PTO Policy: [Accrual rate and rules]
4.4 Holidays: [List of observed holidays]

SECTION 5: TIME OFF
5.1 Vacation: Employees accrue [X] days per year
5.2 Sick Leave: [X] days per year
5.3 Parental Leave: [Policy details]
5.4 Bereavement Leave: [Policy details]

SECTION 6: PERFORMANCE & DEVELOPMENT
Performance reviews are conducted [annually/semi-annually]. We support professional development through [describe programs].

SECTION 7: WORKPLACE POLICIES
7.1 Anti-Harassment: Zero tolerance for harassment of any kind
7.2 Drug-Free Workplace: Substance use during work hours is prohibited
7.3 Social Media: Employees may not disclose confidential company information online
7.4 Confidentiality: Protect all proprietary company information

SECTION 8: TERMINATION
Voluntary resignation: Provide [2 weeks] notice
Involuntary termination: [Describe process]
Final paycheck: Per state law requirements

QUESTIONS?
Contact HR at: {{HR_EMAIL}}

Employee Acknowledgment:
I have received and read this handbook.
Name: _________________________  Date: _______________
Signature: _________________________

---
⚠️ DISCLAIMER: This handbook template requires customization for your specific situation. Employment laws vary by state. Consult an employment attorney before distributing to employees.`,
  },

  invoice: {
    title: 'Business Invoice',
    description: 'Professional invoice template for billing clients for products or services.',
    fields: [
      { name: 'COMPANY_NAME', label: 'Your Business Name', placeholder: 'e.g. Acme Solutions LLC' },
      { name: 'COMPANY_ADDRESS', label: 'Your Business Address', placeholder: 'e.g. 123 Main St, Austin, TX 78701' },
      { name: 'COMPANY_EMAIL', label: 'Your Email', placeholder: 'e.g. billing@acmesolutions.com' },
      { name: 'CLIENT_NAME', label: 'Client Name', placeholder: 'e.g. John Smith / XYZ Corp' },
      { name: 'INVOICE_NUMBER', label: 'Invoice Number', placeholder: 'e.g. INV-001' },
      { name: 'INVOICE_DATE', label: 'Invoice Date', placeholder: 'e.g. June 1, 2025' },
      { name: 'DUE_DATE', label: 'Due Date', placeholder: 'e.g. June 15, 2025' },
      { name: 'SERVICES_DESCRIPTION', label: 'Services / Items', placeholder: 'e.g. Website Design - 20 hours @ $100/hr' },
      { name: 'TOTAL_AMOUNT', label: 'Total Amount Due', placeholder: 'e.g. $2,000.00' },
    ],
    template: `INVOICE

FROM:
{{COMPANY_NAME}}
{{COMPANY_ADDRESS}}
{{COMPANY_EMAIL}}

BILL TO:
{{CLIENT_NAME}}

Invoice #: {{INVOICE_NUMBER}}
Invoice Date: {{INVOICE_DATE}}
Due Date: {{DUE_DATE}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DESCRIPTION OF SERVICES:
{{SERVICES_DESCRIPTION}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

TOTAL AMOUNT DUE: {{TOTAL_AMOUNT}}

PAYMENT INSTRUCTIONS:
[Add your preferred payment method — bank transfer, check, Venmo, PayPal, Stripe, etc.]

Payment is due by {{DUE_DATE}}. Late payments may be subject to a [1.5%] monthly late fee.

Thank you for your business!

{{COMPANY_NAME}}`,
  },
};

export function generateDocument(templateId, fields) {
  const template = DOCUMENT_TEMPLATES[templateId];
  if (!template) return null;

  let content = template.template;
  for (const [key, value] of Object.entries(fields)) {
    const placeholder = new RegExp(`\\{\\{${key}\\}\\}`, 'g');
    content = content.replace(placeholder, value || `[${key}]`);
  }
  return content;
}

export function downloadDocument(content, filename) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}
