"""Project 3 ISMS documentation content for the fictional Orvanta Payments UAB.

All wording is original. Annex A controls are cited by ID only. Each requirement lists the controls it implements,
so the control-to-policy map is derived from this file, not maintained by hand.
"""

EXCEPTIONS = ("Request an exception through the security exception form in Jira. State the business reason, the compensating control and an expiry date no more than six months ahead. "
              "The CISO approves or rejects it. An exception that leaves a High risk also needs written acceptance by the CEO under the Risk Management Methodology (ORV-RISK-001). "
              "The CISO reviews the exception register every month.")
ENFORCEMENT = ("Compliance is checked through control tests, access reviews and the internal audit. Breaches by staff are handled under the disciplinary process in the Human Resources Security Policy, "
               "in proportion to intent and harm. Breaches by suppliers are handled under their contract. Nobody is penalized for reporting a problem in good faith.")

POLICIES = [
    dict(num=1, code="IS", title="Information Security Policy", owner="R-CISO", reviewer="R-CISO", approver="R-CEO", date="19 February 2027",
         purpose="This is Orvanta's top-level security policy. It states what leadership commits to, how security is governed and which topic policies carry the detail.",
         scope="Everyone who works for Orvanta Payments UAB and Orvanta Engineering LLC, in Vilnius, Baku or remotely, and every supplier that handles Orvanta information. It covers all products, systems and data in the ISMS scope.",
         roles=[("Management Board", "Approves this policy and the risk appetite. Reviews ISMS performance every quarter."),
                ("CEO", "Accountable for information security. Provides resources and accepts High risks."),
                ("CISO", "Runs the ISMS, owns the security policies and reports risk to the CEO and the Board."),
                ("Managers", "Make sure their teams know and follow the policies."),
                ("All staff", "Follow the policies and report anything suspicious.")],
         sections=[
             ("Commitment", [
                 ("Orvanta protects the confidentiality, integrity and availability of customer funds records, payment services and personal data, and meets its legal, regulatory and contractual duties.", "5.1, 5.31"),
                 ("The Management Board approves this policy, and the CEO communicates it to all staff and relevant suppliers.", "5.1"),
                 ("Security objectives are set each year in the ISMS Manual (ORV-ISMS-001), measured monthly and reported to the Management Board every quarter.", "5.1"),
                 ("Risks are assessed and treated under the Risk Management Methodology (ORV-RISK-001), and selected controls are recorded in the Statement of Applicability.", "5.1"),
             ]),
             ("Governance", [
                 ("The CISO reports to the CEO and may raise any risk directly with the Management Board.", "5.2"),
                 ("Every system, data class, supplier and control has a named owner, recorded in the asset register or the Statement of Applicability.", "5.2, 5.9"),
                 ("Conflicting duties are separated. Where a small team makes that impractical, the CISO approves a compensating control such as independent review.", "5.3"),
                 ("Managers explain security duties to their teams, check that training is completed and act on policy breaches.", "5.4"),
                 ("The Head of Compliance keeps current contacts for the Bank of Lithuania, the State Data Protection Inspectorate and the national CSIRT.", "5.5"),
                 ("The CISO keeps Orvanta in at least one financial-sector security information sharing group.", "5.6"),
                 ("The CISO reviews threat intelligence every month and updates the threat catalog and detection rules.", "5.7"),
                 ("Projects that change systems or data handling include a security check at the start and before launch.", "5.8"),
             ]),
             ("Compliance and assurance", [
                 ("The Head of Compliance maintains a register of legal, regulatory and contractual requirements, each with an owner.", "5.31"),
                 ("Software and content are used within their license terms, and open-source licenses are checked in CI.", "5.32"),
                 ("Records are kept and deleted according to the retention schedule owned by the Head of Compliance.", "5.33"),
                 ("Personal data is handled as the DPO directs, including transfer safeguards for access from Baku.", "5.34"),
                 ("The ISMS is reviewed independently every year through the internal audit programme.", "5.35"),
                 ("Control owners test their controls on the calendar set by the CISO and keep the evidence.", "5.36"),
                 ("Security-relevant operating procedures are documented, owned and kept in the controlled ISMS space in Confluence.", "5.37"),
             ]),
             ("Physical and environmental security", [
                 ("Each office has a defined perimeter, with badge or reception-controlled entry and a visitor log.", "7.1, 7.2"),
                 ("Offices are locked out of hours, and entrances are monitored by CCTV or the landlord's equivalent, confirmed yearly.", "7.3, 7.4"),
                 ("Production runs only in AWS. The CISO reviews AWS assurance reports every year for physical, environmental and utility protection.", "7.5, 7.11"),
                 ("No office holds production systems, so Orvanta has no secure areas. If that changes, the CISO sets rules before the systems arrive.", "7.6"),
                 ("Office network equipment sits in locked cabinets with protected cabling, and only IT Operations or approved suppliers maintain it.", "7.8, 7.12, 7.13"),
             ]),
         ],
         measures=[("Security objectives reported to the Management Board", "Every quarter"), ("Controls with a named owner", "100%"), ("Policies reviewed on time", "100%")],
         related="ISMS Manual (ORV-ISMS-001), Risk Management Methodology (ORV-RISK-001), all topic policies (ORV-POL-02 to ORV-POL-12)"),

    dict(num=2, code="AC", title="Access Control Policy", owner="R-CISO", reviewer="R-ITOPS", approver="R-CISO", date="12 March 2027",
         purpose="This policy makes sure only the right people and services reach Orvanta systems and data, with no more access than they need.",
         scope="All workforce, service and supplier identities, and all systems in the ISMS scope, including AWS, Okta, GitHub, the Orbit console and legacy tools.",
         roles=[("CISO", "Owns this policy and approves exceptions."), ("IT Operations Lead", "Runs Okta, joiner-mover-leaver changes and access reviews."),
                ("Head of Platform and SRE", "Runs AWS and Kubernetes access, privileged access and network controls."), ("System owners", "Approve access to their systems and review it every quarter.")],
         sections=[
             ("Principles", [
                 ("Access is granted by role, on least privilege and need to know, and approved by the system owner.", "5.15"),
                 ("Every person has one named identity in Okta. Shared accounts are not allowed.", "5.16"),
                 ("Each service account has a named owner, no interactive login and credentials held in AWS Secrets Manager.", "5.16, 5.17"),
             ]),
             ("Authentication", [
                 ("All workforce applications sign in through Okta single sign-on with MFA. An application that cannot do so is retired or covered by an approved exception.", "8.5"),
                 ("Administrators authenticate with phishing-resistant security keys.", "8.5"),
                 ("Passwords are at least 14 characters, unique to each service and stored in the company password manager.", "5.17"),
                 ("Long-lived cloud access keys are not allowed in repositories or on laptops. Pipelines use short-lived OIDC roles.", "5.17"),
             ]),
             ("Privileged access", [
                 ("Privileged access to AWS, Kubernetes and databases is requested just in time, approved, time-limited and logged.", "8.2"),
                 ("Standing administrators are limited to two Okta super admins and one sealed break-glass account, which is tested every quarter.", "8.2"),
                 ("Administrative tools such as kubectl and database clients are limited to approved roles, and their sessions are recorded.", "8.18"),
             ]),
             ("Access to data and code", [
                 ("Access to production personal data is restricted by role, masked by default and time-limited for support cases.", "8.3"),
                 ("Source code access is granted by repository team, and production repositories have branch protection.", "8.4"),
             ]),
             ("Access lifecycle", [
                 ("Joiner, mover and leaver changes follow the User Access Procedure (ORV-PRC-01). Leaver access is removed within 24 hours of the last working day.", "5.18"),
                 ("System owners review access every quarter, and privileged access is reviewed every month.", "5.18"),
             ]),
             ("Network access", [
                 ("Production networks are private, defined in Terraform and reached only through identity-aware access. Shared VPN profiles are not allowed.", "8.20"),
                 ("Required security settings for network services, such as Cloudflare and AWS load balancers, are documented and checked in code review.", "8.21"),
                 ("Production, staging, development and legacy environments run in separate AWS accounts with restricted connections between them.", "8.22"),
             ]),
         ],
         measures=[("Workforce applications behind Okta MFA", "100%"), ("Shared administrative accounts", "0"), ("Leaver access removed within 24 hours", "100%"), ("Quarterly access reviews completed on time", "100%")],
         related="User Access Procedure (ORV-PRC-01), Cryptography and Key Management Policy (ORV-POL-05), Logging and Monitoring Policy (ORV-POL-10)"),

    dict(num=3, code="AU", title="Acceptable Use Policy", owner="R-CISO", reviewer="R-HPEOPLE", approver="R-CISO", date="12 March 2027",
         purpose="This policy tells everyone what they may and may not do with Orvanta systems and information.",
         scope="All employees, contractors and supplier staff who use Orvanta devices, accounts or information.",
         roles=[("CISO", "Owns this policy."), ("Head of People", "Collects acknowledgments at joining and every year."), ("All users", "Follow the rules and report problems.")],
         sections=[
             ("Using systems and information", [
                 ("Company systems are for business use. Limited personal use is allowed when it is lawful and adds no security risk.", "5.10"),
                 ("Every user acknowledges this policy when joining and once a year.", "5.10"),
                 ("Company information is stored only in approved tools: Google Workspace, Confluence, Jira, GitHub, Slack and the business systems. Personal email and personal cloud storage are not used for company information.", "5.10"),
                 ("Credentials, card numbers and customer identity documents are never placed in Slack, tickets, email or code.", "5.10, 5.12"),
                 ("Users do not install unlicensed software, disable security tools or connect unapproved devices.", "5.10"),
                 ("Customer data, cardholder data and other Restricted information are not entered into external AI tools without CISO approval.", "5.10"),
                 ("Orvanta monitors its systems for security purposes within the law, and tells users how.", "5.10"),
             ]),
             ("Workspace", [
                 ("Screens lock after five minutes of inactivity, and users lock their device whenever they leave it.", "7.7"),
                 ("Desks, printers and whiteboards are cleared of confidential information at the end of the day.", "7.7"),
                 ("Web access from company devices is filtered for malicious sites, and users do not bypass the filter.", "8.23"),
             ]),
             ("Reporting", [
                 ("Users report suspected incidents, phishing and lost devices at once through the #security-report channel or the phishing report button.", "6.8"),
             ]),
         ],
         measures=[("Staff with a current acknowledgment", "100%"), ("Phishing emails reported within one hour during simulations", "Above 60%")],
         related="Remote Working Policy (ORV-POL-11), Asset Management and Classification Policy (ORV-POL-04), Incident Management Policy (ORV-POL-08)"),

    dict(num=4, code="AM", title="Asset Management and Classification Policy", owner="R-CISO", reviewer="R-ITOPS", approver="R-CISO", date="26 March 2027",
         purpose="This policy makes sure Orvanta knows what it has, who owns it and how sensitive it is, so that protection matches value.",
         scope="All systems, devices, SaaS tools, supplier services and information in the ISMS scope.",
         roles=[("CISO", "Owns this policy and the classification scheme."), ("IT Operations Lead", "Maintains the asset register and device lifecycle."),
                ("Asset owners", "Classify their assets and approve how they are used."), ("DPO", "Approves handling rules for personal data.")],
         sections=[
             ("Inventory and ownership", [
                 ("IT Operations keeps one asset register covering systems, devices, SaaS tools, data classes and supplier services, each with a named owner.", "5.9"),
                 ("The register is reconciled every month against Terraform, Jamf and Okta.", "5.9"),
                 ("Leavers return all assets by their last working day, and IT Operations records the return.", "5.11"),
             ]),
             ("Classification and handling", [
                 ("Owners classify information as Public, Internal, Confidential or Restricted.", "5.12"),
                 ("Restricted information, meaning cardholder data, identity documents and credentials, is stored only in systems approved for it.", "5.12"),
                 ("Documents and shared drives holding Confidential or Restricted information carry a label.", "5.13"),
                 ("Confidential and Restricted information leaves Orvanta only through approved channels, under contract and encrypted.", "5.14"),
                 ("Access to personal data from outside the EEA, including from Baku, follows the transfer impact assessment approved by the DPO.", "5.14, 5.34"),
             ]),
             ("Data protection in systems", [
                 ("Information is deleted at the end of its retention period, automatically where the system allows.", "8.10"),
                 ("Full card numbers are not stored in any Orvanta system. Support tickets are redacted automatically and searched every month.", "8.10, 8.11"),
                 ("Personal data is masked by default in reporting, support views and non-production environments.", "8.11"),
                 ("Data loss prevention rules alert on bulk exports and on external sharing of Confidential and Restricted information.", "8.12"),
             ]),
             ("Media and equipment", [
                 ("Removable storage is blocked on the devices of roles that handle Restricted information.", "7.10"),
                 ("Devices are wiped, with evidence, before reuse. Disposal goes through a supplier that issues a destruction certificate.", "7.14"),
             ]),
         ],
         measures=[("Assets with a named owner", "100%"), ("Laptops enrolled in Jamf", "100%"), ("Card numbers found in monthly ticket search", "0")],
         related="Acceptable Use Policy (ORV-POL-03), Cryptography and Key Management Policy (ORV-POL-05), Remote Working Policy (ORV-POL-11)"),

    dict(num=5, code="CR", title="Cryptography and Key Management Policy", owner="R-CISO", reviewer="R-HSRE", approver="R-CISO", date="26 March 2027",
         purpose="This policy sets how Orvanta uses encryption and manages keys, so that data stays protected at rest and in transit.",
         scope="All production and corporate systems, laptops, backups and connections to customers, banks and suppliers.",
         roles=[("CISO", "Owns this policy and approves algorithms and exceptions."), ("Head of Platform and SRE", "Runs AWS KMS, Secrets Manager and certificates."),
                ("Treasury and Safeguarding Manager", "Owns the bank connection keys."), ("Engineers", "Use the approved services and never handle raw keys in code.")],
         sections=[
             ("Encryption", [
                 ("Production data at rest is encrypted with keys managed in AWS KMS.", "8.24"),
                 ("Data in transit uses TLS 1.2 or higher, including traffic between internal services.", "8.24"),
                 ("Laptop disks are encrypted with FileVault, enforced through Jamf.", "8.24"),
                 ("Backups are encrypted with keys held in the backup account.", "8.24"),
                 ("Only approved algorithms and managed cryptographic services are used. Teams do not design their own cryptography.", "8.24"),
                 ("Card data cryptography stays with Tessarin. Orvanta systems handle tokens and truncated card numbers only.", "8.24"),
             ]),
             ("Key management", [
                 ("Keys and secrets are created and stored in AWS KMS or Secrets Manager, never in code, tickets or chat.", "8.24, 5.17"),
                 ("Each key has an owner, a purpose and a rotation date in the key inventory.", "8.24"),
                 ("KMS keys rotate every year. Secrets and SFTP keys rotate at least every year, and immediately after suspected exposure.", "8.24"),
                 ("Access to keys is limited by role and logged in CloudTrail.", "8.24"),
                 ("Certificates are issued and renewed automatically, and expiry is monitored.", "8.24"),
             ]),
         ],
         measures=[("Production data stores encrypted at rest", "100%"), ("Keys rotated on schedule", "100%"), ("Secrets found in repositories by scanning", "0")],
         related="Access Control Policy (ORV-POL-02), Backup and Recovery Policy (ORV-POL-09)"),

    dict(num=6, code="SD", title="Secure Development and Change Management Policy", owner="R-CISO", reviewer="R-CTO", approver="R-CISO", date="9 April 2027",
         purpose="This policy builds security into how Orvanta designs, changes and releases software and infrastructure.",
         scope="All code, infrastructure and configuration that reaches staging or production, written in Vilnius, Baku or remotely.",
         roles=[("CISO", "Owns this policy and sets the security gates."), ("CTO", "Accountable for engineering compliance."),
                ("Engineering heads", "Make sure their teams follow the life cycle."), ("Engineers", "Write, review and test changes as this policy requires.")],
         sections=[
             ("Secure development", [
                 ("Changes follow the secure development life cycle, with security gates set by the risk tier of the change.", "8.25"),
                 ("Security requirements, including abuse cases, are written for changes to payment, account and card functions.", "8.26"),
                 ("Major design changes go through threat modeling against the published engineering principles.", "8.27"),
                 ("All code is peer reviewed. Static analysis, dependency scanning and secret scanning run in every pipeline.", "8.28"),
                 ("Security tests run before release: dynamic testing in staging for web and API changes, and a penetration test every year.", "8.29"),
                 ("Orvanta does not outsource development today. If that changes, this policy and its reviews apply by contract.", "8.30"),
             ]),
             ("Environments and test data", [
                 ("Development, staging and production run in separate AWS accounts, and engineers hold no standing production access.", "8.31"),
                 ("Live personal data is not used in development or staging. Test data is synthetic or masked.", "8.33"),
             ]),
             ("Change control", [
                 ("Production changes deploy only through the CI pipeline, from protected branches, with approval from a second person.", "8.32, 5.3"),
                 ("Emergency changes use the logged break-glass route and are reviewed within two working days.", "8.32"),
                 ("Infrastructure is defined in Terraform and applied only from CI. Configuration drift raises an alert.", "8.9"),
                 ("Software reaches production only as built images. Manual installs on production hosts are not allowed.", "8.19"),
             ]),
             ("Vulnerabilities and testing", [
                 ("Vulnerabilities are handled under the Vulnerability and Patch Management Procedure (ORV-PRC-02): critical within 7 days, high within 30, medium within 90.", "8.8"),
                 ("Third-party components are tracked in a software bill of materials generated in CI.", "8.8, 5.21"),
                 ("Audit and penetration tests on production are scoped and scheduled with the Head of Platform and SRE to avoid disruption.", "8.34"),
             ]),
         ],
         measures=[("Production deployments through the reviewed CI path", "100%"), ("Critical vulnerabilities fixed within 7 days", "100%"), ("Repositories with scanning enabled", "100%")],
         related="Vulnerability and Patch Management Procedure (ORV-PRC-02), Access Control Policy (ORV-POL-02)"),

    dict(num=7, code="SU", title="Supplier Security Policy", owner="R-CISO", reviewer="R-HCOMP", approver="R-CISO", date="9 April 2027",
         purpose="This policy makes sure suppliers protect Orvanta information and services to the standard Orvanta holds itself to.",
         scope="All suppliers that handle Orvanta information or support its services, including AWS, Tessarin, Kyrovia, Vaskora Bank and Helvora.",
         roles=[("CISO", "Owns this policy and runs security assessments."), ("Head of Compliance", "Runs the third-party risk program and the DORA register of information."),
                ("General Counsel", "Makes sure contracts carry the required clauses."), ("Supplier owners", "Manage the relationship and report changes.")],
         sections=[
             ("Selection and contract", [
                 ("Every supplier that handles Orvanta information or supports a critical service is recorded, tiered and given an owner.", "5.19"),
                 ("Tier 1 and Tier 2 suppliers pass a security assessment before a contract is signed and before any data is shared.", "5.19"),
                 ("Contracts include security, confidentiality, incident notification, audit, subprocessor and exit clauses, using the contract checklist.", "5.20"),
                 ("Suppliers disclose their subprocessors, and Tier 1 suppliers show how they manage their own supply chain.", "5.21"),
                 ("ICT suppliers that support critical or important functions are recorded in the DORA register of information.", "5.19, 5.31"),
             ]),
             ("Operation", [
                 ("Supplier access to Orvanta systems is named, protected by MFA, limited to the task and removed when the contract ends.", "5.19"),
                 ("Tier 1 suppliers are reviewed every year and Tier 2 every two years. Assurance reports are tracked for expiry.", "5.22"),
                 ("A significant change or incident at a supplier triggers a reassessment.", "5.22"),
                 ("Cloud services follow the cloud security standard, which includes a shared responsibility matrix and exit considerations.", "5.23"),
                 ("Supplier incidents that affect Orvanta are handled under the Incident Management Policy.", "5.19"),
             ]),
             ("Exit", [
                 ("At the end of a contract, the supplier returns or destroys Orvanta information and confirms it in writing.", "5.20"),
             ]),
         ],
         measures=[("Tier 1 suppliers with a current assessment", "100%"), ("Tier 1 contracts with all required clauses", "100% at renewal"), ("Suppliers with a named owner", "100%")],
         related="Incident Management Policy (ORV-POL-08), Access Control Policy (ORV-POL-02)"),

    dict(num=8, code="IM", title="Incident Management Policy", owner="R-CISO", reviewer="R-HSRE", approver="R-CISO", date="9 April 2027",
         purpose="This policy makes sure security incidents are reported quickly, handled consistently and learned from.",
         scope="All security events and incidents that affect Orvanta information, systems or services, including those at suppliers.",
         roles=[("CISO", "Owns this policy, the response plan and the playbooks."), ("Incident lead", "Directs the response to a declared incident."),
                ("Head of Compliance and DPO", "Decide on regulatory and data subject notifications."), ("CEO", "Approves external communication."), ("All staff", "Report suspected events at once.")],
         sections=[
             ("Preparation", [
                 ("The CISO maintains the incident response plan, the on-call rota and playbooks for ransomware and cloud credential compromise.", "5.24"),
                 ("The plan is exercised at least once a year through a tabletop exercise, and lessons update the playbooks.", "5.24"),
             ]),
             ("Reporting and triage", [
                 ("Staff and suppliers report suspected security events immediately through #security-report or the on-call number.", "6.8"),
                 ("Events are triaged against the severity matrix. Severity 1 and 2 events are declared incidents.", "5.25"),
             ]),
             ("Response", [
                 ("Each incident has one incident lead with authority to isolate systems and revoke access.", "5.26"),
                 ("The Head of Compliance and the DPO join any incident that may need regulatory or customer notification. Deadlines follow the notification matrix.", "5.26"),
                 ("The CEO or a named delegate approves communication with customers, regulators and the media.", "5.26"),
                 ("Incident records are kept in the restricted security project in Jira.", "5.26"),
             ]),
             ("Evidence and learning", [
                 ("Evidence is preserved under the evidence handling procedure, with chain of custody, before systems are rebuilt.", "5.28"),
                 ("Severity 1 and 2 incidents get a post-incident review within 10 working days. Actions are tracked to closure and feed the risk register.", "5.27"),
             ]),
         ],
         measures=[("Severity 1 and 2 incidents with a review inside 10 working days", "100%"), ("Tabletop exercises held", "At least 1 a year"), ("Time from report to triage", "Under 1 hour")],
         related="Logging and Monitoring Policy (ORV-POL-10), Backup and Recovery Policy (ORV-POL-09), Supplier Security Policy (ORV-POL-07)"),

    dict(num=9, code="BR", title="Backup and Recovery Policy", owner="R-CISO", reviewer="R-HSRE", approver="R-CISO", date="23 April 2027",
         purpose="This policy makes sure Orvanta can restore its data and services after loss, attack or outage.",
         scope="All production data stores, the ledger, document stores and the corporate SaaS data Orvanta depends on.",
         roles=[("CISO", "Owns this policy."), ("Head of Platform and SRE", "Runs backups, restores and resilience."), ("COO", "Approves recovery objectives and continuity plans."),
                ("Service owners", "Confirm that restored data is complete and usable.")],
         sections=[
             ("Backup", [
                 ("Production databases and document stores are backed up at least daily. The ledger also has point-in-time recovery.", "8.13"),
                 ("Backups are copied to a separate AWS account with immutability, and to a second EU region.", "8.13"),
                 ("No single identity can delete both production data and its backups.", "8.13, 5.3"),
                 ("Backup jobs are monitored, and a failure alerts the on-call engineer.", "8.13"),
                 ("Backups are kept for the periods in the retention schedule.", "8.13, 5.33"),
                 ("Important SaaS data, including GitHub and Google Workspace, has an export or backup arrangement.", "8.13"),
             ]),
             ("Recovery", [
                 ("A full restore of each critical database is tested every quarter, and the result is recorded.", "8.13"),
                 ("Recovery time and recovery point objectives for each critical service come from the Business Impact Analysis and are approved by the COO.", "5.30"),
                 ("Critical services run across at least three availability zones.", "8.14"),
                 ("Continuity plans exist for critical processes and are exercised every year.", "5.30"),
                 ("Security controls stay in force during a disruption. Any emergency relaxation is approved by the CISO, logged and reversed afterwards.", "5.29"),
             ]),
         ],
         measures=[("Quarterly restore tests passed", "4 a year"), ("Backup jobs succeeding", "Above 99%"), ("Critical services with approved recovery objectives", "100%")],
         related="Incident Management Policy (ORV-POL-08), Cryptography and Key Management Policy (ORV-POL-05)"),

    dict(num=10, code="LM", title="Logging and Monitoring Policy", owner="R-CISO", reviewer="R-HSRE", approver="R-CISO", date="23 April 2027",
         purpose="This policy makes sure Orvanta records what happens in its systems and notices when something is wrong.",
         scope="All AWS accounts, production workloads, identity systems, source control and corporate SaaS tools.",
         roles=[("CISO", "Owns this policy, the SIEM and the detection rules."), ("Security Engineer", "Triages alerts and tunes detections."),
                ("Head of Platform and SRE", "Makes sure log sources are enabled and delivered."), ("DPO", "Advises on lawful monitoring.")],
         sections=[
             ("Logging", [
                 ("Audit logging is enabled in every AWS account and for Okta, GitHub and Google Workspace.", "8.15"),
                 ("Logs are sent to a central log account that workload administrators cannot change.", "8.15"),
                 ("Security logs are kept for at least 12 months.", "8.15"),
                 ("Logs do not contain secrets, full card numbers or personal data that is not needed.", "8.15"),
                 ("All systems take time from AWS time synchronization or an equivalent trusted source.", "8.17"),
             ]),
             ("Monitoring", [
                 ("A SIEM runs detection rules mapped to MITRE ATT&CK for the priority attack scenarios.", "8.16"),
                 ("Alerts are triaged every working day, and high-severity alerts page the on-call engineer.", "8.16"),
                 ("Detection coverage is reviewed every quarter against the threat catalog.", "8.16, 5.7"),
                 ("Privileged activity and break-glass use are reviewed every month by someone other than the person who acted.", "8.16"),
                 ("Monitoring follows privacy law, and its purposes are agreed with the DPO.", "8.16"),
                 ("Capacity and performance are monitored with alerts, and capacity is forecast every year.", "8.6"),
             ]),
         ],
         measures=[("Priority log sources in the SIEM", "100%"), ("Alerts triaged within one working day", "Above 95%"), ("Monthly privileged activity reviews completed", "100%")],
         related="Incident Management Policy (ORV-POL-08), Access Control Policy (ORV-POL-02)"),

    dict(num=11, code="RW", title="Remote Working Policy", owner="R-CISO", reviewer="R-ITOPS", approver="R-CISO", date="26 March 2027",
         purpose="This policy keeps Orvanta information safe when people work outside the office, which most staff do.",
         scope="All staff and contractors who work from home, while travelling or from any place that is not an Orvanta office.",
         roles=[("CISO", "Owns this policy."), ("IT Operations Lead", "Manages laptops through Jamf and enforces device rules in Okta."),
                ("Head of People", "Approves work from other countries with the CISO."), ("All remote workers", "Protect devices and information wherever they work.")],
         sections=[
             ("Devices", [
                 ("Company work is done only on company laptops enrolled in Jamf.", "8.1, 6.7"),
                 ("Okta blocks sign-in from devices that are not managed.", "8.1"),
                 ("Laptops have disk encryption, EDR, automatic updates, screen lock and remote wipe enforced.", "8.1, 8.7"),
                 ("EDR alerts go to the SIEM, and users cannot switch the agent off.", "8.7"),
                 ("Personal phones are used only for Okta Verify, Slack and email, through managed apps.", "8.1"),
                 ("DNS filtering for malicious sites is active on every laptop.", "8.23"),
             ]),
             ("Working away from the office", [
                 ("Remote workers use a private space, keep screens out of view and do not let others use their company device.", "6.7"),
                 ("Any network may be used, because access goes through encrypted, identity-aware connections. Shared VPN profiles are not used.", "6.7"),
                 ("Laptops are not left unattended in vehicles or public places, and a loss is reported within one hour.", "7.9"),
                 ("Work from a country outside the approved list needs approval from the Head of People and the CISO.", "6.7"),
                 ("Confidential documents are not printed outside the office.", "6.7"),
             ]),
         ],
         measures=[("Laptops enrolled in Jamf with EDR", "100%"), ("Sign-ins from unmanaged devices", "0"), ("Lost devices reported within one hour", "100%")],
         related="Acceptable Use Policy (ORV-POL-03), Asset Management and Classification Policy (ORV-POL-04), Access Control Policy (ORV-POL-02)"),

    dict(num=12, code="HR", title="Human Resources Security Policy", owner="R-CISO", reviewer="R-HPEOPLE", approver="R-CISO", date="23 April 2027",
         purpose="This policy makes sure people are suitable for their roles, understand their security duties and leave cleanly.",
         scope="All employees and contractors of Orvanta Payments UAB and Orvanta Engineering LLC, from recruitment to after they leave.",
         roles=[("CISO", "Owns this policy and the awareness program."), ("Head of People", "Runs screening, contracts, training records and the disciplinary process."),
                ("Managers", "Confirm training, asset return and handover."), ("All staff", "Complete training and keep their confidentiality duties.")],
         sections=[
             ("Before joining", [
                 ("Candidates are screened before they start: identity, right to work and references. Roles with privileged access or control of funds also have criminal record checks where the law allows.", "6.1"),
                 ("Employment and contractor agreements include confidentiality, security duties and acceptance of the security policies. Vilnius and Baku use aligned templates.", "6.2"),
                 ("Contractors and other third parties sign a non-disclosure agreement before they see Confidential information.", "6.6"),
             ]),
             ("During employment", [
                 ("New joiners complete security induction in their first week, and before they receive production access.", "6.3"),
                 ("All staff complete security training every year, with role-based modules for engineers, support and finance.", "6.3"),
                 ("Phishing simulations run every quarter, and people who click repeatedly get coaching.", "6.3"),
                 ("Policy breaches are handled under the disciplinary process, fairly and in proportion. Reporting in good faith is never penalized.", "6.4"),
             ]),
             ("Changing role or leaving", [
                 ("The Head of People tells IT Operations about leavers and movers on the day the change is confirmed.", "6.5, 5.18"),
                 ("Confidentiality duties continue after employment ends, and leavers are reminded of them at exit.", "6.5"),
                 ("Managers confirm that assets are returned and knowledge is handed over.", "5.11, 6.5"),
             ]),
         ],
         measures=[("Annual training completion", "At least 98%"), ("Phishing simulation click rate", "Under 5%"), ("New joiners screened before start", "100%")],
         related="User Access Procedure (ORV-PRC-01), Acceptable Use Policy (ORV-POL-03)"),
]

