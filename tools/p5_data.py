"""Project 5 internal audit and management review content for the fictional Orvanta Payments UAB.

All wording is original. Standards are cited by clause number, control ID and short name only.
Audit evidence, samples and people from the audit firm are simulated.
"""

AUDIT_ID = "IA-2027-01"
AUDIT_DATES = "12 to 16 July 2027"
REPORT_DATE = "23 July 2027"
CAP_DATE = "6 August 2027"
REVIEW_DATE = "26 August 2027"
KPI_DATE = "31 July 2027"
LEAD = "Rasa Kavaliauskaitė"
AUDITOR = "Dovydas Petkus"
FIRM = "Rivenmark Assurance UAB"
INDEPENDENCE = ("Portfolio note: one author prepared both the implementation documents and these audit documents, to show both skills. In a real engagement the people who build an ISMS do not audit it. "
                "Here the audit is carried out by a fictional external team that had no part in the implementation.")

# id, year, month, title, type, focus
PROGRAMME = [
    ("IA-2027-01", 2027, "Jul", "Full ISMS audit", "Full", "All clauses and a risk-based sample of Annex A, before Stage 1"),
    ("IA-2027-02", 2027, "Oct", "Follow-up audit", "Follow-up", "Closure and effectiveness of corrective actions, before Stage 2"),
    ("IA-2028-01", 2028, "Feb", "Identity, access and people", "Themed", "Access lifecycle, privileged access, screening and training"),
    ("IA-2028-02", 2028, "May", "Suppliers and outsourcing", "Themed", "Third-party risk program, contracts and the DORA register"),
    ("IA-2028-03", 2028, "Sep", "Management system and delivery", "Themed", "Clauses 4 to 10, secure development and change, before surveillance"),
    ("IA-2029-01", 2029, "Feb", "Resilience", "Themed", "Incident response, continuity, backup and recovery"),
    ("IA-2029-02", 2029, "May", "Detection and cloud", "Themed", "Logging, monitoring, cloud configuration and cryptography"),
    ("IA-2029-03", 2029, "Sep", "Full ISMS audit", "Full", "All clauses and remaining Annex A, before recertification planning"),
]
# area, risk rating, then one mark per audit in PROGRAMME order: F full, S sample, - none
COVERAGE = [
    ("Clauses 4 to 10", "High", "F S - - F - - F".split()),
    ("Risk management and SoA", "High", "F S - - F - - F".split()),
    ("Identity and access", "High", "F S F - - - S F".split()),
    ("Suppliers and outsourcing", "High", "F F - F - - - F".split()),
    ("Logging and monitoring", "High", "F S - - - - F F".split()),
    ("Incident and continuity", "High", "F - - - - F - F".split()),
    ("Backup and recovery", "High", "F - - - - F - S".split()),
    ("Secure development and change", "High", "F - - - F - - S".split()),
    ("Endpoints and remote working", "Medium", "F - S - - - - F".split()),
    ("Data protection and cryptography", "Medium", "S - - - - - F F".split()),
    ("People security", "Medium", "S S F - - - - S".split()),
    ("Physical security", "Low", "S - - - - - - F".split()),
]

# day, time, activity, auditor, auditees
SCHEDULE = [
    ("Mon 12 Jul", "09:00", "Opening meeting", "Both", "CEO, CISO, CTO, Head of Compliance"),
    ("Mon 12 Jul", "10:00", "Context, scope, leadership, objectives (clauses 4, 5, 6.2)", LEAD, "CEO, CISO"),
    ("Mon 12 Jul", "13:30", "Risk assessment, treatment and SoA (clauses 6.1, 8.2, 8.3)", LEAD, "Risk Manager, CISO"),
    ("Mon 12 Jul", "13:30", "Asset management and classification", AUDITOR, "IT Operations Lead"),
    ("Tue 13 Jul", "09:00", "Suppliers and outsourced processes (clause 8.1)", LEAD, "Head of Compliance, General Counsel"),
    ("Tue 13 Jul", "09:00", "Identity, access lifecycle and privileged access", AUDITOR, "IT Operations Lead, Head of Platform and SRE"),
    ("Tue 13 Jul", "13:30", "People security: screening, induction, training (clauses 7.2, 7.3)", LEAD, "Head of People"),
    ("Tue 13 Jul", "13:30", "Endpoints and remote working, including Baku by video", AUDITOR, "IT Operations Lead"),
    ("Wed 14 Jul", "09:00", "Logging, monitoring and incident management", AUDITOR, "CISO, Security Engineer"),
    ("Wed 14 Jul", "09:00", "Documented information and document control (clause 7.5)", LEAD, "CISO"),
    ("Wed 14 Jul", "13:30", "Backup, recovery and continuity", AUDITOR, "Head of Platform and SRE, COO"),
    ("Wed 14 Jul", "13:30", "Privacy, transfers and legal register", LEAD, "DPO, Head of Compliance"),
    ("Thu 15 Jul", "09:00", "Secure development, change and vulnerability management", AUDITOR, "CTO, Head of Payments Engineering"),
    ("Thu 15 Jul", "09:00", "Monitoring, measurement and corrective action (clauses 9.1, 10)", LEAD, "CISO"),
    ("Thu 15 Jul", "13:30", "Cryptography, physical security walkthrough in Vilnius", AUDITOR, "Head of Platform and SRE, COO"),
    ("Thu 15 Jul", "15:00", "Follow-up sampling and open points", "Both", "As needed"),
    ("Fri 16 Jul", "09:00", "Audit team review and finding classification", "Both", "-"),
    ("Fri 16 Jul", "14:00", "Closing meeting", "Both", "CEO, CISO, CTO, Head of Compliance, auditees"),
]

RESULT = {"C": "Conforms", "MA": "Major nonconformity", "MI": "Minor nonconformity", "OB": "Observation", "OFI": "Opportunity for improvement", "ND": "Not yet due"}

