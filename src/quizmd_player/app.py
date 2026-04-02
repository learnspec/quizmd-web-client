"""Flask application for QuizMD Player."""

from __future__ import annotations

from flask import Flask, jsonify, render_template, request

from pylearnspec import parse_quiz

from .github import (
    QuizSource,
    fetch_file_sync,
    list_quiz_files_sync,
    parse_source,
)


def create_app(default_source: str | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DEFAULT_SOURCE"] = default_source

    @app.route("/")
    def index():
        return render_template("index.html", default_source=default_source or "")

    @app.route("/api/load", methods=["POST"])
    def api_load():
        """Load quiz from a GitHub source. Returns quiz JSON."""
        data = request.get_json(force=True)
        raw_source = data.get("source", "").strip()
        file_path = data.get("file_path")

        if not raw_source:
            return jsonify({"error": "No source provided"}), 400

        try:
            source = parse_source(raw_source)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

        try:
            if file_path:
                source.path = file_path
                source.ref = source.ref if source.ref != "HEAD" else "HEAD"

            if source.path and source.path.endswith(".quiz.md"):
                content = fetch_file_sync(source)
                quiz = parse_quiz(content)
                return jsonify({"quiz": quiz.to_dict(), "source": source.display_name})
            else:
                files = list_quiz_files_sync(source)
                if not files:
                    return jsonify({"error": "No .quiz.md files found in this repo"}), 404
                if len(files) == 1:
                    source.path = files[0].path
                    content = fetch_file_sync(source)
                    quiz = parse_quiz(content)
                    return jsonify({"quiz": quiz.to_dict(), "source": source.display_name})
                else:
                    return jsonify({
                        "files": [{"path": f.path, "name": f.name} for f in files],
                        "source": source.display_name,
                    })
        except Exception as exc:
            return jsonify({"error": str(exc)}), 500

    return app
