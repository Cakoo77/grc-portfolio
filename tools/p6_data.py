"""Project 6 third-party risk management content for the fictional Orvanta Payments UAB.

All wording is original: the questionnaire is not copied from SIG, CAIQ or any other published set.
Supplier answers, findings and contract terms are simulated. Real vendors appear only as tools Orvanta uses,
and nothing here describes their actual security.
"""

AS_OF = "31 August 2027"
PROCEDURE_DATE = "13 August 2027"
REPORT_DATE = "31 August 2027"

# vendor id -> (owner, data sensitivity 0-3, business criticality 0-3, system access 0-2, assessed date or None, rating or None, contract renewal, checklist status)
VENDORS = {
    "VEN-01": ("R-HSRE", 3, 3, 0, "19 Mar 2027", "Low", "31 Jan 2028", "Complete"),
    "VEN-02": ("R-HCARD", 3, 3, 1, "20 Aug 2027", None, "30 Jun 2028", "Partial"),
    "VEN-03": ("R-HCOMP", 3, 3, 0, "18 Jun 2027", "Medium", "31 Mar 2028", "Complete"),
    "VEN-04": ("R-TREAS", 2, 3, 0, "27 Aug 2027", None, "31 Dec 2028", "Partial"),
    "VEN-05": ("R-SUPMGR", 3, 2, 2, "30 Jul 2027", None, "31 May 2029", "Partial"),
    "VEN-06": ("R-ITOPS", 2, 3, 0, "26 Mar 2027", "Low", "30 Sep 2028", "Complete"),
    "VEN-07": ("R-CTO", 3, 3, 0, "9 Apr 2027", "Low", "30 Apr 2028", "Complete"),
    "VEN-08": ("R-HSRE", 2, 3, 0, "21 May 2027", "Low", "31 Jul 2028", "Complete"),
    "VEN-09": ("R-ITOPS", 2, 2, 0, "28 May 2027", "Low", "31 Oct 2028", "Complete"),
    "VEN-10": ("R-HPAY", 2, 2, 0, None, None, "28 Feb 2028", "At renewal"),
    "VEN-11": ("R-SUPMGR", 2, 2, 0, "11 Jun 2027", "Low", "30 Nov 2027", "Complete"),
    "VEN-12": ("R-HSRE", 1, 2, 0, None, None, "31 Mar 2028", "At renewal"),
    "VEN-13": ("R-ITOPS", 2, 1, 0, None, None, "31 Jan 2028", "At renewal"),
    "VEN-14": ("R-CTO", 2, 1, 0, None, None, "30 Jun 2028", "At renewal"),
    "VEN-15": ("R-ITOPS", 1, 2, 2, None, None, "31 May 2028", "At renewal"),
    "VEN-16": ("R-HPEOPLE", 2, 1, 0, None, None, "31 Dec 2027", "At renewal"),
    "VEN-17": ("R-CISO", 2, 1, 1, None, None, "28 Feb 2028", "At renewal"),
    "VEN-18": ("R-HCOMP", 2, 1, 0, None, None, "31 Dec 2027", "At renewal"),
    "VEN-19": ("R-CFO", 2, 1, 0, None, None, "30 Apr 2028", "At renewal"),
    "VEN-20": ("R-ITOPS", 0, 1, 0, None, None, "31 Aug 2028", "Not required"),
}
ASSESSED = ["VEN-02", "VEN-04", "VEN-05"]

DOMAINS = ["Governance and assurance", "Access control", "Data protection", "Endpoint and network security", "Vulnerability and change management",
           "Logging and monitoring", "Incident management", "Business continuity", "People security", "Subcontractors and compliance"]
