"""
synthetic_data.py — Synthetic Training Data Generator
Creates labelled document examples for each department.

Why synthetic data?
- We don't have real classified documents to train on yet
- Synthetic data with realistic business language is enough for TF-IDF
- Once real documents are classified via the app, we can retrain on real data

Each example mimics what a real PDF extract would look like.
"""

TRAINING_DATA = {
    "Finance": [
        "INVOICE Invoice Number INV-2024-001 Date 15 January 2024 Bill To Acme Corporation Services Rendered Professional Consulting Q4 2023 Amount 25000 GST 2500 Total Due 27500 Payment Terms Net 30 days Bank Transfer BSB 062000",
        "BUDGET REPORT Annual Operating Budget FY2024 Department Finance Total Revenue 5200000 Operating Expenses Salaries 2100000 Marketing 450000 IT Infrastructure 320000 Net Profit Before Tax 1890000 Variance from FY2023 plus 12 percent",
        "FINANCIAL STATEMENT Balance Sheet as at 30 June 2024 Current Assets Cash 450000 Accounts Receivable 890000 Inventory 230000 Total Current Assets 1570000 Current Liabilities Accounts Payable 340000 Short Term Debt 200000",
        "TAX INVOICE ABN 12 345 678 901 Invoice Date 31 March 2024 Client Reference REF2024Q1 Description Software Development Services Hours 160 Rate 150 Subtotal 24000 GST 10 percent 2400 Total 26400",
        "PURCHASE ORDER PO Number PO-2024-0892 Vendor TechSupply Pty Ltd Item Laptops Dell Latitude 5540 Quantity 25 Unit Price 1899 Total 47475 Delivery Address 123 Business Park Sydney Approval Required Finance Director",
        "EXPENSE REPORT Employee John Smith Department Sales Period March 2024 Travel Flights Sydney Melbourne 450 Hotel 3 nights 520 Meals 180 Taxi Uber 95 Total Claimed 1245 Manager Approval Pending Reimbursement",
        "AUDIT REPORT External Audit FY2023 Prepared by KPMG Australia Opinion Unqualified audit opinion Financial statements present fairly material misstatement none identified Internal controls assessment satisfactory Recommendations improve accounts payable process",
        "PAYROLL SUMMARY Period ending 31 January 2024 Total Employees 142 Gross Salaries 1245000 PAYG Withholding 298000 Superannuation 9.5 percent 118275 Net Payroll 828725 Bank File Submitted ABA format CBA Business",
        "CREDIT NOTE CN-2024-015 Original Invoice INV-2024-008 Reason Returned goods damaged in transit Credit Amount 3200 plus GST 320 Total Credit 3520 Applied to Account Balance Remaining 0 Refund Method original payment method",
        "CASH FLOW STATEMENT Quarter 1 2024 Operating Activities Net Income 450000 Depreciation 45000 Changes Working Capital Accounts Receivable decrease 23000 Cash from Operations 518000 Investing Activities Equipment Purchase minus 120000 Net Cash 398000",
        "VENDOR INVOICE Supplier Global Supplies Ltd Invoice Date 20 Feb 2024 Items Office Furniture Chairs 50 units 200 each Desks 30 units 450 each Total 22500 Terms 45 days EOM Payment Bank Transfer Reference GLBL20240220",
        "ANNUAL REPORT SUMMARY Revenue Growth 18 percent EBITDA Margin 24 percent Earnings Per Share 2.45 Dividend Declared 0.85 per share Return on Equity 15.2 percent Debt to Equity Ratio 0.34 Capital Expenditure 3.2 million",
    ],

    "Human Resources": [
        "EMPLOYMENT CONTRACT This agreement is entered into between TechCorp Australia Pty Ltd and Sarah Johnson Position Senior Marketing Manager Commencement Date 1 March 2024 Salary 120000 per annum Probation 3 months Annual Leave 20 days",
        "PERFORMANCE REVIEW Employee Michael Chen Manager David Wong Review Period January to June 2024 Overall Rating Exceeds Expectations KPIs Met 5 of 6 Strengths Leadership technical skills Areas for Improvement presentation skills Next Review December 2024",
        "LEAVE APPLICATION Employee Name Emma Rodriguez Employee ID EMP2045 Leave Type Annual Leave From 15 April 2024 To 26 April 2024 Days 10 Reason Family holiday Return Date 29 April 2024 Manager Approval Required",
        "JOB DESCRIPTION Position Data Analyst Department Business Intelligence Reports to Head of Analytics Responsibilities Analyse business data develop dashboards prepare monthly reports Requirements Bachelor degree Statistics 3 years experience SQL Python desirable Salary Range 85000 to 100000",
        "ONBOARDING CHECKLIST New Employee James Wilson Start Date 8 January 2024 Complete payroll form Submit tax file number declaration Set up IT accounts email laptop mobile Workplace health safety induction HR policies manual signed Benefits superannuation health insurance",
        "TERMINATION LETTER Dear Mr Thompson This letter confirms termination of employment effective 28 February 2024 Reason redundancy Position Business Analyst Notice Period 4 weeks served Entitlements Annual leave balance 15 days paid out Redundancy payment 18000",
        "HR POLICY DOCUMENT Policy Flexible Working Arrangements Effective Date 1 January 2024 Scope All permanent employees Purpose enable work life balance Eligibility 6 months service Application process written request manager approval Types hybrid remote flexible hours",
        "PAYSLIP Employee Lisa Park Employee ID EMP1892 Pay Period 1 to 31 January 2024 Gross Pay 7500 Tax Withheld 1875 Superannuation 712.50 Net Pay 5625 YTD Gross 7500 YTD Tax 1875 Payment Date 31 January 2024",
        "WORKPLACE INVESTIGATION REPORT Incident Date 15 February 2024 Complainant anonymous Respondent Team Leader HR Department Allegation workplace bullying Investigation Findings substantiated partially Outcome formal warning issued counselling recommended",
        "TRAINING PLAN Employee Development Program 2024 Employee Group Middle Management Modules Leadership Communication Performance Management Duration 3 days Provider External facilitator Budget per employee 2500 Completion Required by June 2024",
        "RECRUITMENT REQUISITION Position Cloud Architect Department IT Infrastructure Headcount 1 new position Justification business growth Target Start Date May 2024 Salary Budget 150000 Interview Panel CTO HR Manager Technical Lead Recruitment Agency preferred",
        "EXIT INTERVIEW SUMMARY Employee Departing Jane Doe Department Customer Success Tenure 3 years 2 months Reason leaving better opportunity Feedback management style concerns workload balance Recommendation review team structure consider flexible arrangements",
    ],

    "Legal & Regulatory": [
        "NON DISCLOSURE AGREEMENT This Mutual Non Disclosure Agreement is entered into between Alpha Technologies Pty Ltd and Beta Solutions Ltd Purpose evaluation of potential business partnership Confidential Information trade secrets business plans technical data Term 2 years Governing Law New South Wales",
        "SERVICE AGREEMENT This Service Agreement dated 1 February 2024 between Cloud Services Inc Service Provider and Retail Corp Client Services managed IT infrastructure SLA uptime 99.9 percent Payment monthly 45000 Dispute Resolution arbitration Sydney Termination 90 days notice",
        "LEGAL NOTICE CEASE AND DESIST To Copycat Designs Ltd We write on behalf of our client Creative Studios Pty Ltd You are hereby directed to immediately cease and desist use of trademark logo design infringement damages sought 250000 Response required within 14 days",
        "REGULATORY SUBMISSION ASIC Annual Compliance Report Reporting Entity First National Bank Australia ACN 123 456 789 Reporting Period 1 July 2023 to 30 June 2024 AML CTF Program Status compliant Suspicious Matter Reports lodged 23 Training completed all staff",
        "COURT ORDER IN THE SUPREME COURT OF NEW SOUTH WALES Plaintiff Acme Corporation Defendant XYZ Trading Order The defendant is restrained from using the trade mark costs awarded to plaintiff hearing date 15 March 2024 Judge Honourable Justice Williams",
        "CONTRACT AMENDMENT Deed of Variation Original Contract Master Services Agreement dated 1 January 2023 Parties unchanged Amendment Clause 5.2 payment terms changed from 30 to 45 days Clause 8.1 liability cap increased to 2 million All other terms unchanged",
        "PRIVACY POLICY UPDATE Effective Date 1 March 2024 Changes Made Section 3 data retention updated to 7 years Section 5 third party sharing added marketing partners Section 7 user rights updated GDPR alignment Notification sent all users email 29 February 2024",
        "DISPUTE RESOLUTION NOTICE Pursuant to Clause 12 of the Master Agreement dated June 2022 we formally notify dispute regarding unpaid invoices totalling 89000 Request mediation within 21 days failing which arbitration proceedings will commence ACICA Rules apply",
        "TERMS OF SERVICE AGREEMENT User Agreement Version 4.2 Acceptance by using our platform you agree to these terms Intellectual Property all content owned by company Limitation of Liability maximum 1000 dollars Governing Law Victoria Australia Changes 30 days notice",
        "REGULATORY CHANGE NOTICE From APRA To All Authorised Deposit Taking Institutions Re Prudential Standard APS 112 Capital Adequacy amendments effective 1 January 2025 Submissions due 30 September 2024 Impact assessment required board sign off mandatory",
        "SHAREHOLDERS AGREEMENT This agreement governs relationship between shareholders Quorum Holdings 60 percent stake Minority Investors 40 percent Dividend Policy 30 percent net profit Tag Along Rights applies Drag Along threshold 75 percent Director Appointments 2 each",
        "INTELLECTUAL PROPERTY ASSIGNMENT Assignment of all rights title and interest in software platform TechApp Version 2.0 including source code documentation patents copyright from Developer John Smith to Purchaser Digital Corp Consideration 500000 Warranties clear title",
    ],

    "Licensing & Compliance": [
        "SOFTWARE LICENSE AGREEMENT Enterprise License Agreement between MegaSoft Corp and Financial Services Group License Type Enterprise Named Users 500 Annual Maintenance 20 percent Compliance Requirements ISO 27001 SOC 2 Type II Audit Rights annually Renewal Auto unless 90 days notice",
        "BUSINESS LICENSE Certificate of Registration Business Name Sunshine Retail Pty Ltd ACN 987 654 321 License Number BL-2024-089234 Type General Business License Issue Date 1 January 2024 Expiry 31 December 2024 Conditions comply with local council zoning requirements",
        "COMPLIANCE AUDIT REPORT Internal Audit Compliance Assessment Q1 2024 Scope AML KYC procedures data protection APRA requirements Findings 3 high risk 5 medium risk 12 low risk Recommendations board approved remediation plan 90 day implementation",
        "FOOD SAFETY CERTIFICATION Certification Body SafeFood Australia Certificate Holder Fresh Meals Co Certificate Number FS-2024-4521 Standard HACCP compliance Food Safety Program approved Audit Date 15 January 2024 Valid Until 14 January 2025 Rating Satisfactory",
        "ENVIRONMENTAL COMPLIANCE REPORT Organisation ManuFacture Pty Ltd Reporting Period FY2024 Emissions Scope 1 2400 tonnes CO2e Scope 2 890 tonnes Energy Consumption 45000 MWh Waste Generated 230 tonnes Recycled 78 percent Regulatory compliance NSW EPA confirmed",
        "OCCUPATIONAL LICENSE Electrician License License Number EL-234892 Holder Robert Wilson Class A Unlimited Issue Date 15 March 2020 Expiry 14 March 2026 Issuing Authority NSW Fair Trading Conditions comply with Australian wiring rules AS NZS 3000",
        "GDPR COMPLIANCE CERTIFICATE Data Protection Officer certification confirms organisation DataFlow Ltd complies with GDPR requirements Data Processing Register maintained Privacy Impact Assessments completed Breach notification procedures tested Annual review completed",
        "QUALITY MANAGEMENT CERTIFICATION ISO 9001 2015 Certificate Organisation Precision Engineering Pty Ltd Certificate Number QMS-2024-7823 Scope Design manufacture mechanical components Issue Date 1 February 2024 Expiry 31 January 2027 Surveillance audits annual",
        "BUILDING PERMIT Permit Number BP-2024-089 Property 45 Industrial Drive Penrith NSW Work Type Commercial fitout 3rd floor Description new office partitioning electrical mechanical Approved Plans attached Engineer Certificate required Conditions fire safety compliance",
        "FINANCIAL SERVICES LICENSE AFSL Number 456789 Holder Wealth Advisory Group Pty Ltd Authorisations provide financial product advice deal financial products operate registered scheme Conditions PI insurance minimum 2 million internal dispute resolution required",
        "IMPORT EXPORT PERMIT Permit Number IMP-2024-4521 Importer Pacific Trading Co Goods Electronic components resistors capacitors Country of Origin Taiwan Customs Tariff Heading 8533 Quantity 50000 units Value AUD 125000 Conditions BICON compliance required",
        "WORKPLACE HEALTH SAFETY COMPLIANCE SafeWork NSW Compliance Certificate Employer BuildRight Construction Certificate Period January to December 2024 Incidents reported 2 near misses Lost time injury frequency rate 2.3 Training completed all site workers",
    ],

    "IT & Technology": [
        "SYSTEM ARCHITECTURE DOCUMENT Project Cloud Migration Phase 2 Architecture AWS Multi Region Sydney Melbourne Primary Services EC2 Auto Scaling RDS PostgreSQL Multi AZ S3 CloudFront Route53 Security VPC WAF CloudTrail Performance targets 99.95 uptime sub 200ms latency",
        "INCIDENT REPORT Severity P1 Date 14 February 2024 System Production API Gateway Duration 2 hours 35 minutes Impact 45000 users affected Root Cause database connection pool exhaustion Resolution connection pool increased monitoring alerts added Post Incident Review scheduled",
        "SOFTWARE DEVELOPMENT AGREEMENT Client RetailCo Supplier DevShop Pty Ltd Project eCommerce platform rebuild Technology React Next.js Node.js PostgreSQL Timeline 6 months Milestones design approval sprint demos UAT go live Payment milestone based 250000 total",
        "SECURITY POLICY DOCUMENT Information Security Policy Version 3.1 Scope all employees contractors systems Classification Public Data no restriction Internal limited staff Confidential need to know Restricted executive only Password Requirements minimum 12 characters MFA mandatory",
        "IT INFRASTRUCTURE PROPOSAL Hardware Refresh Program 2024 Current State 3 year old server infrastructure Proposed Dell PowerEdge R750 x8 servers 2 NetApp storage arrays Cisco switching upgrade Total Investment 890000 ROI analysis 3 year payback period",
        "DATA BREACH NOTIFICATION Under Notifiable Data Breach Scheme Organisation HealthTech Pty Ltd Date Detected 8 March 2024 Date Notified OAIC 12 March 2024 Data Affected name email date of birth 23000 individuals Cause phishing attack credentials compromised Remediation MFA implemented",
        "CLOUD SERVICE AGREEMENT Provider Azure Microsoft Customer Analytics Corp Services Azure Kubernetes Service Azure SQL Database Azure DevOps Committed Spend 180000 annually Support Premier SLA 99.99 percent Data Residency Australia East region Data Sovereignty compliant",
        "PENETRATION TEST REPORT Scope external internal web application mobile Methodology OWASP PTES Findings Critical 1 SQL injection High 3 XSS stored broken auth Medium 8 Low 15 Remediation Critical fixed within 24 hours all others 30 day plan",
        "DISASTER RECOVERY PLAN RTO 4 hours RPO 1 hour Primary Site Sydney CBD Secondary Site Melbourne AWS Backup Strategy daily snapshots transaction log shipping 15 min Test Schedule quarterly full DR test last tested December 2023 result successful",
        "SOFTWARE ASSET MANAGEMENT REPORT Licence Compliance Review Microsoft Office 365 Licensed 450 Installed 423 Compliant Adobe Creative Cloud Licensed 45 Installed 52 Non compliant action required Oracle Database Licensed 10 Installed 8 Compliant SAP licences under review",
        "API DOCUMENTATION REST API v2.3 Base URL api.company.com Authentication Bearer JWT token Endpoints GET users returns user list POST documents upload PDF DELETE sessions logout Rate Limits 100 requests per minute Error Codes 401 unauthorized 429 rate limited",
        "CHANGE MANAGEMENT REQUEST Change Reference CHG-2024-0892 Type Standard change System Payment Gateway Description Update TLS version 1.2 to 1.3 Risk Low Impact minimal downtime expected Testing completed staging Approval CAB approved Rollback plan available",
    ],

    "Operations": [
        "STANDARD OPERATING PROCEDURE Document Control No SOP-OPS-2024-15 Title Warehouse Receiving Process Scope all inbound goods Purpose ensure accurate receipt inspection storage Steps 1 Verify delivery docket 2 Inspect goods damage 3 Scan barcode system 4 Allocate storage location Review Annual",
        "VENDOR AGREEMENT Supplier FastFreight Logistics Client ManuFacture Corp Services Freight forwarding warehousing distribution Term 2 years from 1 January 2024 KPIs on time delivery 98 percent damage rate below 0.5 percent Payment 45 days EOM Penalties SLA breach 2 percent invoice",
        "MAINTENANCE LOG Equipment CNC Machine Model Haas VF2 Serial HV24892 Location Workshop Bay 3 Date 20 March 2024 Technician Bob Martinez Work Performed scheduled maintenance spindle bearings replaced coolant flush Next Service due 3 months or 500 hours Parts Used bearings 4",
        "SUPPLY CHAIN REPORT Quarter 1 2024 Supplier Performance 95 percent on time 98 percent quality Inventory Turnover 8.2 times Stock Days on Hand 44 days Out of Stock Events 12 Backorders resolved 9 Freight Costs 2.3 percent revenue Recommendations consolidate suppliers reduce SKUs",
        "FACILITY MANAGEMENT REPORT Building 2 Industrial Park Monthly Report March 2024 Preventive Maintenance completed HVAC electrical plumbing Security incidents 0 Cleaning Services satisfactory Energy Consumption 45000 kWh 8 percent reduction Capital Works lift upgrade Q2 budget 120000",
        "PRODUCTION SCHEDULE Week commencing 18 March 2024 Product A Target 5000 units Actual 4890 Variance minus 2.2 percent Product B Target 3200 Actual 3210 Variance plus 0.3 percent Downtime reasons equipment 2 hours material shortage 1 hour Efficiency Rate 94.5 percent",
        "LOGISTICS MANIFEST Shipment ID SHP-2024-8923 Origin Melbourne Distribution Centre Destination Brisbane Customer Service Centre Carrier StarTrack Express Items 234 cartons Weight 1240kg Volume 8.5 cubic metres Dispatch Date 22 March 2024 ETA 25 March 2024 Reference PO-88234",
        "HEALTH SAFETY ENVIRONMENT REPORT Monthly HSE Report February 2024 LTI Frequency Rate 0 Lost Time Injuries 0 Near Miss Reports 8 Hazard Identifications 23 resolved 19 Toolbox Talks completed 12 PPE compliance 99 percent Environmental incidents 0 Audit scheduled April",
        "CONTRACTOR MANAGEMENT DOCUMENT Contractor Approval Form Company BuildRight Services Work Type Electrical maintenance Site Entry 1 April to 30 June 2024 Induction completed 28 March Insurance public liability 20 million workers compensation current SWMS reviewed approved",
        "INVENTORY MANAGEMENT REPORT End of Month March 2024 Opening Stock Value 2340000 Purchases 890000 Cost of Goods Sold 1100000 Closing Stock 2130000 Slow Moving Items 145 SKUs write down recommended Stocktake Variance 0.8 percent within acceptable threshold",
        "FLEET MANAGEMENT REPORT March 2024 Total Vehicles 45 Operational 42 In Service 3 Average Kilometres 12400 Fuel Consumption 11.2 litres per 100km Registration Renewals due April 8 vehicles Insurance renewal June 2024 Incidents minor 2 no fault Maintenance costs 23400",
        "QUALITY CONTROL REPORT Production Run QC-2024-892 Product Electronic Components Batch Size 10000 Sample Tested 500 Defects Found 12 Defect Rate 2.4 percent Target below 1.5 percent Action Initiated production line review supplier component quality audit scheduled",
    ],
}


def get_training_samples() -> tuple:
    """
    Returns (texts, labels) ready for sklearn training.
    texts: list of document strings
    labels: list of department names
    """
    texts = []
    labels = []
    for department, samples in TRAINING_DATA.items():
        for sample in samples:
            texts.append(sample)
            labels.append(department)
    return texts, labels


def get_department_counts() -> dict:
    """Return count of training samples per department."""
    return {dept: len(samples) for dept, samples in TRAINING_DATA.items()}


if __name__ == "__main__":
    texts, labels = get_training_samples()
    print(f"Total training samples: {len(texts)}")
    for dept, count in get_department_counts().items():
        print(f"  {dept}: {count} samples")
