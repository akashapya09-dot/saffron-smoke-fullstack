# Saffron & Smoke — Frontend + Backend EC2 Demo

This package keeps the uploaded Saffron & Smoke HTML/CSS design and adds a small Python API so you can learn how two EC2 instances communicate.

## Architecture
- **Frontend EC2:** Apache serves `index.html`, `style.css`, `script.js`, and `config.js` over HTTP port 80.
- **Backend EC2:** Flask API listens on TCP port 8000.
- **API routes:** `GET /api/health`, `GET /api/menu`, `POST /api/cart-events`, `GET /api/cart-events`.
- **Database:** SQLite stores the demo "Add" button events on the backend instance.
- This is a learning demo only; it does not take payments or submit real restaurant orders.

## 1. Prepare a GitHub repository
Create a new repository for this project and upload the contents of this folder so that `frontend/` and `backend/` are at the repository root. Do not overwrite your teacher's original lab repository.

## 2. Launch two EC2 instances
Use Amazon Linux 2023. You can use your teacher's two-instance pattern:
- backend instance: `app_server`
- frontend instance: `app_client`

Security groups:
- **Backend SG inbound:** TCP 8000 from the frontend security group (recommended); SSH 22 from *My IP*.
- **Frontend SG inbound:** HTTP 80 from Anywhere IPv4; SSH 22 from *My IP*.
- If your lab specifically requires SSH from Anywhere, change it back after the lab; it is less safe.
- Both instances need outbound internet access for package installation and `git clone`.

## 3. Backend EC2
SSH into backend. Replace `YOUR_GITHUB_REPO_URL` with your new repository URL:
```bash
sudo dnf update -y
sudo dnf install git -y
git clone YOUR_GITHUB_REPO_URL
cd YOUR_REPO_NAME/backend
chmod +x setup_backend.sh
./setup_backend.sh
```
Test locally:
```bash
curl http://localhost:8000/api/health
curl http://localhost:8000/api/menu
```
Then from your laptop, test:
`http://BACKEND_PUBLIC_IPV4:8000/api/health`

## 4. Frontend EC2
SSH into frontend:
```bash
sudo dnf update -y
sudo dnf install git -y
git clone YOUR_GITHUB_REPO_URL
cd YOUR_REPO_NAME/frontend
chmod +x setup_frontend.sh
./setup_frontend.sh BACKEND_PUBLIC_IPV4
```
Replace `BACKEND_PUBLIC_IPV4` with the backend instance's current public IPv4 address (no angle brackets).

Open `http://FRONTEND_PUBLIC_IPV4` in your browser.

## 5. Verify backend receives interactions
1. Open the frontend and click **+ Add** on a dish.
2. On backend, run:
```bash
curl http://localhost:8000/api/cart-events
```
The returned JSON should include the dish click saved in SQLite.

## Notes
- If you stop/start an EC2 instance, its public IPv4 can change unless you use an Elastic IP. Update `config.js`/rerun frontend setup if the backend IP changes.
- If the browser reports a CORS or network error, verify the backend is running, port 8000 inbound allows traffic from the frontend SG, and the frontend has the correct backend public IPv4.
- For a production deployment, use HTTPS, restrict CORS to the frontend origin, add validation/rate limiting, and do not expose administrative endpoints publicly.