# id, area, criteria, question, evidence sought, sampling, auditee, result, what the auditor saw, finding
CHECKLIST = [
    ("Q01", "Context and scope", "Clause 4.3", "Is the ISMS scope documented, and does it match how Orvanta operates?", "ISMS Manual, architecture, supplier list", "Whole document", "R-CISO", "C", "Scope matches products, sites and systems seen during the week. Supplier boundaries are stated.", "-"),
    ("Q02", "Context and scope", "Clauses 4.1, 4.2", "Are issues and interested parties identified, including the climate change determination?", "Context and parties tables", "Whole document", "R-CISO", "C", "Ten issues and eleven parties recorded. Climate relevance decided and reasoned.", "-"),
    ("Q03", "Leadership", "Clauses 5.1, 5.2", "Does top management show commitment, and is the policy approved and known?", "Policy approval, Board minutes, staff interviews", "CEO interview, 6 staff asked", "R-CEO", "C", "Policy approved 19 February 2027. All six staff could find it and name the report channel.", "-"),
    ("Q04", "Leadership", "Clause 5.3", "Are security roles assigned and understood?", "RACI, role descriptions", "5 role-holders interviewed", "R-CISO", "C", "RACI in use. The CISO reports to the CEO. Control owners knew their controls.", "-"),
    ("Q05", "Risk management", "Clause 6.1.2", "Is the risk method applied consistently?", "Risk register, workshop records", "8 of 30 risks", "R-RISK", "C", "All eight followed the method, with owner, three scores and criteria applied as defined.", "-"),
    ("Q06", "Risk management", "Clause 6.1.3", "Is the Statement of Applicability complete, justified and current?", "SoA, evidence register", "15 of 93 controls", "R-RISK", "OB", "Justifications sound. Version 1.1 is dated 30 April, and at least 14 controls have changed status since.", "OBV-01"),
    ("Q07", "Risk management", "Clause 8.3", "Are accepted risks managed under the acceptance rules?", "Acceptance record RA-01 and its conditions", "The one acceptance", "R-HSRE", "MI", "Recovery runbook condition, due 30 June, not met. No escalation and no tracking of conditions.", "NC-05"),
    ("Q08", "Objectives", "Clause 6.2", "Are objectives measurable, monitored and resourced?", "Objectives table, KPI dashboard", "All 10 objectives", "R-CISO", "C", "All ten have baseline, target, owner and monthly readings. Two targets were missed and are reported openly.", "-"),
    ("Q09", "Competence", "Clause 7.2", "Is competence defined and evidenced for security roles?", "Competence matrix, training records", "6 role-holders", "R-HPEOPLE", "C", "Matrix exists. Records support all six, including the security hire who joined in March.", "-"),
    ("Q10", "Awareness", "Clause 7.3, A.6.3, HR-04", "Do new joiners complete induction before production access?", "Training records, Okta group history", "15 of 22 joiners, Feb to Jun", "R-HPEOPLE", "MI", "Three joiners held production access two to six days before induction was recorded as complete.", "NC-04"),
    ("Q11", "Documented information", "Clause 7.5.3", "Are documents in use the current approved versions?", "Documents seen in use during interviews", "12 documents", "R-CISO", "MI", "Two superseded copies in use: a draft policy PDF in Baku and an old restore runbook in Google Drive.", "NC-03"),
    ("Q12", "Operations", "Clause 8.1", "Are outsourced processes identified and controlled?", "Third-party risk register, contracts", "All 8 Tier 1 suppliers", "R-HCOMP", "MA", "Three of eight Tier 1 suppliers unassessed past target. One critical contract renewed without assessment.", "NC-01"),
    ("Q13", "Risk management", "Clause 8.2", "Are risk assessments repeated at planned intervals and on change?", "Register history, change triggers", "3 change-triggered reviews", "R-RISK", "C", "Quarterly review done in April. Three targeted reviews followed architecture changes.", "-"),
    ("Q14", "Performance", "Clause 9.1", "Is it clear what is measured, how and by whom?", "KPI definitions, data sources", "10 KPIs", "R-CISO", "OB", "Results are reported, but two KPIs are calculated differently by different people and no definitions are written.", "OBV-02"),
    ("Q15", "Performance", "Clause 9.2", "Is there an audit programme, and are auditors independent?", "Programme, auditor records", "Whole programme", "R-HCOMP", "C", "Three-year programme approved. This audit is its first. Auditors had no part in implementation.", "-"),
    ("Q16", "Performance", "Clause 9.3", "Does top management review the ISMS?", "Review schedule and agenda", "-", "R-CEO", "ND", "First review is scheduled for 26 August 2027. Quarterly checkpoints were held in February and May.", "-"),
    ("Q17", "Improvement", "Clause 10.2", "Are nonconformities corrected and causes addressed?", "Corrective action register", "5 of 11 entries", "R-CISO", "C", "All five had a cause, action, owner and closure evidence. Three had an effectiveness check.", "-"),
    ("Q18", "Assets", "A.5.9, AM-01, AM-02", "Is the asset register complete and reconciled?", "Register against Jamf, Terraform and Okta", "25 assets", "R-ITOPS", "C", "All 25 found in the source systems with an owner. Monthly reconciliation records seen for April to June.", "-"),
    ("Q19", "Assets", "A.5.12, A.5.13, AM-04 to AM-06", "Is information classified and labelled?", "Scheme, shared drives", "10 shared drives", "R-ITOPS", "C", "All ten carried the correct label. Staff could explain the four levels.", "-"),
    ("Q20", "Access", "A.5.15, A.5.16, AC-01 to AC-03", "Are identities named, with no shared accounts?", "Okta and AWS account lists", "All admin accounts", "R-ITOPS", "C", "No shared accounts found. The legacy AWS account was closed on 28 May 2027.", "-"),
    ("Q21", "Access", "A.5.17, AC-06, AC-07", "Are secrets kept out of code and laptops?", "Secret scanning results, pipeline roles", "All production repositories", "R-HSRE", "C", "No long-lived cloud keys found. Pipelines use short-lived roles.", "-"),
    ("Q22", "Access", "A.5.18, AC-13, ORV-PRC-01", "Is leaver access removed within 24 hours, everywhere?", "Leaver tickets, Okta logs, tools outside SSO", "10 of 14 leavers, Apr to Jun", "R-ITOPS", "MI", "Okta suspension within 21 hours for all ten. Two had no checklist for other tools, and one token stayed live for nine days.", "NC-02"),
    ("Q23", "Access", "A.5.18, AC-14", "Do system owners review access every quarter?", "Review records", "6 of 26 systems, Q1 review", "R-ITOPS", "C", "All six reviews completed within 10 working days. 14 access rights removed as a result.", "-"),
    ("Q24", "Suppliers", "A.5.19, A.5.20, A.5.22, SU-02, SU-03", "Are suppliers assessed before contract, and do contracts carry the required clauses?", "Assessments, contract checklist", "All 8 Tier 1 suppliers, 5 contracts", "R-HCOMP", "MA", "Same evidence as Q12. The Helvora renewal of 1 June 2027 had no assessment and no completed checklist.", "NC-01"),
    ("Q25", "Suppliers", "A.5.23, SU-09", "Is cloud use governed by a standard?", "Cloud security standard", "Whole document", "R-HSRE", "C", "Standard and shared responsibility matrix approved in June.", "-"),
    ("Q26", "Incidents", "A.5.24 to A.5.26, IM-01 to IM-08", "Is incident response planned, tested and followed?", "Plan, playbooks, tabletop record, incident record", "1 exercise, 1 incident", "R-CISO", "C", "Tabletop held in May. The Severity 2 incident of 18 May followed the plan and was contained in 40 minutes.", "-"),
    ("Q27", "Incidents", "A.5.27, A.5.28, IM-09, IM-10", "Are incidents reviewed and evidence preserved?", "Post-incident review, evidence log", "The one incident", "R-CISO", "C", "Review completed in six working days. Three actions raised and closed.", "-"),
    ("Q28", "Continuity", "A.5.29, A.5.30, BR-08, BR-10", "Are recovery objectives set and continuity plans in place?", "BIA, continuity plan", "Whole documents", "R-COO", "C", "BIA approved 28 May 2027 with objectives for six critical services. First continuity exercise is planned for September.", "-"),
    ("Q29", "Privacy", "A.5.34, A.5.14, AM-08", "Are transfers to Baku covered by safeguards?", "Transfer impact assessment, access configuration", "5 Baku engineers' access", "R-DPO", "C", "Assessment approved in May. All five saw masked data by default.", "-"),
    ("Q30", "Compliance", "A.5.31, IS-13", "Is there a register of legal and contractual requirements?", "Legal register", "10 entries", "R-HCOMP", "C", "Register approved in June. All ten entries had an owner and a review date.", "-"),
    ("Q31", "People", "A.6.1, A.6.2, HR-01, HR-02", "Are people screened and under contract terms before they start?", "Screening and contract records", "10 of 22 joiners", "R-HPEOPLE", "C", "All ten screened before start, with signed terms.", "-"),
    ("Q32", "Endpoints", "A.8.1, A.6.7, RW-01 to RW-03", "Are all laptops managed and protected?", "Jamf and EDR reports, device checks", "20 of 131 laptops", "R-ITOPS", "C", "All 20 enrolled, encrypted and running EDR. A test sign-in from an unmanaged device was blocked.", "-"),
    ("Q33", "Physical", "A.7.1 to A.7.4, IS-20, IS-21", "Are office perimeters and entry controlled?", "Walkthrough, visitor log", "Vilnius on site, Baku by video", "R-COO", "C", "Badge entry and visitor log working in Vilnius. Baku reception control confirmed by video.", "-"),
    ("Q34", "Access", "A.8.2, AC-08, AC-09", "Is privileged access just in time, approved and reviewed?", "Access request logs, review records", "15 requests, 1 break-glass use", "R-HSRE", "C", "All 15 approved by a second person and expired on time. The break-glass use was reviewed the next day.", "-"),
    ("Q35", "Access", "A.8.5, AC-04, AC-05", "Is every workforce tool behind MFA?", "Okta application report against asset register", "All 31 workforce tools", "R-ITOPS", "C", "All 31 behind Okta MFA. Administrators use security keys.", "-"),
    ("Q36", "Vulnerabilities", "A.8.8, SD-13, ORV-PRC-02", "Are vulnerabilities fixed within the deadlines?", "Vulnerability tickets", "20 critical and high findings, Apr to Jun", "R-HSRE", "C", "19 fixed in time. One high finding ran six days late under an approved exception.", "-"),
    ("Q37", "Backup", "A.8.13, BR-01 to BR-07", "Are backups isolated and restores tested?", "Backup configuration, restore records", "3 restore tests", "R-HSRE", "C", "Backups immutable in a separate account. Restores passed in January, April and July.", "-"),
    ("Q38", "Logging", "A.8.15, LM-01 to LM-03", "Is audit logging complete and protected?", "Trail and log account configuration", "All AWS accounts and 3 SaaS sources", "R-HSRE", "C", "All accounts and sources delivering to the protected log account.", "-"),
    ("Q39", "Monitoring", "A.8.16, LM-07", "Are alerts triaged every working day?", "SIEM triage log", "All working days in June 2027", "R-CISO", "MI", "No triage on four days, 14 to 17 June, while the Security Engineer was on leave. Eleven alerts waited up to four days.", "NC-06"),
    ("Q40", "Cryptography", "A.8.24, CR-07 to CR-09", "Are keys inventoried and rotated?", "Key inventory, rotation records", "10 keys", "R-HSRE", "C", "All ten had an owner and were inside their rotation date.", "-"),
    ("Q41", "Development", "A.8.25 to A.8.29, SD-01 to SD-05", "Are security gates applied to changes?", "Change records, threat models, scan results", "12 changes to payment services", "R-CTO", "OFI", "All 12 passed the gates. Abuse-case requirements are not linked to the threat catalog.", "OFI-02"),
    ("Q42", "Change", "A.8.32, SD-09, SD-10", "Do production changes go through the reviewed path?", "Deployment log", "30 deployments in June", "R-CTO", "C", "All 30 deployed through CI with a second approver. No emergency changes in the period.", "-"),
    ("Q43", "Data handling", "A.8.10, A.8.11, AM-10, AM-11", "Is card data kept out of tickets and personal data masked?", "Monthly search results, masking configuration", "3 monthly searches, 2 tools", "R-SUPMGR", "C", "No card numbers in the last three searches. Masking active in Metabase and Orbit.", "-"),
    ("Q44", "Exceptions", "Policy exception process", "Are policy exceptions approved, time-limited and reviewed?", "Exception register", "All 9 exceptions", "R-CISO", "OB", "All nine approved with compensating controls. Three expire within 30 days with no decision recorded.", "OBV-03"),
    ("Q45", "Performance", "Clause 9.1", "Is recurring evidence collected efficiently?", "Evidence collection method", "-", "R-CISO", "OFI", "Control owners export evidence by hand each month. It works, but it will not scale.", "OFI-01"),
    ("Q46", "Monitoring", "A.8.16, LM-08", "Is detection coverage measured?", "Detection rule list, coverage review", "Quarterly review of June", "R-CISO", "OFI", "Coverage is reviewed, but no measure shows how much of the threat catalog has a tested detection.", "OFI-03"),
]

