#!/usr/bin/env python3
from flask import Flask, request, jsonify, send_file
import requests, re, json
from io import BytesIO

app = Flask(__name__)

API_BASE = "https://www.clubhouseapi.com/api/"
API_TOKEN = "ac00e6e71f99fde1b7780229f7022000e493605d"

# === Profile Lookup ===
@app.route("/api/profile", methods=["GET"])
def get_profile():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400

    headers = {"Authorization": f"Token {API_TOKEN}"}
    payload = {"username": username}
    try:
        resp = requests.post(f"{API_BASE}get_profile", headers=headers, json=payload)
        resp.raise_for_status()
        data = resp.json()
        return jsonify(data.get("user_profile", {}))
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# === Download TXT ===
@app.route("/api/download", methods=["GET"])
def download_profile():
    username = request.args.get("username")
    if not username:
        return jsonify({"error": "Username is required"}), 400

    headers = {"Authorization": f"Token {API_TOKEN}"}
    payload = {"username": username}
    resp = requests.post(f"{API_BASE}get_profile", headers=headers, json=payload)
    profile = resp.json().get("user_profile", {})

    safe_name = re.sub(r'[<>:"/\\|?*]', '', profile.get("name", username))
    txt = (
        f"Name: {profile.get('name', 'N/A')}\n"
        f"Display Name: {profile.get('displayname', 'N/A')}\n"
        f"Username: {profile.get('username', 'N/A')}\n"
        f"Followers: {profile.get('num_followers', 0)}\n"
        f"Following: {profile.get('num_following', 0)}\n"
        f"Bio: {profile.get('bio', 'N/A')}\n"
        f"Created: {profile.get('time_created', 'N/A')}\n"
    )

    buf = BytesIO()
    buf.write(txt.encode('utf-8'))
    buf.seek(0)
    return send_file(buf, as_attachment=True, download_name=f"{safe_name}_profile.txt", mimetype="text/plain")


# === Profile Picture Proxy ===
@app.route("/api/photo", methods=["GET"])
def get_photo():
    url = request.args.get("url")
    if not url:
        return jsonify({"error": "Photo URL required"}), 400
    r = requests.get(url)
    return send_file(BytesIO(r.content), mimetype="image/jpeg")


# === Update Operations ===
@app.route("/api/update", methods=["POST"])
def update_profile():
    action = request.json.get("action")
    value = request.json.get("value")

    headers = {
        "Authorization": f"Token {API_TOKEN}",
        "Content-Type": "application/json; charset=utf-8"
    }

    if action == "name":
        endpoint = "update_name"
        payload = {"name": value}
    elif action == "display":
        endpoint = "update_displayname"
        payload = {"name": value}
    elif action == "username":
        endpoint = "update_username"
        payload = {"username": value}
    else:
        return jsonify({"error": "Invalid action"}), 400

    try:
        resp = requests.post(f"{API_BASE}{endpoint}", headers=headers, json=payload)
        if resp.status_code == 200:
            return jsonify({"success": True, "message": f"{action.capitalize()} updated successfully!"})
        else:
            return jsonify({"error": resp.text}), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def home():
    return jsonify({"message": "Clubhouse Automation API Active"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
