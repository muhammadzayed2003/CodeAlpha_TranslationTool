import os
import secrets
import sqlite3
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.security import check_password_hash, generate_password_hash


app = Flask(__name__)
CORS(app)

GEMINI_API_URL = (
    "https://generativelanguage.googleapis.com/"
    "v1beta/models/gemini-3.1-flash-lite:generateContent"
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "translatex.db")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            source_language TEXT NOT NULL,
            target_language TEXT NOT NULL,
            original_text TEXT NOT NULL,
            translated_text TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    connection.commit()
    connection.close()


def get_user_from_token():
    token = request.headers.get("Authorization", "").replace(
        "Bearer ", ""
    ).strip()

    if not token:
        return None

    connection = get_db()

    row = connection.execute("""
        SELECT users.*
        FROM users
        INNER JOIN sessions
            ON users.id = sessions.user_id
        WHERE sessions.token = ?
    """, (token,)).fetchone()

    connection.close()

    return row


@app.route("/api/signup", methods=["POST"])
def signup():
    try:
        data = request.get_json(silent=True) or {}

        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))

        if not name or not email or not password:
            return jsonify({
                "error": "Name, email and password are required."
            }), 400

        if len(password) < 6:
            return jsonify({
                "error": "Password must be at least 6 characters."
            }), 400

        connection = get_db()

        existing_user = connection.execute(
            "SELECT id FROM users WHERE email = ?",
            (email,)
        ).fetchone()

        if existing_user:
            connection.close()

            return jsonify({
                "error": "An account with this email already exists."
            }), 409

        cursor = connection.execute("""
            INSERT INTO users (
                name,
                email,
                password,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            name,
            email,
            generate_password_hash(password),
            datetime.now(timezone.utc).isoformat()
        ))

        user_id = cursor.lastrowid

        token = secrets.token_urlsafe(32)

        connection.execute("""
            INSERT INTO sessions (
                user_id,
                token,
                created_at
            )
            VALUES (?, ?, ?)
        """, (
            user_id,
            token,
            datetime.now(timezone.utc).isoformat()
        ))

        connection.commit()
        connection.close()

        return jsonify({
            "message": "Account created successfully.",
            "token": token,
            "user": {
                "id": user_id,
                "name": name,
                "email": email
            }
        }), 201

    except sqlite3.Error:
        return jsonify({
            "error": "Could not create your account."
        }), 500

    except Exception as error:
        print("Signup error:", error)

        return jsonify({
            "error": "An unexpected error occurred."
        }), 500


@app.route("/api/login", methods=["POST"])
def login():
    try:
        data = request.get_json(silent=True) or {}

        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", ""))

        if not email or not password:
            return jsonify({
                "error": "Email and password are required."
            }), 400

        connection = get_db()

        user = connection.execute("""
            SELECT *
            FROM users
            WHERE email = ?
        """, (email,)).fetchone()

        if not user or not check_password_hash(
            user["password"],
            password
        ):
            connection.close()

            return jsonify({
                "error": "Invalid email or password."
            }), 401

        token = secrets.token_urlsafe(32)

        connection.execute("""
            INSERT INTO sessions (
                user_id,
                token,
                created_at
            )
            VALUES (?, ?, ?)
        """, (
            user["id"],
            token,
            datetime.now(timezone.utc).isoformat()
        ))

        connection.commit()
        connection.close()

        return jsonify({
            "message": "Login successful.",
            "token": token,
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"]
            }
        })

    except Exception as error:
        print("Login error:", error)

        return jsonify({
            "error": "An unexpected error occurred."
        }), 500


@app.route("/api/logout", methods=["POST"])
def logout():
    token = request.headers.get("Authorization", "").replace(
        "Bearer ", ""
    ).strip()

    if token:
        connection = get_db()

        connection.execute(
            "DELETE FROM sessions WHERE token = ?",
            (token,)
        )

        connection.commit()
        connection.close()

    return jsonify({
        "message": "Logged out successfully."
    })


@app.route("/api/me", methods=["GET"])
def me():
    user = get_user_from_token()

    if not user:
        return jsonify({
            "error": "Authentication required."
        }), 401

    return jsonify({
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    })


@app.route("/api/translate", methods=["POST"])
def translate():
    try:
        user = get_user_from_token()

        if not user:
            return jsonify({
                "error": "Please login to use the translator."
            }), 401

        data = request.get_json(silent=True) or {}

        text = str(data.get("text", "")).strip()
        source = str(data.get("source", "English")).strip()
        target = str(data.get("target", "Urdu")).strip()

        if not text:
            return jsonify({
                "error": "Please enter text to translate."
            }), 400

        if not source or not target:
            return jsonify({
                "error": "Source and target languages are required."
            }), 400

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            return jsonify({
                "error": (
                    "Gemini API key not found. "
                    "Please set GEMINI_API_KEY."
                )
            }), 500

        prompt = f"""
Translate the following text from {source} to {target}.

Rules:
1. Return ONLY the translated text.
2. Do not add explanations.
3. Do not add quotation marks.
4. Preserve the original meaning and tone.
5. Preserve paragraphs and line breaks where possible.
6. Do not translate names, URLs, email addresses, or code unnecessarily.
7. Treat the source and target language names exactly as provided.

Text:
{text}
"""

        headers = {
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 4096,
            },
        }

        response = requests.post(
            GEMINI_API_URL,
            headers=headers,
            json=payload,
            timeout=45,
        )

        if response.status_code != 200:
            try:
                error_data = response.json()

                error_message = (
                    error_data.get("error", {}).get(
                        "message",
                        "Gemini API request failed."
                    )
                )

            except ValueError:
                error_message = "Gemini API request failed."

            return jsonify({
                "error": error_message
            }), response.status_code

        result = response.json()

        candidates = result.get("candidates", [])

        if not candidates:
            return jsonify({
                "error": "Gemini returned no translation."
            }), 502

        parts = (
            candidates[0]
            .get("content", {})
            .get("parts", [])
        )

        translated_text = ""

        for part in parts:
            if "text" in part:
                translated_text += part["text"]

        translated_text = translated_text.strip()

        if not translated_text:
            return jsonify({
                "error": "Gemini returned an empty translation."
            }), 502

        connection = get_db()

        connection.execute("""
            INSERT INTO translations (
                user_id,
                source_language,
                target_language,
                original_text,
                translated_text,
                created_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user["id"],
            source,
            target,
            text,
            translated_text,
            datetime.now(timezone.utc).isoformat()
        ))

        connection.commit()
        connection.close()

        return jsonify({
            "translation": translated_text
        })

    except requests.Timeout:
        return jsonify({
            "error": "Translation request timed out. Please try again."
        }), 504

    except requests.RequestException:
        return jsonify({
            "error": "Could not connect to the translation service."
        }), 502

    except Exception as error:
        print("Server error:", error)

        return jsonify({
            "error": "An unexpected server error occurred."
        }), 500


