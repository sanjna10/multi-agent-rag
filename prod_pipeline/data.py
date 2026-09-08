SAMPLE_RFP = """
REQUEST FOR PROPOSAL
Meridian Healthcare Systems
RFP-2024-MH-0847

TITLE: AI-Powered Analytics Platform Enhancement

ISSUING ORGANIZATION: Meridian Healthcare Systems
CONTACT: James Rivera, VP of Technology, j.rivera@meridianhc.com
SUBMISSION DEADLINE: October 15, 2024
BUDGET RANGE: $800,000 - $1,200,000

1. BACKGROUND
Meridian Healthcare Systems operates 14 hospitals and 52 outpatient clinics
across the Midwest region, serving approximately 2.3 million patients annually.
We currently use Acme Corporation's Product Alpha for our core analytics
needs and have been a customer since 2021 (current contract: $1.2M ACV).

We are seeking to enhance our analytics capabilities with AI-powered features
to improve clinical decision support, operational efficiency, and patient
outcome prediction.

2. SCOPE OF WORK
The selected vendor shall provide:

2.1 Clinical Decision Support Module
- Real-time patient risk scoring using historical EHR data
- Predictive models for readmission risk (target: 30-day readmission)
- Integration with existing Epic EHR system via FHIR APIs
- Dashboard for clinical staff with configurable alert thresholds

2.2 Operational Analytics Enhancement
- AI-powered demand forecasting for staffing and resource allocation
- Automated anomaly detection for billing and coding patterns
- Natural language query interface for non-technical users
- Integration with existing Product Alpha dashboards

2.3 Patient Outcome Analytics
- Population health trend analysis across all 14 facilities
- Social determinants of health (SDOH) data integration
- Predictive modeling for chronic disease management
- Outcome tracking and reporting for value-based care contracts

3. REQUIREMENTS
3.1 Technical Requirements
- Must integrate with existing Product Alpha deployment
- HIPAA-compliant data handling and storage
- SOC 2 Type II certification required
- Support for on-premises and hybrid cloud deployment
- API-first architecture for future extensibility
- Minimum 99.9% uptime SLA

3.2 Data Requirements
- Must process structured (EHR) and unstructured (clinical notes) data
- Support for HL7 FHIR R4 data standards
- Data retention per healthcare regulatory requirements
- De-identification capabilities for research datasets

3.3 Team Requirements
- Dedicated project manager
- Healthcare domain expertise (minimum 3 years)
- Data science team with clinical NLP experience
- 24/7 support during go-live and 90-day stabilization period

4. PROPOSAL FORMAT
Respondents must include:
a) Technical Approach
b) Healthcare Industry Experience
c) Proposed Team and Qualifications
d) Project Timeline and Milestones
e) Cost Proposal and Value Justification

5. EVALUATION CRITERIA
- Technical capability and approach: 30%
- Healthcare experience and domain expertise: 25%
- Team qualifications: 15%
- Timeline feasibility: 15%
- Cost and value: 15%
"""

PAST_PROPOSALS = [
    {
        "id": "proposal-midwest-health-2023",
        "title": "Midwest Health Network - Analytics Platform Deployment",
        "category": "healthcare",
        "text": """Acme Corporation proposed a comprehensive analytics deployment for Midwest
Health Network, a 9-hospital system serving 1.4 million patients. The project
included real-time clinical dashboards powered by Product Alpha, integration
with Cerner EHR via FHIR APIs, and predictive models for ED visit forecasting.

Technical approach: We deployed Product Alpha in a hybrid architecture with
on-premises data processing for PHI and cloud-based model training using
de-identified datasets.

Team: 8-person team including clinical informaticists, data scientists,
a project manager, and platform engineers.

Timeline: 14-month implementation with Discovery, Core Platform,
AI Model Development, UAT and Go-Live phases.

Outcome: ED visit prediction accuracy reached 84%. 30-day readmission model
achieved 0.78 AUC. Client renewed for 3 additional years."""
    },
    {
        "id": "proposal-statewide-insurance-2024",
        "title": "Statewide Insurance Group - Claims Analytics",
        "category": "insurance",
        "text": """Acme Corporation developed an AI-powered claims analytics system for
Statewide Insurance Group to detect fraudulent claims patterns and optimize
claims processing workflows. Product Alpha served as the analytics foundation
with custom ML models and NLP over unstructured claims narratives and medical records."""
    },
    {
        "id": "proposal-regional-medical-2024",
        "title": "Regional Medical Center - Patient Flow Optimization",
        "category": "healthcare",
        "text": """Acme Corporation built a patient flow optimization system for Regional
Medical Center. Product Alpha was deployed with predictive modules for patient
flow management, admission prediction, bed management, and discharge prediction.
Epic EHR integration used FHIR R4 APIs and included SDOH data."""
    },
]

COMPANY_KNOWLEDGE = [
    {
        "id": "kb-product-alpha-capabilities",
        "title": "Product Alpha Technical Capabilities",
        "category": "product",
        "text": """Product Alpha supports real-time data processing, customizable dashboards,
ML model hosting and serving, FHIR R4 and HL7v2, SOC 2 Type II certification,
HIPAA-compliant data handling, hybrid cloud deployment, API-first REST/GraphQL
interfaces, and 99.95% historical uptime."""
    },
    {
        "id": "kb-product-beta-overview",
        "title": "Product Beta Overview",
        "category": "product",
        "text": """Product Beta is a self-service analytics tool for non-technical users.
Features include natural-language queries, automated report generation,
anomaly detection, alerting, and integration with Product Alpha."""
    },
    {
        "id": "kb-team-bios",
        "title": "Acme Corporation Key Personnel",
        "category": "team",
        "text": """Acme Corporation maintains engineering, data science, and client services teams.
Healthcare leadership includes biomedical informatics and clinical NLP expertise,
supported by experienced project managers and platform engineers."""
    },
    {
        "id": "kb-security-compliance",
        "title": "Acme Corporation Security and Compliance",
        "category": "compliance",
        "text": """Acme Corporation is SOC 2 Type II certified, HIPAA compliant with BAA support,
HITRUST CSF certified, uses encryption at rest and in transit, SAML 2.0 SSO,
role-based access control, and a 99.95% uptime SLA."""
    },
]
