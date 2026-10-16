# Saffron & Smoke — Full-Stack Restaurant Website

This version keeps the original Saffron & Smoke premium restaurant design, adds a reservation section in the same visual style, and connects the frontend to a Flask + SQLite backend. It also includes interactive API documentation at `/docs`.

## Features
- Original brand, hero, menu cards, category filters, search, story, experience, visit section, typography, and colour palette retained.
- Menu loaded from the backend API, with a local fallback if the backend is temporarily unavailable.
- Add-to-order demo actions recorded in SQLite.
- Reservation form: name, email, phone, party size, date, time, and optional notes.
- Backend validation and persistent SQLite reservation storage.
- Each reservation request returns a reference such as `SS-A1B2C3`.
- Swagger UI at `/docs` and OpenAPI JSON at `/openapi.json`.

**Reservation note:** This demo saves a reservation *request*. It does not send email or SMS and does not automatically confirm that a table is available. A staff confirmation workflow would be a separate feature.

## Deploy without a permanent `.pem` key pair
You can avoid downloading/managing a permanent key pair by connecting through AWS Console **EC2 Instance Connect** or **Systems Manager Session Manager**. This only works when the selected connection method is supported and configured. For EC2 Instance Connect, ensure the instance has a public IP and the security group/network allows the connection. If AWS Console Connect is unavailable, configure Session Manager or the supported network settings before proceeding.

You do **not** need to recreate an instance solely because it has a key pair. A key pair does not control whether the website can be opened in a browser.

## Deployment architecture
- Backend EC2: Flask API on TCP `8000`, SQLite database, interactive API docs.
- Frontend EC2: Apache HTTP server on TCP `80`.
- Frontend config: `config.js` is updated by the setup script with the backend public IPv4 address.

## 1. Backend EC2
Use Amazon Linux 2023 and make sure the instance has a public IPv4 address.

1. Connect with EC2 Instance Connect or Session Manager.
2. Run:

```bash
sudo dnf install -y git
 git clone https://github.com/akashapya09-dot/saffron-smoke-fullstack.git
cd saffron-smoke-fullstack/backend
chmod +x setup_backend.sh
./setup_backend.sh
```

If you are using a clean folder or have not pushed the updated files to GitHub yet, upload the `frontend/`, `backend/`, and `README.md` from this ZIP to the repository first.

Check the service:

```bash
sudo systemctl status saffron-smoke-backend --no-pager
curl http://localhost:8000/api/health
curl http://localhost:8000/api/menu
```

After configuring the backend security group, open these in a browser (replace with your current backend public IP):

- `http://BACKEND_PUBLIC_IP:8000/docs` — interactive API docs.
- `http://BACKEND_PUBLIC_IP:8000/api/health` — health check.
- `http://BACKEND_PUBLIC_IP:8000/api/menu` — menu JSON.

For browser access to `/docs`, allow inbound TCP `8000` from your current public IP temporarily. For frontend API traffic, allow TCP `8000` from the frontend security group. Avoid leaving port 8000 open to the whole internet unnecessarily.

## 2. Frontend EC2
Use Amazon Linux 2023 and a public IPv4 address. Allow inbound HTTP TCP `80` from `0.0.0.0/0`.

1. Connect with EC2 Instance Connect or Session Manager.
2. Run:

```bash
sudo dnf install -y git
git clone https://github.com/akashapya09-dot/saffron-smoke-fullstack.git
cd saffron-smoke-fullstack/frontend
chmod +x setup_frontend.sh
./setup_frontend.sh BACKEND_PUBLIC_IPV4
```

Replace `BACKEND_PUBLIC_IPV4` with the backend instance's public IPv4 address only (no `http://` and no port).

Then open `http://FRONTEND_PUBLIC_IPV4` in your browser.

## API routes
- `GET /api/health` — backend health check.
- `GET /api/menu` — menu list.
- `POST /api/cart-events` — record an add-to-order demo event.
- `GET /api/cart-events` — inspect recent demo events (learning endpoint).
- `POST /api/reservations` — validate and save a reservation request.
- `GET /api/reservations/availability?date=YYYY-MM-DD` — counts saved requests for a future date; this is not a live availability guarantee.
- `GET /docs` — Swagger UI.
- `GET /openapi.json` — OpenAPI specification.

## GitHub update
If your GitHub repository already contains the previous full-stack version, replace its `frontend/`, `backend/`, and `README.md` with the updated files from this package and commit/push them. Keep the folder names exactly `frontend` and `backend` at the repository root.

## Production caveats
This is a learning/demo deployment. For a real restaurant, use HTTPS, restrict CORS to the frontend origin, add authentication for staff/admin functions, protect customer data, add rate limiting/backups, and implement a staff confirmation process. The demo `/api/cart-events` endpoint is not a production ordering or payment system.
