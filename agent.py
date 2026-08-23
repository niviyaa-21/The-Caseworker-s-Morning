from tools import (
    get_case_details,
    get_resident_details,
    get_documents,
    check_eligibility,
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

    def process_case(self, case_id):
        case = get_case_details(case_id)
        if not case:
            return {"error": f"Case {case_id} not found"}

        resident = get_resident_details(case["resident_id"])
        documents = get_documents(case_id)
        eligibility = check_eligibility(case_id)

        actions = [
            "Read case details",
            "Read resident details",
            "Check submitted documents",
            "Check eligibility",
        ]

        # Safe action: prepare a status change but do not submit it.
        proposed_status = "ready_for_review" if eligibility["eligible"] and documents["complete"] else "needs_attention"

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
            "actions_completed": actions,
            "proposed_action": {
                "approval_id": approval_id,
                "type": "update_case_status",
                "new_status": proposed_status,
                "reason": self._reason(documents, eligibility),
                "requires_human_approval": True,
            },
        }

    def resolve_approval(self, approval_id, approved):
        approval = self.pending_approvals.pop(approval_id, None)
        if not approval:
            return {"error": "Approval request not found or already resolved."}

        if not approved:
            ACTION_LOG.append({
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
    def _reason(documents, eligibility):
        if not documents["complete"]:
            return "Some required documents are missing."
        if not eligibility["eligible"]:
            return "The eligibility check did not pass."
        return "Required documents are complete and the eligibility check passed."
