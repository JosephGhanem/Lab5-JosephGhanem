"""Run with python app.py, then import the supplied Postman files."""

import os
import sqlite3

from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import HTTPException

import database as db


def create_app(database_path=None):
    app = Flask(__name__)
    app.config["DATABASE"] = database_path or os.environ.get("DATABASE_PATH", str(db.DEFAULT_DATABASE))
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.create_db_table(app.config["DATABASE"])

    def payload(require_id=False):
        user = request.get_json()
        if not isinstance(user, dict):
            return None, "The JSON body must be an object."
        for field in db.FIELDS:
            if not isinstance(user.get(field), str) or not user[field].strip():
                return None, f"{field} must be a nonempty string."
        if require_id and (type(user.get("user_id")) is not int or user["user_id"] < 1):
            return None, "user_id must be a positive integer."
        return user, None

    @app.get("/api/users")
    def api_get_users():
        return jsonify(db.get_users(app.config["DATABASE"]))

    @app.get("/api/users/<int:user_id>")
    def api_get_user(user_id):
        user = db.get_user_by_id(user_id, app.config["DATABASE"])
        return jsonify(user) if user else (jsonify(error="User not found."), 404)

    @app.post("/api/users/add")
    def api_add_user():
        user, error = payload()
        if error:
            return jsonify(error=error), 400
        return jsonify(db.insert_user(user, app.config["DATABASE"])), 201

    @app.put("/api/users/update")
    def api_update_user():
        user, error = payload(require_id=True)
        if error:
            return jsonify(error=error), 400
        updated = db.update_user(user, app.config["DATABASE"])
        return jsonify(updated) if updated else (jsonify(error="User not found."), 404)

    @app.delete("/api/users/delete/<int:user_id>")
    def api_delete_user(user_id):
        if not db.delete_user(user_id, app.config["DATABASE"]):
            return jsonify(error="User not found."), 404
        return jsonify(status="User deleted successfully")

    @app.errorhandler(HTTPException)
    def http_error(error):
        return jsonify(error=error.description), error.code

    @app.errorhandler(sqlite3.Error)
    def database_error(error):
        app.logger.error("Database operation failed: %s", error)
        return jsonify(error="Database operation failed."), 500

    return app


if __name__ == "__main__":
    create_app().run(host="127.0.0.1", port=int(os.environ.get("PORT", "5000")))
