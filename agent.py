from datetime import datetime

from tools import (
    get_case_details,
    get_resident_details,
    get_documents,
    check_eligibility,
    check_certificate,
    update_case_status,
    send_notification,
    ACTION_LOG,
)

class CaseworkerAgent:
    """
    Prototype agent.

    The 'brain' decides the next workflow step.
    Tools perform actual operations.
    High-impact/irreversible actions require human approval.
    """

    def __init__(self):
        self.pending_approvals = {}

    def triage_cases(self):
        """Run the read-only checks for every case that still needs work."""
        results = []
        for case in self._pending_cases():
            result = self.process_case(case["case_id"])
            if "error" not in result:
                results.append(self._triage_summary(result))
        return results

    def pending_approval_list(self):
        return [
            {"approval_id": approval_id, **approval}
            for approval_id, approval in self.pending_approvals.items()
        ]

    def process_case(self, case_id):
        case = get_case_details(case_id)
        if not case:
            return {"error": f"Case {case_id} not found"}

        resident = get_resident_details(case["resident_id"])
        documents = get_documents(case_id)
        eligibility = check_eligibility(case_id)
        certificate = check_certificate(case_id)

        actions = [
            "Read case details",
            "Read resident details",
            "Check submitted documents",
            "Check eligibility",
            "Verify certificate presence and originality",
        ]

        # Safe action: prepare a status change but do not submit it.
        proposed_status = "ready_for_review" if (
            eligibility["eligible"]
            and documents["complete"]
            and certificate["present"]
            and certificate["original"]
        ) else "needs_attention"

        approval_id = f"APR-{case_id}"
        self.pending_approvals[approval_id] = {
            "case_id": case_id,
            "action": "update_case_status",
            "new_status": proposed_status,
        }

        return {
            "case": case,
            "resident": resident,
            "documents": documents,
            "eligibility": eligibility,
            "certificate": certificate,
            "actions_completed": actions,
            "proposed_action": {
                "approval_id": approval_id,
                "type": "update_case_status",
                "new_status": proposed_status,
                "reason": self._reason(documents, eligibility, certificate),
                "requires_human_approval": True,
            },
        }

    @staticmethod
    def _pending_cases():
        from tools import CASES
        return [case for case in CASES if case["status"] == "pending"]

    @staticmethod
    def _triage_summary(result):
        documents = result["documents"]
        eligibility = result["eligibility"]
        return {
            "case": result["case"],
            "resident": result["resident"],
            "documents": documents,
            "certificate": result["certificate"],
            "eligibility": eligibility,
            "priority": "high" if (
                not documents["complete"]
                or not eligibility["eligible"]
                or not result["certificate"]["present"]
                or not result["certificate"]["original"]
            ) else "normal",
            "recommendation": result["proposed_action"],
        }

    def resolve_approval(self, approval_id, approved):
        approval = self.pending_approvals.pop(approval_id, None)
        if not approval:
            return {"error": "Approval request not found or already resolved."}

        if not approved:
            ACTION_LOG.append({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "event": "human_rejected",
                "approval_id": approval_id,
                "case_id": approval["case_id"],
            })
            return {
                "status": "rejected",
                "message": "The proposed action was not executed."
            }

        result = update_case_status(
            approval["case_id"],
            approval["new_status"]
        )

        # Example of a second high-impact action:
        # In a real system, sending an official notice would also require approval.
        ACTION_LOG.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "event": "human_approved",
            "approval_id": approval_id,
            "case_id": approval["case_id"],
            "result": result,
        })

        return {
            "status": "approved",
            "message": "The approved action was executed.",
            "result": result,
        }

    @staticmethod
    def _reason(documents, eligibility, certificate):
        reasons = []
        if not documents["complete"]:
            reasons.append("Some required documents are missing")
        if not eligibility["eligible"]:
            reasons.append("The eligibility check did not pass")
        if not certificate["present"]:
            reasons.append("The required certificate was not submitted")
        elif not certificate["original"]:
            reasons.append("The submitted certificate could not be verified as original")
        if reasons:
            return ". ".join(reasons) + "."
        return "Required documents, eligibility, and certificate verification passed."