# question, evidence we ask for, key question (True doubles the weight and triggers the High floor when answered No)
QUESTIONS = [
    ("Do you have a named person accountable for information security?", "Role description or organization chart", True),
    ("Do you hold a current independent security certificate or assurance report covering the service we buy?", "Certificate or report, with scope and date", True),
    ("Do you have approved security policies that staff must follow?", "Policy list with approval dates", False),
    ("Do you assess information security risks at least once a year?", "Summary of the latest risk assessment", False),
    ("Do you test your own controls through internal audit or a similar review?", "Audit plan or latest report summary", False),
    ("Will you tell us before you make a significant change to the service or to how it is secured?", "Change notification clause or process", False),
    ("Does every person who can reach our data have their own named account?", "Account policy and a sample user list", True),
    ("Is multi-factor authentication required for all remote and administrative access?", "Configuration evidence", True),
    ("Is access granted on least privilege, with approval?", "Sample access requests", False),
    ("Do you review access rights at least twice a year?", "Latest review record", False),
    ("Do you remove access within one working day when someone leaves or changes role?", "Leaver procedure and a sample", False),
    ("Are privileged actions logged and reviewed?", "Log sample and review record", False),
    ("Is our data encrypted in transit and at rest, including on staff devices?", "Encryption standard and configuration", True),
    ("Is our data kept logically separate from other customers' data?", "Architecture description", False),
    ("Can you name every country where our data is stored or accessed from?", "Data location list", True),
    ("Do you return or delete our data at the end of the contract and confirm it in writing?", "Deletion procedure", False),
    ("Do you limit and monitor copying of our data to removable media and personal devices?", "Device control settings", False),
    ("Do you have a data protection contact and a record of processing for our data?", "Contact details and record extract", False),
    ("Are all devices that handle our data centrally managed, with disk encryption?", "Device management report", True),
    ("Do those devices run anti-malware or EDR that staff cannot switch off?", "Coverage report", False),
    ("Are systems that handle our data separated from the rest of your network?", "Network diagram", False),
    ("Are internet-facing systems protected by a firewall or equivalent filtering?", "Configuration summary", False),
    ("Do staff handle our data only from approved locations and devices?", "Remote working rules", False),
    ("Is physical access to places where our data is handled controlled and logged?", "Access logs or site description", False),
    ("Do you scan for vulnerabilities at least monthly?", "Scan schedule and a sample report", False),
    ("Do you fix critical vulnerabilities within a defined time?", "Policy and remediation statistics", True),
    ("Do you commission an independent penetration test at least once a year?", "Test summary or attestation", False),
    ("Are changes to production reviewed and approved by a second person?", "Sample change records", False),
    ("Are development, test and production environments kept separate?", "Environment description", False),
    ("Do you keep an inventory of the third-party software components you use?", "Component inventory", False),
    ("Do you log access to our data and administrative activity?", "Log sample", True),
    ("Do you keep security logs for at least 12 months?", "Retention setting", False),
    ("Do you monitor for security events at all hours?", "Monitoring arrangement", False),
    ("Are logs protected from change by the people whose actions they record?", "Log architecture", False),
    ("Are alerts reviewed within one working day?", "Triage records", False),
    ("Can you give us logs about our data when we need them for an investigation?", "Process description", False),
    ("Do you have a documented incident response plan?", "Plan summary", True),
    ("Have you tested that plan in the last 12 months?", "Exercise record", False),
    ("Will you notify us within 24 hours of an incident affecting our data or service?", "Contract clause or procedure", True),
    ("Do you have a named security contact who can be reached at all hours?", "Contact details", False),
    ("Will you share the root cause and corrective actions after an incident?", "Sample post-incident report", False),
    ("Have you been free of incidents affecting customer data for 24 months, or can you show what you changed after one?", "Incident summary", False),
    ("Do you have a business continuity plan for the service we buy?", "Plan summary", True),
    ("Have you set recovery time and recovery point objectives for it?", "Objectives", False),
    ("Have you tested recovery in the last 12 months?", "Test record", False),
    ("Are backups stored separately from production and tested?", "Backup design and restore record", False),
    ("Can the service continue if one site or region fails?", "Resilience design", False),
    ("Do you have a plan to help us move to another provider or bring the service in house?", "Exit assistance terms", False),
    ("Do you screen staff before they handle our data?", "Screening policy", True),
    ("Do staff sign confidentiality terms?", "Template", False),
    ("Do all staff complete security training at least once a year?", "Completion rate", False),
    ("Do you run phishing simulations or similar tests?", "Results summary", False),
    ("Is there a disciplinary process for security breaches?", "Policy extract", False),
    ("Do staff who handle our data get training specific to it, such as handling card numbers?", "Training content", False),
    ("Will you tell us which subcontractors handle our data, and tell us before adding one?", "Subcontractor list and clause", True),
    ("Do you assess the security of those subcontractors?", "Assessment records", False),
    ("Do you pass our security requirements on to them by contract?", "Contract template", False),
    ("Do you accept our right to audit, or provide independent assurance in its place?", "Audit clause", True),
    ("Will you cooperate with our regulators if they ask?", "Contract clause", False),
    ("Do you hold insurance that covers security incidents?", "Certificate", False),
]
ANSWER = {"Y": "Yes", "P": "Partial", "N": "No", "A": "N/A"}
# one letter per question, in order, six per domain
ANSWERS = {
    "VEN-02": "YYYYYP YYYYYY YYYPYY YYYYYY YYYYYY YYYYYP YYYYYY YYYYYP YYYYYY PYYYYY",
    "VEN-04": "YYYYYP YYYYYY YYYYYY YYYYYY YYPYYP YYYYYN YYPYPY YYYYYP YYYYYY YYYPYY",
    "VEN-05": "YNYPNY PNYNYN PAYYNY NYYYYY YNNAAA PNNYNY PNNYYY NNNYNP PYYNYY YAAPYN",
}
RATING_BANDS = [("Low", 0.85, "Meets Orvanta's requirements, with minor points at most"), ("Medium", 0.70, "Gaps that need a remediation plan, without a time limit on the relationship"),
                ("High", 0.50, "Serious gaps. The relationship continues only with conditions, deadlines and interim controls"),
                ("Critical", 0.0, "Does not meet minimum requirements. Do not onboard, or plan an exit")]