# --- Procedures ------------------------------------------------------------------------------
PROCEDURES = [
    dict(num=1, title="User Access Procedure", subtitle="Provisioning, review and offboarding of access", owner="R-ITOPS", reviewer="R-ITOPS", approver="R-CISO", date="26 March 2027",
         purpose="This procedure turns the Access Control Policy (ORV-POL-02) into steps. It covers how access is given when someone joins, changed when they move, checked every quarter and removed when they leave.",
         scope="All workforce identities in Okta and every system connected to it, plus AWS, GitHub, the Orbit console and supplier portals.",
         roles=[("Head of People", "Starts joiner, mover and leaver requests in Personio."), ("Line manager", "States the role and confirms asset return."),
                ("System owner", "Approves access to their system and reviews it every quarter."), ("IT Operations", "Makes the changes in Okta and records evidence."),
                ("Security Engineer", "Checks a sample each month and reports the metrics.")],
         flows=[("Joiner", ["HR creates the joiner in Personio", "Okta account and role group created", "Laptop enrolled, security key issued", "Induction done, then access live"]),
                ("Mover", ["HR records the new role", "New role group requested", "Owner approves, old group removed", "Change logged in Jira"]),
                ("Leaver", ["HR confirms the last day", "Okta account suspended at end of day", "Tools outside SSO checked", "Assets returned and confirmed"])],
         steps=[
             ("Joiner", [
                 ("1", "Create the joiner record with role, manager and start date, at least five working days ahead.", "Head of People", "Personio", "Joiner record"),
                 ("2", "Create the Okta account and assign the role group for the job. Role groups carry the standard access for each role.", "IT Operations", "Okta", "Jira ticket"),
                 ("3", "Request any access beyond the role group. The system owner approves or rejects it.", "Line manager, system owner", "Jira", "Approval in ticket"),
                 ("4", "Enroll the laptop in Jamf and issue a security key to administrators.", "IT Operations", "Jamf, Okta", "Device record"),
                 ("5", "Complete security induction. Production access starts only after this.", "Joiner", "Training platform", "Completion record"),
             ]),
             ("Mover", [
                 ("6", "Record the role change and its date.", "Head of People", "Personio", "Change record"),
                 ("7", "Assign the new role group and remove the old one on the same day. Access is replaced, not added.", "IT Operations", "Okta", "Jira ticket"),
                 ("8", "Confirm that special access from the old role is still needed, or remove it.", "System owner", "Jira", "Approval in ticket"),
             ]),
             ("Leaver", [
                 ("9", "Notify IT Operations on the day the departure is confirmed, with the last working day.", "Head of People", "Personio", "Leaver record"),
                 ("10", "Suspend the Okta account at the end of the last working day. For dismissals, suspend it before the conversation.", "IT Operations", "Okta", "Jira ticket with timestamp"),
                 ("11", "Check and remove accounts in any tool outside single sign-on, and revoke tokens, keys and sessions.", "IT Operations", "Checklist", "Completed checklist"),
                 ("12", "Collect the laptop and other assets, then wipe the device.", "Line manager, IT Operations", "Jamf", "Asset return record"),
                 ("13", "Delete the account after 30 days, once data has been handed over.", "IT Operations", "Okta", "Jira ticket"),
             ]),
             ("Privileged access", [
                 ("14", "Request privileged access for a named task and time window. The request is approved by a second person.", "Engineer, approver", "AWS SSO", "Access request log"),
                 ("15", "Access ends automatically when the window closes. Break-glass use raises an alert and is reviewed the next working day.", "Head of Platform and SRE", "AWS SSO, SIEM", "Review record"),
             ]),
             ("Access review", [
                 ("16", "Send each system owner the list of users and roles on their system in the first week of the quarter.", "IT Operations", "Okta reports", "Review pack"),
                 ("17", "Confirm or remove each entry within 10 working days. No response means the access is removed.", "System owner", "Jira", "Signed review"),
                 ("18", "Review privileged roles and service accounts every month.", "Head of Platform and SRE", "AWS, Okta", "Review record"),
                 ("19", "Sample five leavers and five reviews each month, and report the metrics.", "Security Engineer", "Jira", "Monthly report"),
             ]),
         ],
         metrics=[("Leaver accounts suspended within 24 hours", "100%"), ("Median time to suspend a leaver", "Under 24 hours"), ("Quarterly reviews completed within 10 working days", "100%"),
                  ("Access granted without a recorded approval", "0")],
         controls="5.15, 5.16, 5.18, 6.5, 8.2",
         related="Access Control Policy (ORV-POL-02), Human Resources Security Policy (ORV-POL-12)"),

    dict(num=2, title="Vulnerability and Patch Management Procedure", subtitle="Finding, prioritizing and fixing technical vulnerabilities", owner="R-HSRE", reviewer="R-HSRE", approver="R-CISO", date="9 April 2027",
         purpose="This procedure turns the Secure Development and Change Management Policy (ORV-POL-06) into steps. It covers how Orvanta finds vulnerabilities, decides which matter most and fixes them in time.",
         scope="All production and corporate systems: AWS infrastructure, container images, application code and dependencies, laptops and SaaS configuration.",
         roles=[("Head of Platform and SRE", "Owns this procedure and infrastructure patching."), ("Security Engineer", "Runs scanning, triages findings and reports the metrics."),
                ("Engineering heads", "Fix findings in their services within the deadline."), ("IT Operations Lead", "Patches laptops through Jamf."), ("CISO", "Approves exceptions and escalates overdue items.")],
         flows=[("Process", ["Identify", "Triage", "Assign", "Fix", "Verify", "Report"])],
         steps=[
             ("Identify", [
                 ("1", "Scan container images and dependencies in every CI pipeline, and block builds with critical findings.", "Engineers", "CI scanning", "Pipeline results"),
                 ("2", "Scan running AWS workloads and configuration continuously.", "Security Engineer", "Cloud scanning", "Findings list"),
                 ("3", "Collect findings from the yearly penetration test, supplier advisories and threat intelligence.", "Security Engineer", "Jira", "Tickets"),
             ]),
             ("Triage", [
                 ("4", "Rate each finding within two working days, using vendor severity adjusted for exposure, data sensitivity and known exploitation.", "Security Engineer", "Jira", "Severity in ticket"),
                 ("5", "Treat a finding on an internet-facing system as urgent when it is being exploited in the wild.", "Security Engineer", "Jira", "Urgent flag"),
             ]),
             ("Assign and fix", [
                 ("6", "Assign the ticket to the owning team with the deadline from the table below.", "Security Engineer", "Jira", "Assigned ticket"),
                 ("7", "Fix by patching, upgrading, changing configuration or removing the component, through the normal change process.", "Owning team", "CI pipeline", "Linked change"),
                 ("8", "Rebuild Kubernetes node images every month, and apply database engine updates in the agreed maintenance window.", "Head of Platform and SRE", "Terraform, AWS", "Change record"),
                 ("9", "Install laptop operating system and browser updates automatically within 14 days of release.", "IT Operations", "Jamf", "Compliance report"),
             ]),
             ("Verify and report", [
                 ("10", "Rescan to confirm the fix before closing the ticket.", "Security Engineer", "Scanners", "Clean scan"),
                 ("11", "Escalate overdue items to the CISO each week. An item that cannot be fixed in time needs an approved exception.", "Security Engineer", "Jira", "Escalation log"),
                 ("12", "Report open findings by severity and age to the ISMS steering meeting every month.", "Security Engineer", "Dashboard", "Monthly report"),
             ]),
         ],
         sla=[("Urgent", "Internet-facing and exploited in the wild", "48 hours"), ("Critical", "Likely to give control of a system or Restricted data", "7 days"),
              ("High", "Serious, but needs other conditions to exploit", "30 days"), ("Medium", "Limited effect or hard to exploit", "90 days"), ("Low", "Minimal effect", "Next planned release")],
         metrics=[("Critical findings fixed within 7 days", "100%"), ("High findings fixed within 30 days", "At least 95%"), ("Overdue findings without an approved exception", "0"),
                  ("Laptops fully patched", "At least 98%")],
         controls="8.8, 8.9, 8.19, 8.28, 5.21",
         related="Secure Development and Change Management Policy (ORV-POL-06), Risk Management Methodology (ORV-RISK-001)"),
]

