from flask import Blueprint, request, jsonify, render_template
from app.extensions import mongo
from datetime import datetime

# Registering blueprint with prefix /webhook
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')


@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.get_json()
    author = data.get("sender", {}).get("login")
    timestamp = datetime.utcnow().strftime('%-d %B %Y - %-I:%M %p UTC')

    if data.get("commits"):
        # Handle push event
        to_branch = data.get("ref", "").split("/")[-1]
        msg = f"{author} pushed to {to_branch} on {timestamp}"

    elif data.get("action") == "opened" and data.get("pull_request"):
        # Handle pull request event
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        msg = f"{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"

    elif data.get("action") == "closed" and data.get("pull_request", {}).get("merged"):
        # Handle merge event (bonus)
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        msg = f"{author} merged branch {from_branch} to {to_branch} on {timestamp}"

    else:
        return jsonify({"status": "ignored"}), 200

    # Insert into MongoDB
    mongo.db.events.insert_one({"message": msg, "timestamp": timestamp})
    return jsonify({"status": "success"}), 200


@webhook.route('/events', methods=["GET"])
def get_events():
    data = list(mongo.db.events.find({}, {"_id": 0}))
    return jsonify(data)


@webhook.route('/', methods=["GET"])
def home():
    return render_template("index.html")