# id, vendor, severity, finding, question refs, what Orvanta requires, due, interim control
FINDINGS = [
    ("SF-01", "VEN-05", "High", "Agents sign in to shared shift desktops with a password only. Multi-factor authentication protects Orvanta's tools, but not Helvora's own systems.", "Q07, Q08",
     "Named accounts and multi-factor authentication on every device and system used for Orvanta work", "31 Oct 2027", "Orvanta restricts Orbit and Zendesk sign-in to Helvora's office network range"),
    ("SF-02", "VEN-05", "High", "Shift desktops are not centrally managed and have no disk encryption. Removable storage is not blocked, and no deadline is set for security updates.", "Q13, Q17, Q19, Q26",
     "Managed, encrypted devices with removable storage blocked, or use of Orvanta-provided virtual desktops", "31 Oct 2027", "Bulk export disabled for agent roles. Monthly review of agent downloads"),
    ("SF-03", "VEN-05", "High", "No incident notification time is agreed, and the incident process is informal and untested.", "Q37, Q38, Q39",
     "A written incident plan, a yearly test, and notification to Orvanta within 24 hours, added to the contract", "30 Sep 2027", "Helvora's site manager added to Orvanta's incident call list"),
    ("SF-04", "VEN-05", "High", "There is no business continuity plan for the support service, which runs from one site in Riga.", "Q43, Q44, Q45, Q47",
     "A continuity plan with recovery objectives agreed with Orvanta, tested once a year", "30 Nov 2027", "Orvanta's in-house team can take priority tickets for up to five working days"),
    ("SF-05", "VEN-05", "Medium", "Helvora holds no independent certificate or assurance report and does not audit its own controls.", "Q02, Q04, Q05",
     "A yearly independent review of the controls in this plan, shared with Orvanta", "31 Mar 2028", "Orvanta reassesses on site every six months until then"),
    ("SF-06", "VEN-05", "Medium", "Screening covers identity only. Access is not reviewed, and privileged actions are not logged on Helvora's side.", "Q10, Q12, Q49",
     "Reference checks for agents on Orvanta work, and a six-monthly access review shared with Orvanta", "30 Nov 2027", "Orvanta reviews agent accounts in its own tools every quarter"),
    ("SF-07", "VEN-05", "Medium", "Security logs are kept for 90 days and nobody monitors them outside office hours.", "Q31, Q32, Q33, Q35",
     "Twelve months of retention for systems used on Orvanta work, and a named contact for alerts", "31 Dec 2027", "Agent activity is logged in Orvanta's own systems and monitored in its SIEM"),
    ("SF-08", "VEN-02", "Low", "Tessarin lists its subcontractors on request, but does not commit to telling Orvanta before adding one.", "Q55",
     "Advance notice of new subcontractors that handle Orvanta data, added at renewal", "30 Jun 2028", "Orvanta requests the list every six months"),
    ("SF-09", "VEN-02", "Low", "Exit assistance and the format for returning data are described only in general terms.", "Q16, Q48",
     "An exit schedule naming data formats, timescales and support, added at renewal", "30 Jun 2028", "Exit options are covered in Orvanta's continuity plan"),
    ("SF-10", "VEN-04", "Medium", "The contract requires notification of incidents without undue delay, with no fixed time, and gives no commitment to share root causes.", "Q39, Q41",
     "A defined notification time and a post-incident report, by contract addendum", "31 Dec 2027", "Treasury holds a direct escalation contact at the bank"),
    ("SF-11", "VEN-04", "Low", "The bank shares neither penetration test summaries nor logs about Orvanta's connection, and limits audit to its assurance report.", "Q27, Q36, Q58",
     "A yearly summary of independent testing, and agreed log extracts for investigations", "31 Dec 2028", "Orvanta logs every file transfer on its own side"),
]