# --- ISMS manual -----------------------------------------------------------------------------
SCOPE = dict(
    statement=("The ISMS covers the design, development, operation and support of Orvanta's merchant payment API, business accounts and card program, "
               "delivered by Orvanta Payments UAB in Vilnius and Orvanta Engineering LLC in Baku, including remote staff, and hosted in AWS eu-central-1."),
    included=[("Legal entities", "Orvanta Payments UAB and Orvanta Engineering LLC"), ("People", "All 120 employees and contractors, in Vilnius, Baku and remote"),
              ("Locations", "Vilnius office, Baku office and remote working locations"), ("Products", "Merchant Payment API, business accounts, card program"),
              ("Processes", "All twelve business processes, BP-01 to BP-12"), ("Technology", "All 26 systems in the asset register, SYS-01 to SYS-26, and the laptop fleet"),
              ("Information", "All nine data classes, including payment, personal, KYC and cardholder data")],
    interfaces=[("AWS", "Hosts production. AWS secures the facilities and underlying platform, and Orvanta secures what it builds and configures."),
                ("Tessarin Card Services", "Runs issuer processing and the card vault. These sit outside the boundary and are controlled through contract and supplier assurance."),
                ("Kyrovia Compliance", "Runs KYC and AML screening as a service. Orvanta controls the data it sends and the accounts it uses."),
                ("Vaskora Bank", "Provides SEPA access and safeguarding accounts. Orvanta controls its side of the connection and its keys."),
                ("Helvora Support", "Provides outsourced support staff who work in Orvanta's Zendesk and Orbit under Orvanta's policies.")],
    exclusions="No part of Orvanta's own operations is excluded. Supplier-run services are outside the boundary, as listed above, and are managed as dependencies.")

