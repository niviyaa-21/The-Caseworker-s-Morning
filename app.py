from flask import Flask, render_template, request, jsonify
from agent import CaseworkerAgent
from tools import CASES, ACTION_LOG, RESIDENTS

app = Flask(__name__)
agent = CaseworkerAgent()

@app.route("/")
def index():
    return render_template("index.html", cases=CASES)

@app.get("/api/cases")
def cases():
    return jsonify([
        {**case, "resident_name": RESIDENTS.get(case["resident_id"], {}).get("name", "Unknown")}
        for case in CASES
    ])

@app.post("/api/run")
def run_agent():
    data = request.get_json(silent=True) or {}
    case_id = data.get("case_id")
    if not case_id:
        return jsonify({"error": "case_id is required"}), 400

    result = agent.process_case(case_id)
    return jsonify(result)

@app.post("/api/triage")
def triage():
    return jsonify({"cases": agent.triage_cases(), "pending_approvals": agent.pending_approval_list()})

@app.get("/api/approvals")
def approvals():
    return jsonify(agent.pending_approval_list())

@app.post("/api/approval")
def approval():
    data = request.get_json(silent=True) or {}
    approval_id = data.get("approval_id")
    if not approval_id or not isinstance(data.get("approved"), bool):
        return jsonify({"error": "approval_id and a boolean approved value are required"}), 400
    approved = data["approved"]

    result = agent.resolve_approval(approval_id, approved)
    status = 200 if "error" not in result else 404
    return jsonify(result), status

@app.get("/api/logs")
def logs():
    return jsonify(ACTION_LOG)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