# id, type, title, criteria, what is required, evidence, statement, classification reason, owner, linked risks
FINDINGS = [
    dict(id="NC-01", type="Major nonconformity", title="Critical suppliers not under control", criteria="Clause 8.1; A.5.19, A.5.20, A.5.22; SU-02, SU-03",
         requirement="Orvanta must control the processes it outsources. Its own policy says Tier 1 and Tier 2 suppliers pass a security assessment before a contract is signed (SU-02), and that contracts carry the clauses in the contract checklist (SU-03).",
         evidence="The third-party risk register on 13 July 2027 showed five of eight Tier 1 suppliers assessed. Tessarin, Vaskora Bank and Helvora were not, against a target of 30 June. The Helvora contract was renewed on 1 June 2027 for 24 months with no assessment on file and no completed checklist (EN-05). The Head of Compliance and the General Counsel confirmed that a contract renewal does not trigger the third-party risk process.",
         statement="Supplier security requirements were not applied to critical outsourced services. Three of eight Tier 1 suppliers are unassessed, and one critical contract was renewed without the required assessment and clauses, so Orvanta cannot show that these outsourced processes are controlled.",
         reason="Major. The failure is systematic, because nothing connects contract renewal to the supplier process. It affects services that handle customer data and card processing, and it puts a required ISMS outcome in doubt.",
         owner="R-HCOMP", risks="RSK-12, RSK-13, RSK-14, RSK-29"),
    dict(id="NC-02", type="Minor nonconformity", title="Leaver access not fully removed outside single sign-on", criteria="A.5.18; AC-13; ORV-PRC-01 step 11",
         requirement="Leaver access must be removed within 24 hours of the last working day (AC-13). The procedure requires accounts, tokens and keys in tools outside single sign-on to be checked and removed (step 11).",
         evidence="Ten of 14 leavers from 1 April to 30 June 2027 were sampled. All ten Okta accounts were suspended within 21 hours. Two leaver tickets had no completed checklist for other tools. For one of them, a GitHub personal access token stayed valid for nine days after the last working day (EN-06). The token was not used in that time.",
         statement="The leaver procedure was not followed in two of ten cases, and one access token remained valid for nine days, so access removal within 24 hours is not assured outside single sign-on.",
         reason="Minor. The main control works and no misuse occurred. The lapse is limited to one step of the procedure.",
         owner="R-ITOPS", risks="RSK-06"),
    dict(id="NC-03", type="Minor nonconformity", title="Superseded documents in use", criteria="Clause 7.5.3",
         requirement="Documented information must be controlled so that the current approved version is the one in use, and obsolete versions are not used by mistake.",
         evidence="Twelve documents seen in use during interviews were compared with the controlled versions in Confluence. Two were superseded: the Baku platform team worked from a PDF of the Remote Working Policy at draft 0.9, and a restore runbook in Google Drive differed from the approved version 1.2 (EN-07).",
         statement="Two of twelve sampled documents in use were superseded versions, so control of documented information is not fully effective.",
         reason="Minor. The differences were small and caused no error, but the restore runbook is used in an emergency.",
         owner="R-CISO", risks="-"),
    dict(id="NC-04", type="Minor nonconformity", title="Production access granted before induction", criteria="Clause 7.3; A.6.3; HR-04",
         requirement="New joiners complete security induction in their first week, and before they receive production access (HR-04).",
         evidence="Fifteen of 22 joiners from 1 February to 30 June 2027 were sampled. For three engineers, Okta group history showed production access two to six days before the training platform recorded induction as complete (EN-08).",
         statement="Three of 15 sampled joiners received production access before completing security induction, contrary to requirement HR-04.",
         reason="Minor. All three completed induction within the first week, and no incident followed. The sequence is not enforced by any technical gate.",
         owner="R-HPEOPLE", risks="RSK-02"),
    dict(id="NC-05", type="Minor nonconformity", title="Risk acceptance condition not met or tracked", criteria="Clause 8.3; ORV-RISK-001; acceptance record RA-01",
         requirement="An accepted risk above appetite stays valid only while its conditions are met. RA-01 required a documented manual regional recovery runbook by 30 June 2027.",
         evidence="On 12 July 2027 no runbook existed. The Head of Platform and SRE confirmed it had not been started. The conditions of RA-01 were not recorded in the treatment plan or any tracker, and nobody had escalated the missed date (EN-09).",
         statement="A condition of risk acceptance RA-01 was missed without escalation or re-approval, and acceptance conditions are not tracked, so the acceptance was not managed as the methodology requires.",
         reason="Minor. The other three conditions were met and the risk itself did not change. The gap is in tracking.",
         owner="R-HSRE", risks="RSK-16"),
    dict(id="NC-06", type="Minor nonconformity", title="Alerts not triaged every working day", criteria="A.8.16; LM-07",
         requirement="Alerts are triaged every working day, and high-severity alerts page the on-call engineer (LM-07).",
         evidence="The SIEM triage log for June 2027 showed no entries from 14 to 17 June, when the Security Engineer was on leave. Eleven alerts waited up to four days. None was high severity, and paging worked throughout (EN-10).",
         statement="Alerts were not triaged on four working days in June 2027 because the task depends on one person, contrary to requirement LM-07.",
         reason="Minor. High-severity paging was unaffected and no alert proved to be an incident, but detection relies on a single person.",
         owner="R-CISO", risks="RSK-05, RSK-27"),
    dict(id="OBV-01", type="Observation", title="Statement of Applicability is not current", criteria="Clause 6.1.3",
         requirement="-", evidence="Version 1.1 is dated 30 April 2027. At least 14 controls have changed status since, including A.5.16 and A.8.22 after the legacy account closed.",
         statement="If the statement is not updated before Stage 1, the certification auditor will find statuses that do not match reality.", reason="Observation. Not yet a nonconformity, because statuses understate progress.",
         owner="R-RISK", risks="-"),
    dict(id="OBV-02", type="Observation", title="KPI definitions are not written down", criteria="Clause 9.1",
         requirement="-", evidence="Training completion excludes contractors in one report and includes them in another. Two people measure leaver suspension time from different start points.",
         statement="Without written definitions, KPI results cannot be compared over time and could mislead the management review.", reason="Observation. Results are reported and the differences are small.",
         owner="R-CISO", risks="-"),
    dict(id="OBV-03", type="Observation", title="Exceptions close to expiry without a decision", criteria="Policy exception process",
         requirement="-", evidence="Three of nine exceptions expire within 30 days. No renewal or closure decision is recorded for them.",
         statement="An exception that lapses unnoticed becomes an unapproved policy breach.", reason="Observation. None has expired yet.",
         owner="R-CISO", risks="-"),
    dict(id="OFI-01", type="Opportunity for improvement", title="Automate recurring evidence collection", criteria="Clause 9.1",
         requirement="-", evidence="Control owners export reports from Okta, Jamf and AWS by hand every month.",
         statement="Scheduled exports into the ISMS space would cut effort and make evidence consistent for the certification audit.", reason="-", owner="R-CISO", risks="-"),
    dict(id="OFI-02", type="Opportunity for improvement", title="Link abuse cases to the threat catalog", criteria="A.8.26",
         requirement="-", evidence="Abuse-case requirements in Jira are written as free text.",
         statement="Tagging them with threat IDs would show which threats each change addresses and feed the risk register.", reason="-", owner="R-CTO", risks="-"),
    dict(id="OFI-03", type="Opportunity for improvement", title="Measure detection coverage", criteria="A.8.16",
         requirement="-", evidence="Detection rules are reviewed every quarter, but no figure shows how much of the threat catalog is covered by a tested rule.",
         statement="A coverage percentage would turn the review into a KPI and show progress to the Board.", reason="-", owner="R-CISO", risks="-"),
]

