from flask import Flask, render_template, request, jsonify
from agent import CaseworkerAgent
from tools import CASES, ACTION_LOG

app = Flask(__name__)
agent = CaseworkerAgent()

@app.route("/")
def index():
    return render_template("index.html", cases=CASES)

@app.post("/api/run")
def run_agent():
    data = request.get_json(force=True)
    case_id = data.get("case_id")
    if not case_id:
        return jsonify({"error": "case_id is required"}), 400

    result = agent.process_case(case_id)
    return jsonify(result)

@app.post("/api/approval")
def approval():
    data = request.get_json(force=True)
    approval_id = data.get("approval_id")
    approved = bool(data.get("approved"))

    result = agent.resolve_approval(approval_id, approved)
    status = 200 if "error" not in result else 404
    return jsonify(result), status

@app.get("/api/logs")
def logs():
    return jsonify(ACTION_LOG)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
