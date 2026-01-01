from flask import Flask, request, jsonify
from flask_cors import CORS
from fake_news_agent import FakeNewsAgent

app = Flask(__name__)

CORS(
    app,
    resources={r"/verify": {"origins": "*"}},
    methods=["POST", "OPTIONS"],
    allow_headers=["Content-Type"]
)

agent = FakeNewsAgent()


@app.route("/verify", methods=["POST", "OPTIONS"])
def verify():

    if request.method == "OPTIONS":
        return "", 200

    data = request.get_json(force=True, silent=True) or {}
    text = data.get("text", "")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    result = agent.run(text)
    return jsonify(result)



@app.route("/")
def health():
    return "Fake News Agent Server Running"


if __name__ == "__main__":
    print("🚀 Starting Fake News Agent Server on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=False)