# id, date, method, auditee, what was examined, result
EVIDENCE_NOTES = [
    ("EN-01", "12 Jul 2027", "Document review", "R-CISO", "ISMS Manual version 1.0: scope, context, parties, objectives.", "Consistent with operations observed."),
    ("EN-02", "12 Jul 2027", "Interview", "R-CEO", "Leadership commitment, resources, Board reporting. Six staff asked about the policy and report channel.", "Commitment evident. All six staff answered correctly."),
    ("EN-03", "12 Jul 2027", "Sample test", "R-RISK", "Risks RSK-01, 04, 05, 09, 12, 16, 22 and 28 traced from workshop record to register and treatment plan.", "Method applied consistently in all eight."),
    ("EN-04", "12 Jul 2027", "Sample test", "R-RISK", "SoA controls A.5.16, 5.18, 5.19, 5.24, 6.3, 8.1, 8.2, 8.5, 8.8, 8.13, 8.15, 8.16, 8.22, 8.24 and 8.32 compared with evidence.", "Justifications sound. Several statuses out of date. See OBV-01."),
    ("EN-05", "13 Jul 2027", "Document review and interview", "R-HCOMP", "Third-party risk register, all eight Tier 1 entries. Contract files for Helvora, Kyrovia, AWS, Okta and GitHub.", "Three unassessed. Helvora renewed 1 June without assessment or checklist. See NC-01."),
    ("EN-06", "13 Jul 2027", "Sample test", "R-ITOPS", "Ten leaver tickets, Okta system log and GitHub organization audit log.", "Okta suspension within 21 hours in all ten. Two checklists missing, one token live nine days. See NC-02."),
    ("EN-07", "14 Jul 2027", "Observation", "R-CISO", "Twelve documents seen in use during interviews, compared with Confluence versions.", "Two superseded copies. See NC-03."),
    ("EN-08", "13 Jul 2027", "Sample test", "R-HPEOPLE", "Fifteen joiner records: training completion date against Okta production group assignment date.", "Three had access before induction. See NC-04."),
    ("EN-09", "12 Jul 2027", "Document review and interview", "R-HSRE", "Acceptance record RA-01, its four conditions and the treatment plan.", "Condition 3 not met and not tracked. See NC-05."),
    ("EN-10", "14 Jul 2027", "Sample test", "R-SECENG", "SIEM triage log for every working day in June 2027, and PagerDuty history.", "No triage 14 to 17 June. Paging unaffected. See NC-06."),
    ("EN-11", "13 Jul 2027", "Sample test", "R-ITOPS", "Twenty laptops checked in Jamf and the EDR console. Test sign-in from an unmanaged device.", "All compliant. Sign-in blocked. Strength."),
    ("EN-12", "13 Jul 2027", "Sample test", "R-HSRE", "Fifteen just-in-time access requests and one break-glass use, May to June.", "All approved by a second person and expired on time. Strength."),
    ("EN-13", "14 Jul 2027", "Document review", "R-HSRE", "Restore test records for January, April and July 2027, and the backup account configuration.", "Three restores passed. Backups immutable and isolated. Strength."),
    ("EN-14", "14 Jul 2027", "Document review", "R-CISO", "Incident record and post-incident review for the Severity 2 incident of 18 May 2027. Tabletop exercise record.", "Plan followed. Contained in 40 minutes. Review done in six working days."),
    ("EN-15", "15 Jul 2027", "Sample test", "R-CTO", "Thirty production deployments in June and twelve changes to payment services.", "All through the reviewed path with security gates applied."),
]

