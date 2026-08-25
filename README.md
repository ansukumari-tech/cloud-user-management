# ☁️ Cloud User Management — Microservices Architecture

A user management system split into two independently deployable services
(Flask + Django) that communicate over HTTP, behind an nginx gateway.

## Architecture

```
                    ┌─────────────┐
   client  ──────▶  │   gateway   │  (nginx, port 80 — the only public entry point)
                    └──────┬──────┘
                 ┌─────────┴─────────┐
                 ▼                   ▼
        ┌────────────────┐   ┌──────────────────┐
        │  auth-service   │   │  admin-service    │
        │  (Flask)        │◀──│  (Django + DRF)   │
        │  owns Postgres  │   │  stateless        │
        └────────┬────────┘   └───────────────────┘
                  ▼
             ┌─────────┐
             │ Postgres │
             └─────────┘
```

- **auth-service** (Flask + SQLAlchemy) owns the user database. It's the
  only thing that ever touches Postgres. Public routes: `POST /register`,
  `POST /login` (issues a JWT with a `role` claim). It also exposes
  `/internal/users*` routes, callable only by something holding the shared
  `INTERNAL_SERVICE_KEY` header — i.e. only admin-service.

- **admin-service** (Django + DRF) holds **no user data at all**. It
  verifies incoming JWTs itself (same secret, no network call needed for
  that part), checks the `role` claim, and — only for admin-only actions —
  calls auth-service's internal API over real HTTP to list/update/delete
  users. See `admin-service/users/authentication.py` and
  `admin-service/users/services.py`.

- **gateway** (nginx) is the single public entry point. It routes
  `/register` and `/login` to auth-service, `/users*` to admin-service, and
  does **not** expose either service's port directly or the `/internal/*`
  routes — those only exist inside the docker network.

This means the two services can be developed, tested, deployed, and scaled
independently — genuine service separation, not just two folders sharing a
repo.

## Running locally with Docker (recommended)

```bash
cp .env.example .env    # then set real values for JWT_SECRET_KEY etc.
docker compose up --build
```

- Gateway: http://localhost/register, http://localhost/login, http://localhost/users
- Postgres data persists in a named volume between runs

## Running without Docker (for local development)

Each service needs its own `.env` with **matching** `JWT_SECRET_KEY` and
`INTERNAL_SERVICE_KEY`:

```bash
# Terminal 1
cd auth-service
python -m venv venv && source venv/bin/activate   # or venv\Scripts\Activate.ps1 on Windows
pip install -r requirements.txt
cp .env.example .env    # or hand-write one — see below
python app.py            # runs on :5000

# Terminal 2
cd admin-service
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver 8000
```

`admin-service/.env` needs `AUTH_SERVICE_URL=http://127.0.0.1:5000` when
running this way (it's `http://auth-service:5000` in docker-compose,
since docker gives each service a DNS name on its internal network).

## Testing the flow

```bash
# Register + log in via auth-service
curl -X POST http://localhost/register -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"pass123","role":"admin"}'

curl -X POST http://localhost/login -H "Content-Type: application/json" \
  -d '{"username":"admin1","password":"pass123"}'
# -> {"access_token": "..."}

# Use the token against admin-service (which calls auth-service internally)
curl http://localhost/users -H "Authorization: Bearer <token>"
```

## CI/CD
`.github/workflows/microservices-ci-cd.yml` tests both services
independently against a real Postgres service container, then builds and
pushes three Docker images (auth-service, admin-service, gateway) to
GitHub Container Registry on merges to `main`.