CONTEXT_INTERNAL = [
    ("Fast growth", "Headcount doubled in three years, and informal habits no longer scale.", "Clear policies, role-based access and onboarding training"),
    ("Two engineering sites", "Most engineers are in Baku, outside the EEA, and many staff are remote.", "Transfer safeguards, device management and remote working rules"),
    ("Delivery culture", "Teams value speed, and some changes bypassed review.", "Change control built into CI, not added as paperwork"),
    ("Small security team", "Two people supported 120 until a third joined in 2027.", "Automation, clear ownership outside the security team"),
    ("Legacy technology", "A legacy AWS account and older tools sat outside standard controls.", "Retirement plan in the risk treatment plan"),
]
CONTEXT_EXTERNAL = [
    ("Regulation", "DORA applies to Orvanta as a financial entity, alongside GDPR and payment services rules.", "Legal register, incident notification matrix, third-party register"),
    ("Customer demand", "Enterprise merchants require ISO/IEC 27001:2022 certification by 30 November 2027.", "Certification roadmap"),
    ("Threat landscape", "Payment firms attract credential theft, ransomware and fraud.", "Threat-informed risk assessment mapped to MITRE ATT&CK"),
    ("Supplier dependence", "Five critical services are outsourced.", "Supplier Security Policy and third-party risk program"),
    ("Card scheme rules", "PCI DSS applies through the card program.", "Card data kept with the processor; ticket redaction"),
]
CLIMATE = ("Orvanta considered whether climate change is a relevant issue for the ISMS, as Amendment 1:2024 asks. It concluded that the relevance is limited. Orvanta owns no data centers, "
           "and production runs in a region with three availability zones. Two points are kept under review: extreme weather could disrupt a cloud region or an office, which the Business Impact Analysis covers, "
           "and enterprise merchants may ask sustainability questions in due diligence. No interested party has set a climate-related requirement so far. The decision is reviewed every year at management review.")

