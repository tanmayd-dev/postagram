# postagram

> **Archive Notice**: This project is an archived school project created for Akshara International School by Sidhart, Tanishq, and Tanmay. It is maintained in a preserved, usable state for portfolio demonstration and historical reference.

Small Flask social app (users, posts, replies, likes).

## Deployment (Getting a live URL)

### Deploy to Render

This repository includes a `render.yaml` blueprint for one-click deployment to [Render](https://render.com):

1. Push your repository to GitHub.
2. In the Render Dashboard, click **New +** > **Blueprint**.
3. Select your repository and click **Apply**.
4. Render will automatically build the Docker image, assign a secure generated `SECRET_KEY`, and provide a public `https://postagram-xxxx.onrender.com` URL.

## Requirements

- Python 3.10+
- `python3 -m venv .venv && source .venv/bin/activate`
- `pip install -r requirements.txt`

MySQL/MariaDB is optional: the app defaults to SQLite and only uses MySQL when
`DATABASE_URL` says so (`pymysql` is the supported driver).

## Configuration

| Variable | Default | Notes |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite:///<instance>/postagram.db` | Any SQLAlchemy URL, e.g. `mysql+pymysql://user:pass@host/postagram`. For MySQL the database must already exist; tables are created automatically. |
| `SECRET_KEY` | insecure dev fallback (`dev-only-insecure-secret-key`) | Sessions signed with the fallback can be forged. A warning is logged on startup when it is unset. Always set this in production. |
| `FLASK_DEBUG` | unset (off) | `1`/`true`/`yes`/`on` enables the debugger when running `main.py`. Never enable in production. |

`<instance>` is `instance/` next to the `website` package. It is created on
startup and must be writable; when using the default SQLite database it holds
`postagram.db`.

## Run locally (development)

```sh
python main.py                  # http://127.0.0.1:5000/
FLASK_DEBUG=1 python main.py    # with the reloader/debugger
```

## Run in production

```sh
export SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')"
gunicorn --bind 0.0.0.0:8000 "website:create_app()"
```

## Run with Docker

```sh
docker build -t postagram .
docker run -p 8000:8000 -e SECRET_KEY="$(python -c 'import secrets; print(secrets.token_hex(32))')" \
    -v postagram-instance:/app/instance postagram
```

The image runs gunicorn as the unprivileged `appuser` and declares
`/app/instance` as a volume. When using a bind mount for that path, make sure
the host directory is writable by uid `10001`.
