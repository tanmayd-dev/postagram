# postagram

Small Flask social app (users, posts, replies, likes).

## Requirements

- python 3
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
