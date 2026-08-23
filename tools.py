from datetime import datetime

from database import store

# -------------------------------------------------------------------
# Mock data layer
# Replace these dictionaries/functions with real APIs in production.
# -------------------------------------------------------------------

CASES = [
    {
        "case_id": "1001",
        "resident_id": "R001",
        "program": "Housing Assistance",
        "status": "pending",
    },
    {
        "case_id": "1002",
        "resident_id": "R002",
        "program": "Food Assistance",
        "status": "pending",
    },
    {
        "case_id": "1003",
        "resident_id": "R003",
        "program": "Childcare Assistance",
        "status": "pending",
    },
    {
        "case_id": "1004",
        "resident_id": "R004",
        "program": "Energy Assistance",
        "status": "completed",
    },
]

RESIDENTS = {
    "R001": {"name": "Asha Kumar", "language": "English", "contact": "asha@example.test"},
    "R002": {"name": "Daniel Joseph", "language": "English", "contact": "daniel@example.test"},
    "R003": {"name": "Meena Ravi", "language": "Tamil", "contact": "meena@example.test"},
    "R004": {"name": "Jordan Lee", "language": "English", "contact": "jordan@example.test"},
}

DOCUMENTS = {
    "1001": {
        "required": 3,
        "submitted": 3,
        "complete": True,
        "items": [
            {"name": "Proof of identity", "submitted": True},
            {"name": "Proof of address", "submitted": True},
            {"name": "Income statement", "submitted": True},
        ],
    },
    "1002": {
        "required": 3,
        "submitted": 2,
        "complete": False,
        "items": [
            {"name": "Proof of identity", "submitted": True},
            {"name": "Proof of address", "submitted": True},
            {"name": "Income statement", "submitted": False},
        ],
    },
    "1003": {
        "required": 3,
        "submitted": 3,
        "complete": True,
        "items": [
            {"name": "Proof of identity", "submitted": True},
            {"name": "Proof of address", "submitted": True},
            {"name": "Childcare cost certificate", "submitted": True},
        ],
    },
    "1004": {
        "required": 3,
        "submitted": 3,
        "complete": True,
        "items": [
            {"name": "Proof of identity", "submitted": True},
            {"name": "Proof of address", "submitted": True},
            {"name": "Energy bill statement", "submitted": True},
        ],
    },
}

ELIGIBILITY = {
    "1001": {"eligible": True, "reason": "All prototype checks passed."},
    "1002": {"eligible": True, "reason": "Eligibility appears satisfied, but documents are incomplete."},
    "1003": {"eligible": False, "reason": "Prototype income threshold check failed."},
    "1004": {"eligible": True, "reason": "Eligibility review completed successfully."},
}

CERTIFICATES = {
    "1001": {
        "present": True,
        "original": True,
        "certificate_type": "Housing eligibility certificate",
        "verification_method": "Issuing authority reference matched",
        "reason": "Certificate reference and issuing authority record matched.",
    },
    "1002": {
        "present": False,
        "original": False,
        "certificate_type": "Housing eligibility certificate",
        "verification_method": "Not checked",
        "reason": "No certificate was submitted.",
    },
    "1003": {
        "present": True,
        "original": False,
        "certificate_type": "Childcare eligibility certificate",
        "verification_method": "Duplicate reference found",
        "reason": "The certificate reference matches a previously submitted document.",
    },
}

ACTION_LOG = []

PROGRAM_REQUIREMENTS = {
    "Housing Assistance": {
        "fields": ["Monthly household income", "Household size"],
        "documents": ["Proof of identity", "Proof of address", "Income statement"],
        "optional_documents": ["Housing eligibility certificate"],
    },
    "Food Assistance": {
        "fields": ["Monthly household income", "Household size"],
        "documents": ["Proof of identity", "Proof of address", "Income statement"],
        "optional_documents": ["Food eligibility certificate"],
    },
    "Childcare Assistance": {
        "fields": ["Monthly household income", "Number of children", "Childcare provider"],
        "documents": ["Proof of identity", "Childcare cost certificate", "Child enrollment record"],
        "optional_documents": [],
    },
    "Energy Assistance": {
        "fields": ["Monthly household income", "Service address"],
        "documents": ["Proof of identity", "Proof of address", "Energy bill statement"],
        "optional_documents": ["Energy eligibility certificate"],
    },
    "Transport Assistance": {
        "fields": ["Monthly household income", "Transport need"],
        "documents": ["Proof of identity", "Proof of address", "Transport need statement"],
        "optional_documents": ["Transport eligibility certificate"],
    },
}

store.seed_or_load(CASES, RESIDENTS, DOCUMENTS, ELIGIBILITY, CERTIFICATES)


