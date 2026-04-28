from flask import Flask, request, jsonify
import os
from supabase import create_client

app = Flask(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
GUMROAD_SECRET = os.environ.get("GUMROAD_SECRET", "echo_secret")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/verify", methods=["POST"])
def verify():
    email = request.json.get("email", "").lower().strip()
    if not email:
        return jsonify({"valid": False, "message": "No email provided"})
    result = supabase.table("licenses").select("*").eq("email", email).eq("active", True).execute()
    if result.data:
        return jsonify({"valid": True, "message": "License valid"})
    return jsonify({"valid": False, "message": "Email not found. Please purchase Echo at gumroad.com"})

@app.route("/webhook/gumroad", methods=["POST"])
def gumroad_webhook():
    secret = request.form.get("secret")
    if secret != GUMROAD_SECRET:
        return jsonify({"error": "Unauthorized"}), 401
    email = request.form.get("email", "").lower().strip()
    if email:
        supabase.table("licenses").upsert({"email": email, "active": True}).execute()
    return jsonify({"success": True})

if __name__ == "__main__":
    app.run()