STRENGTHS = [
    ("Device control is complete.", "All 20 sampled laptops were managed, encrypted and protected, and a sign-in from an unmanaged device was refused (EN-11)."),
    ("Privileged access is disciplined.", "Every sampled request had a second approver and expired on time. The single break-glass use was reviewed the next day (EN-12)."),
    ("Recovery is proven.", "Three full restores have passed since January, from backups an attacker with production access could not delete (EN-13)."),
    ("The incident process worked under pressure.", "A real phishing incident in May was contained in 40 minutes, and its review led to three closed actions (EN-14)."),
    ("Reporting is honest.", "Missed targets are shown openly in the KPI dashboard, which makes the management system credible."),
]

# finding, correction, five whys, root cause, corrective actions [(action, owner, due)], effectiveness check, status at CAP_DATE
CAPA = [
    dict(id="CA-01", finding="NC-01", correction="Assess Helvora at once and agree a contract addendum with the missing clauses. Assessment completed 30 July 2027.",
         whys=["Why was a critical contract renewed without an assessment? The supplier owner and Legal handled the renewal and did not involve Compliance.",
               "Why was Compliance not involved? The contract renewal workflow has no step that calls the third-party risk process.",
               "Why does the workflow lack that step? The Supplier Security Policy was approved in April, but the contract workflow, owned by Legal, was not changed.",
               "Why was it not changed? Nobody was assigned to carry the new policy into other teams' processes.",
               "Why not? Policy rollout covered publishing and training, but had no step for integrating requirements into the processes they affect."],
         root="Policy rollout stops at publication. It has no step that builds new requirements into the workflows of the teams that must follow them. A second cause is capacity: one person performed all assessments.",
         actions=[("Add a mandatory third-party risk sign-off to the contract workflow, so no Tier 1 or Tier 2 contract can be signed without it", "R-GC", "15 Aug 2027"),
                  ("Complete assessments of Tessarin, Vaskora Bank and Helvora, with remediation plans", "R-HCOMP", "31 Aug 2027"),
                  ("Add a process integration check to the policy rollout checklist, and apply it to all 12 policies", "R-CISO", "31 Aug 2027"),
                  ("Train a second assessor in the security team", "R-CISO", "30 Sep 2027")],
         check="Follow-up audit IA-2027-02 samples every Tier 1 and Tier 2 contract signed from 15 August. Target: none without sign-off, and eight of eight Tier 1 suppliers assessed.", status="In progress"),
    dict(id="CA-02", finding="NC-02", correction="Revoke the token and check all 14 leavers of the quarter for other live credentials. Done 14 July 2027. No further cases found.",
         whys=["Why did a token stay valid for nine days? The checklist for tools outside single sign-on was not completed.",
               "Why was it not completed? It is a manual step, and the ticket can be closed without it.",
               "Why does the step rely on memory? Personal access tokens are not visible in Okta, so suspension there gives a false sense of completion.",
               "Why are tokens outside Okta's control? GitHub tokens were allowed without an expiry and without single sign-on authorization.",
               "Why was that allowed? Token rules were never defined when GitHub moved behind Okta."],
         root="Personal access tokens were ungoverned: they had no expiry and survived the suspension of the identity that created them.",
         actions=[("Enforce fine-grained GitHub tokens with single sign-on authorization and a 30-day maximum lifetime", "R-CTO", "15 Aug 2027"),
                  ("Make the checklist a set of required sub-tasks, so a leaver ticket cannot close without them", "R-ITOPS", "15 Aug 2027")],
         check="Sample ten leavers in the fourth quarter. Target: all checklists complete, no credential live after 24 hours.", status="In progress"),
    dict(id="CA-03", finding="NC-03", correction="Delete both copies and point the teams to the Confluence versions. Done 15 July 2027.",
         whys=["Why were superseded copies in use? Teams had exported documents to PDF and Google Drive.",
               "Why did they export them? They wanted to comment on drafts and to have the runbook to hand during an outage.",
               "Why was that not possible in Confluence? Review comments were not enabled for all staff, and nobody had said where the offline runbook copy should live.",
               "Why did the copies stay after approval? Nothing marks an export as uncontrolled, and nobody looks for copies.",
               "Why not? Document control rules covered publishing, not copies."],
         root="Document control did not cover exported copies. Staff had legitimate needs that the controlled space did not meet.",
         actions=[("Enable review comments in the ISMS space for all staff, and add an 'uncontrolled when copied' banner to exports", "R-CISO", "31 Aug 2027"),
                  ("Keep one approved offline copy of emergency runbooks, replaced automatically on each new version", "R-HSRE", "31 Aug 2027"),
                  ("Search Google Drive every quarter for copies of controlled documents", "R-CISO", "30 Sep 2027")],
         check="Repeat the sample of twelve documents in use during the follow-up audit. Target: none superseded.", status="In progress"),
    dict(id="CA-04", finding="NC-04", correction="Confirm that all three engineers have completed induction. Confirmed 13 July 2027.",
         whys=["Why did joiners get production access before induction? The production role group is assigned on the start date.",
               "Why on the start date? Group assignment in Okta is driven by job role alone.",
               "Why does it ignore induction? Training status lives in a separate platform that Okta does not read.",
               "Why were the two never connected? The requirement was written into policy, and the rule in Okta was left as it was.",
               "Why? As with NC-01, policy rollout had no step for building the requirement into the system that enforces it."],
         root="The rule existed only on paper. No technical gate tied production access to induction.",
         actions=[("Sync an 'induction complete' attribute from the training platform to Okta, and require it in the production group rule", "R-ITOPS", "15 Sep 2027"),
                  ("Until then, IT Operations checks induction by hand before assigning production groups", "R-ITOPS", "20 Jul 2027")],
         check="Sample all joiners with production access in the fourth quarter. Target: none granted before induction.", status="In progress"),
    dict(id="CA-05", finding="NC-05", correction="Write the regional recovery runbook and ask the CEO to reconfirm RA-01. Runbook approved 30 July 2027. Acceptance reconfirmed 2 August 2027.",
         whys=["Why was the runbook condition missed? Nobody was tracking it.",
               "Why not? The conditions were written in the acceptance record but not entered in any action tracker.",
               "Why not entered? The methodology says acceptance needs conditions, but not who tracks them.",
               "Why does it not say? Risk acceptance was new to Orvanta, and RA-01 was the first record.",
               "Why was the gap not seen at the quarterly risk review? The review covered scores and treatment actions, not acceptance conditions."],
         root="The methodology gave acceptance conditions no owner and no place in the tracker, so they fell outside every review.",
         actions=[("Enter each acceptance condition as an action in the treatment plan, with an owner and due date", "R-RISK", "15 Aug 2027"),
                  ("Issue methodology version 1.1 naming the Risk Manager as tracker of conditions, and add them to the quarterly review agenda", "R-RISK", "31 Aug 2027")],
         check="At the October risk review, confirm every open condition has an owner, date and status.", status="In progress"),
    dict(id="CA-06", finding="NC-06", correction="Triage the backlog of eleven alerts. Done 18 June 2027, before the audit. No incident found.",
         whys=["Why were alerts not triaged for four days? The Security Engineer was on leave.",
               "Why did nobody else do it? Triage was assigned to one person, with no deputy.",
               "Why was there no deputy? The SIEM went live in March, and the rota was meant to follow once the third security hire was trained.",
               "Why had that not happened by June? Training focused on supplier assessments and policy work.",
               "Why did nobody notice the missing triage? No alert fires when a working day passes without a triage record."],
         root="A daily control depended on one person, and nothing detected when it did not run.",
         actions=[("Set a triage rota of three: Security Engineer, security analyst and the SRE on call", "R-CISO", "15 Aug 2027"),
                  ("Alert the CISO if no triage record exists by 15:00 on a working day", "R-SECENG", "15 Aug 2027"),
                  ("Bring a proposal for a managed detection service for out-of-hours cover to the management review", "R-CISO", "26 Aug 2027")],
         check="Triage log for September and October. Target: a record on every working day.", status="In progress"),
]
FISHBONE = {
    "People": ["One assessor", "Owners unaware"],
    "Process": ["No workflow gate", "No integration step"],
    "Tools": ["Not linked to contracts", "No renewal reminders"],
    "Governance": ["Split ownership", "Target not escalated"],
    "Suppliers": ["Slow supplier replies"],
    "Time": ["Compressed roadmap"],
}

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"]
# id, name, unit, direction (up or down is better), target, monthly values Jan to Jul 2027, owner
KPIS = [
    ("OBJ-01", "Certification milestones completed, of 6", "count", "up", 6, [0, 2, 3, 3, 3, 3, 4], "R-CEO"),
    ("OBJ-02", "Workforce tools outside Okta MFA", "count", "down", 0, [3, 3, 0, 0, 0, 0, 0], "R-ITOPS"),
    ("OBJ-03", "Shared administrative accounts", "count", "down", 0, [3, 3, 2, 1, 0, 0, 0], "R-HSRE"),
    ("OBJ-04", "Laptops enrolled in Jamf with EDR", "%", "up", 100, [78, 90, 100, 100, 100, 100, 100], "R-ITOPS"),
    ("OBJ-05", "Median time to suspend a leaver account", "hours", "down", 24, [30, 26, 22, 20, 18, 19, 16], "R-ITOPS"),
    ("OBJ-06", "Full restore tests passed in the last 12 months", "count", "up", 4, [1, 1, 1, 2, 2, 2, 3], "R-HSRE"),
    ("OBJ-07", "Priority log sources in the SIEM", "%", "up", 100, [0, 0, 20, 40, 60, 85, 90], "R-CISO"),
    ("OBJ-08", "Tier 1 suppliers with a current assessment, of 8", "count", "up", 8, [0, 0, 2, 3, 4, 5, 6], "R-HCOMP"),
    ("OBJ-09", "Production deployments through the reviewed CI path", "%", "up", 100, [88, 92, 95, 97, 99, 100, 100], "R-CTO"),
    ("OBJ-10", "Annual security training completion", "%", "up", 98, [92, 93, 95, 96, 97, 98, 98], "R-HPEOPLE"),
    ("KRI-01", "Risks rated High or Critical", "count", "down", 1, [26, 26, 22, 17, 12, 8, 6], "R-RISK"),
    ("KRI-02", "Critical vulnerabilities past deadline", "count", "down", 0, [6, 5, 3, 2, 0, 1, 0], "R-HSRE"),
    ("KRI-03", "Alerts triaged within one working day", "%", "up", 95, [0, 0, 70, 85, 92, 81, 94], "R-CISO"),
    ("KRI-04", "Severity 1 and 2 security incidents", "count", "down", 0, [0, 0, 0, 0, 1, 0, 0], "R-CISO"),
    ("KRI-05", "Corrective actions past due date", "count", "down", 0, [0, 0, 0, 0, 0, 0, 0], "R-CISO"),
]
KPI_DUE = {"OBJ-01": "30 Nov 2027", "OBJ-02": "31 Mar 2027", "OBJ-03": "30 Apr 2027", "OBJ-04": "31 Mar 2027", "OBJ-05": "31 Mar 2027", "OBJ-06": "31 Dec 2027",
           "OBJ-07": "30 Jun 2027", "OBJ-08": "30 Jun 2027", "OBJ-09": "30 Apr 2027", "OBJ-10": "30 Jun 2027", "KRI-01": "31 Aug 2027"}