def _log(event, **details):
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "event": event,
        **details,
    }
    ACTION_LOG.append(entry)
    store.log(entry)


def get_case_details(case_id):
    case = next((c for c in CASES if c["case_id"] == case_id), None)
    _log("read_case", case_id=case_id, found=bool(case))
    return dict(case) if case else None


def create_case(name, program, language, contact, fields=None, submitted_documents=None):
    requirements = PROGRAM_REQUIREMENTS[program]
    submitted_documents = submitted_documents or []
    next_number = max((int(case["case_id"]) for case in CASES), default=1000) + 1
    case_id = str(next_number)
    resident_id = f"R{next_number:03d}"
    RESIDENTS[resident_id] = {
        "name": name,
        "language": language,
        "contact": contact,
    }
    CASES.append({
        "case_id": case_id,
        "resident_id": resident_id,
        "program": program,
        "status": "pending",
        "fields": fields or {},
    })
    store.save_resident(resident_id, RESIDENTS[resident_id])
    items = [{"name": document, "submitted": document in submitted_documents} for document in requirements["documents"]]
    DOCUMENTS[case_id] = {
        "required": len(items),
        "submitted": sum(item["submitted"] for item in items),
        "complete": all(item["submitted"] for item in items),
        "items": items,
    }
    store.save_case(CASES[-1])
    store.save_documents(case_id, DOCUMENTS[case_id])
    ELIGIBILITY[case_id] = {
        "eligible": False,
        "reason": "Eligibility has not been reviewed yet.",
    }
    store.save_eligibility(case_id, ELIGIBILITY[case_id])
    certificate_present = any("certificate" in document.lower() for document in submitted_documents)
    CERTIFICATES[case_id] = {
        "present": certificate_present,
        "original": False,
        "certificate_type": f"{program} certificate",
        "verification_method": "Pending human verification" if certificate_present else "Not checked",
        "reason": "Certificate submitted; originality requires human verification." if certificate_present else "No certificate was submitted.",
    }
    store.save_certificate(case_id, CERTIFICATES[case_id])
    _log("case_created", case_id=case_id, resident_id=resident_id, program=program)
    return dict(CASES[-1])


def get_resident_details(resident_id):
    resident = RESIDENTS.get(resident_id)
    _log("read_resident", resident_id=resident_id, found=bool(resident))
    return dict(resident) if resident else None


def get_documents(case_id):
    docs = DOCUMENTS.get(case_id, {
        "required": 0,
        "submitted": 0,
        "complete": False,
        "items": [],
    })
    _log("read_documents", case_id=case_id)
    return dict(docs)


def check_eligibility(case_id):
    result = ELIGIBILITY.get(case_id, {"eligible": False, "reason": "No eligibility result."})
    _log("check_eligibility", case_id=case_id, eligible=result["eligible"])
    return dict(result)


def check_certificate(case_id):
    certificate = CERTIFICATES.get(case_id, {
        "present": False,
        "original": False,
        "certificate_type": "Unknown",
        "verification_method": "Not checked",
        "reason": "No certificate record was found.",
    })
    _log(
        "check_certificate",
        case_id=case_id,
        present=certificate["present"],
        original=certificate["original"],
    )
    return dict(certificate)


def record_certificate_submission(case_id, certificate_type=None):
    certificate = CERTIFICATES.get(case_id)
    if certificate is None:
        return None

    certificate = dict(certificate)
    certificate["present"] = True
    certificate["original"] = False
    certificate["certificate_type"] = certificate_type or certificate["certificate_type"]
    certificate["verification_method"] = "Pending human verification"
    certificate["reason"] = "Certificate submitted; originality requires human verification."
    CERTIFICATES[case_id] = certificate
    store.save_certificate(case_id, certificate)
    _log("certificate_submitted", case_id=case_id, certificate_type=certificate["certificate_type"])
    return dict(certificate)


def update_case_status(case_id, new_status):
    # This is intentionally classified as a high-impact action.
    case = next((c for c in CASES if c["case_id"] == case_id), None)
    if not case:
        return {"success": False, "message": "Case not found."}

    old_status = case["status"]
    case["status"] = new_status
    store.save_case(case)

    _log(
        "case_status_changed",
        case_id=case_id,
        old_status=old_status,
        new_status=new_status,
    )

    return {
        "success": True,
        "case_id": case_id,
        "old_status": old_status,
        "new_status": new_status,
    }


def send_notification(case_id, message):
    # Example of another tool that should be protected by approval
    # in a real benefits system.
    _log("notification_sent", case_id=case_id, message=message)
    return {"success": True}