# party, what they need, how Orvanta meets it
PARTIES = [
    ("Bank of Lithuania", "Sound ICT risk management, incident reporting and control of outsourcing", "Risk methodology, Incident Management Policy, Supplier Security Policy"),
    ("State Data Protection Inspectorate", "Lawful, secure processing of personal data and timely breach notification", "DPO oversight, classification, transfer safeguards, incident process"),
    ("Enterprise merchants", "ISO/IEC 27001:2022 certificate, reliable API and clear security answers", "Certification roadmap, availability targets, this ISMS"),
    ("Merchants and account holders", "Safe funds records, available payments and private data", "Access control, backup and recovery, monitoring"),
    ("Cardholders", "Protection of card data and fast response to fraud", "Card vault kept with Tessarin, ticket redaction, incident process"),
    ("Card schemes, through Tessarin", "PCI DSS compliance for any card data Orvanta touches", "Data handling rules, QSA scope review"),
    ("Vaskora Bank", "Secure handling of payment files and bank credentials", "Key management, dual approval of payout files"),
    ("Critical suppliers", "Clear requirements and a named contact", "Supplier Security Policy and contract checklist"),
    ("Employees and contractors", "Clear rules, usable tools and fair treatment", "Short policies, training, good-faith reporting"),
    ("Management Board and shareholders", "Protected revenue and licence, with visible risk", "Quarterly risk and KPI reporting"),
    ("Certification body", "A conforming, effective and evidenced ISMS", "Internal audit, management review, corrective actions"),
]

