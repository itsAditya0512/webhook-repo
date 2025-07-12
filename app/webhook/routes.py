from flask import Blueprint, request, jsonify, render_template
from app.extensions import mongo
from datetime import datetime

# Registering blueprint with prefix /webhook
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')


@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.get_json()
    print("Payload:", data)

    author = data.get('sender', {}).get('login', 'unknown')
    timestamp = datetime.utcnow().strftime('%-d %B %Y - %-I:%M %p UTC')

    msg = None  # Default to None

    if "commits" in data and data["commits"]:
        to_branch = data.get("ref", "").split("/")[-1]
        msg = f"{author} pushed to {to_branch} on {timestamp}"

    elif data.get("action") == "opened" and "pull_request" in data:
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        msg = f"{author} submitted a PR from {from_branch} to {to_branch} on {timestamp}"

    elif data.get("action") == "closed" and data.get("pull_request", {}).get("merged"):
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        msg = f"{author} merged {from_branch} to {to_branch} on {timestamp}"

    else:
        print("Webhook ignored — payload didn't match any event type.")
        return jsonify({"status": "ignored"}), 200

    print("Inserting to DB:", msg)
    mongo.db.events.insert_one({"message": msg, "timestamp": timestamp})
    return jsonify({"status": "success"}), 200



@webhook.route('/', methods=["GET"])
def home():
    return render_template("index.html")
