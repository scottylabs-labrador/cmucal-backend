# app/routes/admin.py

from flask import Blueprint, jsonify, request
import os
from threading import Thread

from scraper.scripts.export_soc import export_soc_safe

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/export_soc", methods=["POST"])
def trigger_export_soc():
    token = request.headers.get("X-Admin-Token")
    if token != os.getenv("ADMIN_TOKEN"):
        return jsonify({"error": "unauthorized"}), 401

    Thread(target=export_soc_safe, daemon=True).start()
    return jsonify({"status": "SOC export started"}), 202