# clause, what it must cover (our wording), then status for VEN-02, VEN-04, VEN-05 before remediation
CLAUSES = [
    ("Security requirements", "A schedule of the security measures the supplier must keep in place", ("Present", "Present", "Missing")),
    ("Confidentiality", "Protection of Orvanta information during and after the contract", ("Present", "Present", "Present")),
    ("Personal data", "A data processing agreement with instructions, safeguards and locations", ("Present", "Present", "Present")),
    ("Incident notification", "Notice within an agreed time, with facts, impact and contact", ("Present", "Partial", "Missing")),
    ("Assurance and audit", "Right to audit, or independent assurance reports in its place", ("Present", "Partial", "Missing")),
    ("Subcontractors", "Disclosure, advance notice and flow-down of requirements", ("Partial", "Present", "Present")),
    ("Data location", "Countries where data is stored and accessed, with notice of change", ("Present", "Present", "Partial")),
    ("Access to Orvanta systems", "Named accounts, multi-factor authentication and prompt removal", ("Present", "Present", "Partial")),
    ("Staff screening and training", "Screening before access, and training relevant to the data", ("Present", "Present", "Partial")),
    ("Service levels and continuity", "Availability targets, recovery objectives and continuity testing", ("Present", "Present", "Missing")),
    ("Cooperation with regulators", "Support for supervisory requests and inspections", ("Present", "Present", "Missing")),
    ("Change notification", "Advance notice of significant service or security changes", ("Partial", "Partial", "Missing")),
    ("Termination rights", "Right to end the contract for serious security failure", ("Present", "Present", "Partial")),
    ("Exit and data return", "Assistance, formats, timescales and confirmed deletion", ("Partial", "Partial", "Missing")),
    ("Liability and insurance", "Responsibility for security failures, backed by insurance", ("Present", "Present", "Partial")),
]

