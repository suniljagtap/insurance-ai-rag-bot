from rapidfuzz import fuzz

INSURANCE_KEYWORDS = [
    # =====================================
    # General Insurance
    # =====================================
    "insurance",
    "policy",
    "policies",
    "insured",
    "insurer",
    "insurance company",
    "coverage",
    "cover",
    "premium",
    "renewal",
    "rider",
    "add-on",
    "endorsement",
    "nominee",
    "beneficiary",
    "sum insured",
    "policy clause",
    "coverage clause",
    "exclusion",


    # =====================================
    # Policy Status / Eligibility
    # =====================================
    "active policy",
    "inactive policy",
    "policy period",
    "coverage period",
    "policy inception",
    "inception date",
    "policy start date",
    "expiry date",
    "policy expiry",
    "lapsed policy",
    "lapse",
    "grace period",
    "territorial limits",
    "territorial coverage",


    # =====================================
    # Claim Related
    # =====================================
    "claim",
    "claims",
    "claim process",
    "claim status",
    "claim eligibility",
    "claim approval",
    "claim rejection",
    "claim settlement",
    "claim decision",
    "claim amount",
    "claim review",
    "claim dispute",
    "claim submission",
    "claim processing",
    "claim intimation",
    "claim notification",
    "settlement",
    "settle",
    "compensation",
    "reimbursement",
    "loss",
    "damage",
    "incident",
    "reported incident",
    "accident",


    # =====================================
    # Motor Insurance
    # =====================================
    "motor insurance",
    "motor policy",
    "motor claim",
    "vehicle insurance",
    "vehicle claim",
    "car insurance",
    "bike insurance",
    "private vehicle",
    "commercial vehicle",
    "vehicle damage",
    "accident claim",
    "own damage",
    "od cover",
    "third party",
    "third party liability",
    "third party claim",
    "personal accident cover",
    "idv",
    "insured declared value",
    "total loss",
    "partial loss",
    "repair claim",
    "repair estimate",
    "repair cost",
    "depreciation",
    "zero depreciation",
    "salvage",
    "salvage value",
    "stolen vehicle",
    "vehicle theft",
    "theft claim",
    "engine damage",
    "mechanical breakdown",
    "electrical breakdown",
    "roadside assistance",
    "towing",
    "flood damage",
    "water ingress",
    "hydrostatic lock",
    "natural disaster",
    "cyclone",
    "earthquake",
    "riot",
    "civil commotion",
    "stfi",
    "strike riot civil commotion",
    "fitness certificate",
    "puc",


    # =====================================
    # Health Insurance
    # =====================================
    "health insurance",
    "health policy",
    "health claim",
    "medical insurance",
    "hospitalization",
    "hospital admission",
    "hospital bill",
    "medical expense",
    "medical treatment",
    "doctor",
    "medicine",
    "cashless",
    "cashless claim",
    "cashless hospitalization",
    "reimbursement claim",
    "network hospital",
    "non-network hospital",
    "discharge summary",
    "pre authorization",
    "authorization request",
    "planned surgery",
    "treatment plan",
    "critical illness",
    "maternity",
    "maternity claim",
    "day care",
    "daycare procedure",
    "opd",
    "outpatient",
    "icu",
    "room rent",
    "mental health",
    "ambulance",
    "waiting period",
    "survival period",
    "co-payment",
    "copay",
    "sub-limit",


    # =====================================
    # Group Insurance
    # =====================================
    "group insurance",
    "group health insurance",
    "employee insurance",
    "employee health policy",
    "member",
    "policy member",
    "member enrollment",
    "policy roster",
    "active member",
    "removed member",
    "group policy",
    "group health claim",


    # =====================================
    # Home Insurance
    # =====================================
    "home insurance",
    "house insurance",
    "property insurance",
    "residential property",
    "building insurance",
    "contents insurance",
    "contents cover",
    "burglary",
    "theft of valuables",
    "jewelry",
    "electronics",
    "laptop damage",
    "flood claim",
    "earthquake cover",
    "act of god",
    "natural catastrophe",
    "water damage",


    # =====================================
    # Documents
    # =====================================
    "document",
    "documents",
    "document verification",
    "document checklist",
    "required documents",
    "missing documents",
    "document deficiency",
    "document completeness",
    "policy copy",
    "claim form",
    "fir",
    "first information report",
    "vehicle registration certificate",
    "registration certificate",
    "rc",
    "rc book",
    "driving license",
    "original keys",
    "form 35",
    "noc",
    "financier",
    "cancelled cheque",
    "photographs",
    "damage photos",
    "repair estimate",
    "surveyor report",
    "loss estimate",
    "flood confirmation",
    "municipal confirmation",
    "meteorological authority",
    "scanned pdf",
    "digital documents",
    "document integrity",
    "duplicate documents",
    "evidence",
    "records",
    "certificate",
    "invoice",
    "receipt",
    "bill",


    # =====================================
    # Payout Calculation
    # =====================================
    "payout",
    "claim payout",
    "payout calculation",
    "deductible",
    "depreciation value",
    "salvage deduction",
    "insured value",
    "idv calculation",
    "policy limit",
    "maximum payout",
    "claim cap",


    # =====================================
    # Fraud Detection
    # =====================================
    "fraud",
    "fraud detection",
    "fraud investigation",
    "fraud score",
    "risk score",
    "risk assessment",
    "suspicious claim",
    "duplicate claim",
    "repeat claim",
    "staged accident",
    "false claim",
    "document anomaly",
    "damage variance",
    "claim frequency",
    "under investigation",
    "investigation report",
    "investigator",


    # =====================================
    # Claim Workflow
    # =====================================
    "submitted",
    "under review",
    "documents pending",
    "approved",
    "partially approved",
    "partially settled",
    "rejected",
    "appeal",
    "reinvestigation",
    "escalation",
    "senior underwriter",
    "field verification",
    "document audit",
    "audit trail",
    "reasoning trail",
    "decision log",


    # =====================================
    # IRDAI / Compliance
    # =====================================
    "irdai",
    "irdai guidelines",
    "regulation",
    "compliance",
    "turnaround time",
    "settlement timeline",
    "delay",
    "interest",
    "claim rejection reason",
    "written explanation",
    "policyholder rights",
    "grievance",
    "grievance cell",
    "insurance ombudsman",
    "consumer court",
    "regulatory complaint"
]


def insurance_guardrail(question):

    question = question.casefold().strip()

    matched_keywords = []


    for keyword in INSURANCE_KEYWORDS:

        keyword = keyword.casefold()


        # Exact match
        if keyword in question:
            matched_keywords.append(keyword)


        else:
            # Fuzzy match for spelling mistakes
            score = fuzz.partial_ratio(
                keyword,
                question
            )


            if score >= 85:
                matched_keywords.append(keyword)


    if matched_keywords:

        return {
            "allowed": True,
            "matched": matched_keywords
        }


    return {
        "allowed": False,
        "matched": []
    }