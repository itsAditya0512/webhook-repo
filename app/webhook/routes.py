from flask import Blueprint, request, jsonify, render_template
from app.extensions import mongo
from datetime import datetime

webhook = Blueprint('webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    data = request.get_json()
    print("Received GitHub webhook payload:\n", data)

    author = data.get("sender", {}).get("login", "unknown")
    timestamp = datetime.utcnow().strftime('%-d %B %Y - %-I:%M %p UTC')
    msg = None

    # Push Event
    if "commits" in data and data.get("ref"):
        to_branch = data["ref"].split("/")[-1]
        msg = f"{author} pushed to {to_branch} on {timestamp}"

    # Pull Request Opened
    elif data.get("action") == "opened" and "pull_request" in data:
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        msg = f"{author} submitted a PR from {from_branch} to {to_branch} on {timestamp}"

    # Pull Request Merged
    elif data.get("action") == "closed" and data.get("pull_request", {}).get("merged"):
        from_branch = data["pull_request"]["head"]["ref"]
        to_branch = data["pull_request"]["base"]["ref"]
        msg = f"{author} merged {from_branch} to {to_branch} on {timestamp}"

    # Unknown/Unsupported Event
    if not msg:
        print("Unhandled webhook event. No action taken.")
        return jsonify({"status": "ignored"}), 200

    print("Saving message:", msg)
    mongo.db.events.insert_one({"message": msg, "timestamp": timestamp})
    return jsonify({"status": "success"}), 200


@webhook.route('/events', methods=["GET"])
def get_events():
    data = list(mongo.db.events.find({}, {"_id": 0}))
    return jsonify(data)


@webhook.route('/', methods=["GET"])
def ui():
    return render_template("index.html")