# id, objective, KPI, unit, baseline, target, latest, due, owner, data source
OBJECTIVES = [
    ("OBJ-01", "Achieve ISO/IEC 27001:2022 certification", "Certification milestones completed, of 6", "count", 0, 6, 3, "30 Nov 2027", "R-CEO", "ISMS steering minutes"),
    ("OBJ-02", "Put every workforce tool behind MFA", "Workforce tools outside Okta MFA", "count", 5, 0, 0, "31 Mar 2027", "R-ITOPS", "Okta application report"),
    ("OBJ-03", "Remove shared administrative accounts", "Shared administrative accounts", "count", 3, 0, 1, "30 Apr 2027", "R-HSRE", "AWS and Orbit account review"),
    ("OBJ-04", "Manage every laptop", "Laptops enrolled in Jamf with EDR", "%", 67, 100, 100, "31 Mar 2027", "R-ITOPS", "Jamf compliance report"),
    ("OBJ-05", "Remove leaver access within a day", "Median time to suspend a leaver account", "hours", 216, 24, 20, "31 Mar 2027", "R-ITOPS", "Jira leaver tickets"),
    ("OBJ-06", "Prove that data can be restored", "Full restore tests passed in the last 12 months", "count", 0, 4, 2, "31 Dec 2027", "R-HSRE", "Restore test records"),
    ("OBJ-07", "Detect attacks on priority systems", "Priority log sources in the SIEM", "%", 0, 100, 40, "30 Jun 2027", "R-CISO", "SIEM source inventory"),
    ("OBJ-08", "Assure critical suppliers", "Tier 1 suppliers with a current assessment, of 8", "count", 0, 8, 3, "30 Jun 2027", "R-HCOMP", "Third-party risk register"),
    ("OBJ-09", "Deploy only reviewed changes", "Production deployments through the reviewed CI path", "%", 86, 100, 97, "30 Apr 2027", "R-CTO", "Deployment log"),
    ("OBJ-10", "Build a security-aware workforce", "Annual security training completion", "%", 92, 98, 96, "30 Jun 2027", "R-HPEOPLE", "Training platform"),
]
KPI_DATE = "23 April 2027"

RACI_ROLES = ["Board", "CEO", "CISO", "Risk Mgr", "CTO", "SRE", "IT Ops", "Compl.", "DPO", "People"]
# activity, then one letter per role in RACI_ROLES order (R, A, C, I or -)
RACI = [
    ("Approve security policy and risk appetite", "A I R C I - - C C -".split()),
    ("Run the ISMS and report performance", "I A R C C I I C I I".split()),
    ("Assess and treat risks", "I A C R C C C C C -".split()),
    ("Maintain the Statement of Applicability", "- I A R C C C C C -".split()),
    ("Manage identities and access", "- - A - I C R - - C".split()),
    ("Run privileged access and cloud security", "- - A - C R C - - -".split()),
    ("Secure development and change control", "- I C - A R - - - -".split()),
    ("Log, monitor and respond to incidents", "I I A - C R C C C -".split()),
    ("Back up and recover services", "- I C - A R - - - -".split()),
    ("Assess and manage suppliers", "- I C C C - - A C -".split()),
    ("Protect personal data", "- I C - C - - C A -".split()),
    ("Screen, train and offboard people", "- - C - - - R - - A".split()),
    ("Internal audit and management review", "I A C C I I I R I I".split()),
]