# vendor: function supported, data location, known subcontractors, substitutability, exit plan status
REGISTER = {
    "VEN-01": ("All production hosting (BP-01 to BP-05, BP-10)", "EU: Frankfurt, with backup copy in a second EU region", "None relevant to the service", "Hard", "Considerations documented in the cloud standard"),
    "VEN-02": ("Card program operations (BP-04)", "EU", "Listed on request. See SF-08", "Hard", "Exit schedule due at renewal. See SF-09"),
    "VEN-03": ("Merchant onboarding and AML monitoring (BP-06, BP-07)", "EU", "Two, disclosed", "Medium", "Documented in the continuity plan"),
    "VEN-04": ("Payouts, settlement and safeguarding (BP-02, BP-05)", "EU: Lithuania", "None relevant to the service", "Hard", "Documented in the continuity plan"),
    "VEN-05": ("Customer support (BP-08)", "EU: Latvia", "None", "Medium", "In-house fallback for five working days"),
    "VEN-06": ("Workforce identity (BP-11)", "EU", "Disclosed in public list", "Hard", "Break-glass accounts and documented fallback"),
    "VEN-07": ("Software delivery (BP-09)", "EU and US", "Disclosed in public list", "Medium", "Repository mirrors and documented fallback"),
    "VEN-08": ("Payment acceptance edge (BP-01)", "Global network", "Disclosed in public list", "Medium", "Direct-to-origin fallback tested in June 2027"),
}

LIFECYCLE = [("Onboard", "Register the supplier, name an owner and set the tier"), ("Assess", "Run due diligence at the depth the tier requires"),
             ("Contract", "Agree clauses from the checklist. No signature without sign-off"), ("Monitor", "Review on schedule and after incidents or changes"),
             ("Offboard", "Remove access, recover or destroy data, close the record")]
# stage, step, action, who, record
STEPS = [
    ("Onboard", "1", "Raise a supplier request before any commitment, stating the service, the data involved and the systems the supplier will reach.", "Supplier owner", "Jira request"),
    ("Onboard", "2", "Rate data sensitivity, business criticality and system access, and let the workbook set the tier.", "Head of Compliance", "Inventory entry"),
    ("Onboard", "3", "Decide whether the service supports a critical or important function under DORA.", "Head of Compliance, General Counsel", "Register entry"),
    ("Assess", "4", "Send the questionnaire at the depth for the tier, and collect the evidence it asks for.", "Head of Compliance", "Questionnaire and evidence"),
    ("Assess", "5", "Score the answers, verify key answers against evidence, and record findings.", "Security assessor", "Scored assessment"),
    ("Assess", "6", "Agree a remediation plan for each finding, with dates and interim controls.", "Supplier owner", "Findings register"),
    ("Assess", "7", "Decide: approve, approve with conditions, or reject. High and Critical ratings go to the CISO, and Tier 1 with a High rating to the CEO.", "CISO, CEO", "Decision record"),
    ("Contract", "8", "Draft or amend the contract using the clause checklist.", "General Counsel", "Completed checklist"),
    ("Contract", "9", "Obtain third-party risk sign-off in the contract workflow. The workflow blocks signature without it.", "Head of Compliance", "Workflow approval"),
    ("Monitor", "10", "Reassess Tier 1 every year and Tier 2 every two years. Track the expiry of assurance reports.", "Head of Compliance", "Inventory dates"),
    ("Monitor", "11", "Reassess after a supplier incident, a significant change or a new subcontractor.", "Supplier owner", "Triggered review"),
    ("Monitor", "12", "Follow up open findings every month and escalate missed dates to the CISO.", "Head of Compliance", "Findings register"),
    ("Monitor", "13", "Report the supplier risk position to the ISMS steering meeting every month.", "Head of Compliance", "Dashboard"),
    ("Offboard", "14", "Remove the supplier's access to Orvanta systems on the last day of service.", "IT Operations", "Access ticket"),
    ("Offboard", "15", "Recover or destroy Orvanta data and obtain written confirmation.", "Supplier owner", "Confirmation letter"),
    ("Offboard", "16", "Close the inventory and register entries, and record lessons learned.", "Head of Compliance", "Closed record"),
]
DEPTH = [("Tier 1", "Full questionnaire of 60 questions, evidence for every key question, and a call or site visit", "Before contract, then every year"),
         ("Tier 2", "The 15 key questions, plus any domain relevant to the service", "Before contract, then every two years"),
         ("Tier 3", "No questionnaire. Confidentiality terms and a named owner are enough", "Review at renewal")]