@app.route("/api/history", methods=["GET"])
def history():
    user = get_user_from_token()

    if not user:
        return jsonify({
            "error": "Authentication required."
        }), 401

    connection = get_db()

    rows = connection.execute("""
        SELECT
            id,
            source_language,
            target_language,
            original_text,
            translated_text,
            created_at
        FROM translations
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user["id"],)).fetchall()

    connection.close()

    translations = []

    for row in rows:
        translations.append({
            "id": row["id"],
            "source_language": row["source_language"],
            "target_language": row["target_language"],
            "original_text": row["original_text"],
            "translated_text": row["translated_text"],
            "created_at": row["created_at"]
        })

    return jsonify({
        "translations": translations
    })


@app.route("/api/history/<int:translation_id>", methods=["DELETE"])
def delete_history_item(translation_id):
    user = get_user_from_token()

    if not user:
        return jsonify({
            "error": "Authentication required."
        }), 401

    connection = get_db()

    connection.execute("""
        DELETE FROM translations
        WHERE id = ?
        AND user_id = ?
    """, (
        translation_id,
        user["id"]
    ))

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Translation deleted."
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "TranslateX API"
    })


init_db()


if __name__ == "__main__":
    print("=" * 55)
    print("TranslateX API")
    print("Server: http://127.0.0.1:5000")
    print("=" * 55)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )