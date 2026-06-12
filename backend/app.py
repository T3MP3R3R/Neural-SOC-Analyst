from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from analyzer import analyze_text
from history import save_incident, get_history
from report import generate_pdf
from vt import vt_lookup
import os

app = Flask(
    __name__,
    static_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'),
    template_folder=os.path.join(os.path.dirname(__file__), '..', 'frontend')
)
CORS(app)


@app.route("/")
def home():
    return send_file(os.path.join(app.template_folder, 'index.html'))


@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    text = (data or {}).get("text", "").strip()
    if not text:
        return jsonify({"error": "No input provided"}), 400
    result = analyze_text(text)
    save_incident({"input": text, "result": result})
    return jsonify({"analysis": result})


@app.route("/history", methods=["GET"])
def history():
    return jsonify(get_history())


@app.route("/report", methods=["GET"])
def report():
    buf = generate_pdf(get_history())
    return send_file(
        buf,
        as_attachment=True,
        download_name="NSA_SOC_REPORT.pdf",
        mimetype="application/pdf"
    )


@app.route("/vt", methods=["POST"])
def virustotal():
    """VirusTotal lookup — auto-detects IP / hash / URL / domain."""
    data  = request.get_json()
    query = (data or {}).get("query", "").strip()
    if not query:
        return jsonify({"error": "No query provided"}), 400
    result = vt_lookup(query)
    return jsonify(result)


@app.route("/webhook/analyze", methods=["POST"])
def webhook_analyze():
    """
    n8n webhook endpoint.
    n8n sends:  { "text": "...", "source": "email|slack|etc" }
    Returns full analysis + auto-saves to history.
    """
    data   = request.get_json()
    text   = (data or {}).get("text", "").strip()
    source = (data or {}).get("source", "n8n_webhook")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    result = analyze_text(text)
    save_incident({"input": f"[{source}] {text}", "result": result})

    return jsonify({
        "source":   source,
        "analysis": result,
        "webhook":  "NSA_PROCESSED"
    })


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)