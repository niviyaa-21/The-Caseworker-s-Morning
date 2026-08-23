from datetime import datetime

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
]

RESIDENTS = {
    "R001": {"name": "Asha Kumar", "language": "English", "contact": "asha@example.test"},
    "R002": {"name": "Daniel Joseph", "language": "English", "contact": "daniel@example.test"},
    "R003": {"name": "Meena Ravi", "language": "Tamil", "contact": "meena@example.test"},
}

DOCUMENTS = {
    "1001": {"required": 3, "submitted": 3, "complete": True},
    "1002": {"required": 3, "submitted": 2, "complete": False},
    "1003": {"required": 3, "submitted": 3, "complete": True},
}

ELIGIBILITY = {
    "1001": {"eligible": True, "reason": "All prototype checks passed."},
    "1002": {"eligible": True, "reason": "Eligibility appears satisfied, but documents are incomplete."},
    "1003": {"eligible": False, "reason": "Prototype income threshold check failed."},
}

ACTION_LOG = []


def _log(event, **details):
    ACTION_LOG.append({
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "event": event,
        **details,
    })


def get_case_details(case_id):
    case = next((c for c in CASES if c["case_id"] == case_id), None)
    _log("read_case", case_id=case_id, found=bool(case))
    return dict(case) if case else None


def get_resident_details(resident_id):
    resident = RESIDENTS.get(resident_id)
    _log("read_resident", resident_id=resident_id, found=bool(resident))
    return dict(resident) if resident else None


def get_documents(case_id):
    docs = DOCUMENTS.get(case_id, {"required": 0, "submitted": 0, "complete": False})
    _log("read_documents", case_id=case_id)
    return dict(docs)


def check_eligibility(case_id):
    result = ELIGIBILITY.get(case_id, {"eligible": False, "reason": "No eligibility result."})
    _log("check_eligibility", case_id=case_id, eligible=result["eligible"])
    return dict(result)


def update_case_status(case_id, new_status):
    # This is intentionally classified as a high-impact action.
    case = next((c for c in CASES if c["case_id"] == case_id), None)
    if not case:
        return {"success": False, "message": "Case not found."}

    old_status = case["status"]
    case["status"] = new_status

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
