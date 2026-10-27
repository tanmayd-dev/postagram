import os

from website import create_app

app = create_app()


def _debug_enabled():
    return os.environ.get("FLASK_DEBUG", "").strip().lower() in {"1", "true", "yes", "on"}


if __name__ == "__main__":
    # Development server only. Production runs gunicorn "website:create_app()".
    app.run(host="127.0.0.1", port=5000, debug=_debug_enabled())
