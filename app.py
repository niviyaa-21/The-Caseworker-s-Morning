from flask import Flask, render_template, request, jsonify
from agent import CaseworkerAgent
from tools import CASES, ACTION_LOG, RESIDENTS, PROGRAM_REQUIREMENTS, create_case

app = Flask(__name__)
agent = CaseworkerAgent()

@app.route("/")
def index():
    return render_template("index.html", cases=CASES, programs=PROGRAM_REQUIREMENTS)

@app.get("/api/cases")
def cases():
    return jsonify([
        {**case, "resident_name": RESIDENTS.get(case["resident_id"], {}).get("name", "Unknown")}
        for case in CASES
    ])

@app.get("/api/program-requirements")
def program_requirements():
    return jsonify(PROGRAM_REQUIREMENTS)

@app.get("/case/<case_id>")
def case_detail(case_id):
    return render_template("case_detail.html", case_id=case_id)

@app.post("/api/cases")
def add_case():
    data = request.get_json(silent=True) or {}
    required = ("name", "program", "language", "contact")
    if any(not isinstance(data.get(field), str) or not data[field].strip() for field in required):
        return jsonify({"error": "name, program, language, and contact are required"}), 400
    program = data["program"].strip()
    if program not in PROGRAM_REQUIREMENTS:
        return jsonify({"error": "Select a valid benefit program"}), 400
    fields = data.get("fields", {})
    submitted_documents = data.get("submitted_documents", [])
    if not isinstance(fields, dict) or not isinstance(submitted_documents, list):
        return jsonify({"error": "fields must be an object and submitted_documents must be a list"}), 400
    allowed_documents = PROGRAM_REQUIREMENTS[program]["documents"]
    if any(document not in allowed_documents for document in submitted_documents):
        return jsonify({"error": "One or more submitted documents are not required for this program"}), 400
    case = create_case(*(data[field].strip() for field in required), fields, submitted_documents)
    return jsonify(case), 201

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