RISK_STATUS = dict(critical=0, high=6, medium=16, low=8, note="RSK-16 is accepted. RSK-12, 13 and 14 wait on supplier assessments, RSK-05 on the last SIEM sources and RSK-07 on DLP rules.")

# clause 9.3 input topic (our wording), summary for the review
REVIEW_INPUTS = [
    ("Actions from earlier reviews", "This is the first full review. All seven actions from the February and May checkpoints are closed."),
    ("Changes in internal and external issues", "The legacy AWS account closed on 28 May. A third security specialist joined in March. Stage 1 is booked for 20 and 21 September 2027. Enterprise prospects now send security questionnaires before contract talks."),
    ("Needs of interested parties", "Two enterprise prospects asked for the Statement of Applicability version and the certification date. No new regulatory requirement was raised with Orvanta in the period."),
    ("Nonconformities and corrective actions", "The internal audit raised one major and five minor nonconformities. All six have root causes and plans. Immediate corrections are complete for all six, and no action is overdue."),
    ("Monitoring and measurement", "Eight of ten objectives are met or on track. Two missed their dates: SIEM sources stand at 90% against 100% by June, and six of eight Tier 1 suppliers are assessed."),
    ("Audit results", "32 of 46 audit questions showed full conformity, and the strengths were in the highest-risk controls. The auditor judges Orvanta ready for Stage 1 if the major nonconformity is closed first."),
    ("Fulfilment of objectives", "Identity, device, leaver and change objectives are met. Training reached its 98% target in June. Certification stands at four of six milestones."),
    ("Feedback from interested parties", "Staff survey after the May phishing incident: 84% knew how to report. One merchant complaint about a security questionnaire response time."),
    ("Risk assessment and treatment", "Risks rated High or Critical fell from 26 to 6. No risk is Critical. Twenty-one of 26 treatment actions are complete."),
    ("Opportunities for improvement", "Three from the audit: automated evidence collection, abuse cases linked to threats, and a detection coverage measure."),
]
# id, decision
DECISIONS = [
    ("D-01", "The ISMS is suitable and adequate. Its effectiveness is confirmed except in supplier control, where the major nonconformity must close before Stage 1."),
    ("D-02", "The corrective action plan of 6 August 2027 is approved."),
    ("D-03", "Risk acceptance RA-01 is confirmed until 31 December 2027, now that the recovery runbook exists. A second-region design study is added to the 2028 plan."),
    ("D-04", "The date for objective OBJ-07 moves to 30 September 2027. Objective OBJ-08 keeps its target, with a new date of 31 August 2027."),
    ("D-05", "A managed detection service for out-of-hours alert cover is approved in principle, up to the budget the CFO confirms by 15 September."),
    ("D-06", "Statement of Applicability version 1.2 is to be issued before Stage 1."),
    ("D-07", "Stage 1 goes ahead on 20 and 21 September 2027, provided the follow-up check on NC-01 passes."),
]
# id, action, owner, due
REVIEW_ACTIONS = [
    ("MR-01", "Close NC-01: workflow gate live and all eight Tier 1 suppliers assessed", "R-HCOMP", "31 Aug 2027"),
    ("MR-02", "Issue Statement of Applicability version 1.2", "R-RISK", "10 Sep 2027"),
    ("MR-03", "Connect the remaining SIEM log sources", "R-CISO", "30 Sep 2027"),
    ("MR-04", "Confirm the budget for the managed detection service", "R-CFO", "15 Sep 2027"),
    ("MR-05", "Write KPI definitions and add detection coverage as a KPI", "R-CISO", "30 Sep 2027"),
    ("MR-06", "Decide renewal or closure of the three expiring exceptions", "R-CISO", "3 Sep 2027"),
    ("MR-07", "Scope a second-region design study for the 2028 plan", "R-HSRE", "30 Nov 2027"),
    ("MR-08", "Run the follow-up audit IA-2027-02 before Stage 2", "R-HCOMP", "15 Oct 2027"),
]
ATTENDEES = ["R-CEO", "R-CTO", "R-CFO", "R-COO", "R-CISO", "R-HCOMP", "R-RISK", "R-DPO", "R-HPEOPLE"]
