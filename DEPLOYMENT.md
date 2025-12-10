# Deployment Guide - E-Commerce Fraud Detector

This guide covers deploying the E-Commerce Fraud Detector to various platforms:
- [CI/CD Pipeline](#cicd-pipeline) - Automated build and deploy
- [Vercel](#vercel-deployment) - Frontend only (serverless)
- [Railway](#railway-deployment) - Full-stack (managed PostgreSQL)
- [Docker](#docker-deployment) - Local/self-hosted
- [Minikube](#minikube-deployment) - Local Kubernetes cluster

---

## CI/CD Pipeline

### Overview
The project includes automated CI/CD pipelines using GitHub Actions. Pipelines are triggered on push and pull requests.

### Workflows

| Workflow | File | Trigger | Purpose |
|----------|------|---------|---------|
| **CI/CD Pipeline** | `ci-cd.yml` | Push/PR to main, develop | Full pipeline: lint, test, build, deploy |
| **Docker Publish** | `docker-publish.yml` | Push to main, tags | Multi-platform Docker images |
| **K8s Deploy** | `k8s-deploy.yml` | Manual | Kubernetes deployment with environment selection |

### Pipeline Jobs

```mermaid
graph LR
    A[lint-backend] --> D[build-docker]
    B[test-backend] --> D
    C[lint-frontend] --> E[build-frontend]
    E --> D
    D --> F[deploy-staging]
    D --> G[deploy-production]
```

### Required GitHub Secrets

Configure these in **Settings → Secrets and variables → Actions**:

| Secret | Required | Description |
|--------|----------|-------------|
| `GITHUB_TOKEN` | Auto | Automatic, used for GHCR |
| `DOCKERHUB_USERNAME` | Optional | Docker Hub username |
| `DOCKERHUB_TOKEN` | Optional | Docker Hub access token |
| `KUBE_CONFIG` | For K8s | Base64 encoded kubeconfig |

### Triggering Deployments

**Automatic:**
- Push to `develop` → Deploy to staging
- Push to `main` → Deploy to production

**Manual K8s Deploy:**
1. Go to **Actions** → **Kubernetes Deploy**
2. Click **Run workflow**
3. Select environment (staging/production)
4. Enter image tag (default: latest)

---

## Prerequisites

## Vercel Deployment

### Overview
Deploy the React frontend to Vercel's edge network for optimal performance.

> [!NOTE]  
> Vercel deployment is for the **frontend only**. You'll need a separate backend deployment (Railway, Render, or self-hosted).

### Step 1: Install Vercel CLI

```powershell
npm install -g vercel
```

### Step 2: Configure Environment Variables

Create or update `frontend/.env.production`:

```env
VITE_API_URL=https://your-backend-url.railway.app
```

### Step 3: Deploy to Vercel

```powershell
cd frontend
vercel
```

Follow the prompts:
1. Set up and deploy? **Yes**
2. Which scope? Select your account
3. Link to existing project? **No** (first time)
4. Project name? `fraud-detector-frontend`
5. In which directory is your code located? `./`
6. Override settings? **No**

### Step 4: Set Environment Variables in Vercel Dashboard

1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Select your project → Settings → Environment Variables
3. Add:
   - `VITE_API_URL` = Your backend API URL

### Step 5: Production Deployment

```powershell
vercel --prod
```

### Vercel Configuration File

The project includes `frontend/vercel.json` for SPA routing:

```json
{
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

---

## Railway Deployment

### Overview
Deploy the complete stack (frontend + backend + PostgreSQL) to Railway.

### Step 1: Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub

### Step 2: Create New Project

1. Click **New Project** → **Deploy from GitHub repo**
2. Select your `E-Commerce_Fraud_Detector` repository
3. Railway will detect the monorepo structure

### Step 3: Add PostgreSQL Database

1. In your project, click **Add Service** → **Database** → **PostgreSQL**
2. Copy the `DATABASE_URL` from the PostgreSQL service Variables tab

### Step 4: Configure Backend Service

1. Click **Add Service** → **GitHub Repo** → Select your repo
2. Configure settings:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn --config gunicorn.conf.py app:app`

3. Add Environment Variables:
   ```
   DATABASE_URL=${{Postgres.DATABASE_URL}}
   FLASK_ENV=production
   JWT_SECRET=<generate-secure-key>
   ADMIN_SECRET=<generate-secure-key>
   API_TOKEN=<generate-secure-key>
   REVIEW_THR=0.65
   TX_THR=0.50
   ```

### Step 5: Configure Frontend Service

1. Click **Add Service** → **GitHub Repo** → Select your repo
2. Configure settings:
   - **Root Directory**: `frontend`
   - **Build Command**: `npm ci && npm run build`
   - **Start Command**: Leave empty (static files served by Railway)

3. Add Environment Variables:
   ```
   VITE_API_URL=${{Backend.RAILWAY_PUBLIC_DOMAIN}}
   ```

### Step 6: Generate Domain

1. Click on each service → **Settings** → **Networking**
2. Click **Generate Domain**
3. Note your URLs:
   - Backend: `https://fraud-detector-backend-xxxx.railway.app`
   - Frontend: `https://fraud-detector-frontend-xxxx.railway.app`

### Railway Configuration Files

**backend/railway.toml:**
```toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "gunicorn --config gunicorn.conf.py app:app"
healthcheckPath = "/health"
healthcheckTimeout = 180
restartPolicyType = "on_failure"
restartPolicyMaxRetries = 3
```

---

## Docker Deployment

### Overview
Deploy using Docker Compose for local development or self-hosted production.

### Prerequisites

- Docker Desktop installed
- Docker Compose v2+

### Step 1: Development Deployment

```powershell
# From project root
cd infra/compose

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

**Services started:**
| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | React UI |
| Backend API | http://localhost:8000 | Flask API |
| PostgreSQL | localhost:5432 | Database |
| Adminer | http://localhost:8080 | DB admin UI |
| Redis | localhost:6379 | Cache (optional) |

### Step 2: Production Deployment

Use the production compose file:

```powershell
docker-compose -f docker-compose.prod.yml up -d
```

### Step 3: Build Individual Images

**Backend:**
```powershell
cd backend
docker build -t fraud-detector-api:latest .
```

**Frontend:**
```powershell
cd frontend
docker build -t fraud-detector-ui:latest .
```

### Step 4: Push to Registry (Optional)

```powershell
# Tag for Docker Hub
docker tag fraud-detector-api:latest yourusername/fraud-detector-api:latest
docker tag fraud-detector-ui:latest yourusername/fraud-detector-ui:latest

# Push
docker push yourusername/fraud-detector-api:latest
docker push yourusername/fraud-detector-ui:latest
```

### Step 5: Environment Configuration

Create `.env` file in project root (see `.env.production.example`):

```env
# Database
DATABASE_URL=postgresql+psycopg2://postgres:postgres@db:5432/frauddb

# Secrets (CHANGE THESE!)
JWT_SECRET=your-32-char-secret
ADMIN_SECRET=your-32-char-secret
API_TOKEN=your-32-char-secret

# Thresholds
REVIEW_THR=0.65
TX_THR=0.50
```

### Docker Commands Reference

```powershell
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes (DELETES DATA!)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build

# View specific service logs
docker-compose logs -f api

# Execute command in running container
docker-compose exec api python -c "print('Hello from API')"

# Check service status
docker-compose ps
```

---

## Minikube Deployment

### Overview
Deploy to a local Kubernetes cluster using Minikube for testing Kubernetes deployments.

### Prerequisites

- Minikube installed ([Installation Guide](https://minikube.sigs.k8s.io/docs/start/))
- kubectl installed
- Docker Desktop (for building images)

### Step 1: Start Minikube

```powershell
# Start with sufficient resources
minikube start --cpus=4 --memory=8192 --driver=docker

# Enable required addons
minikube addons enable ingress
minikube addons enable metrics-server
```

### Step 2: Build Images in Minikube's Docker

```powershell
# Point shell to Minikube's Docker daemon
minikube docker-env | Invoke-Expression

# Build images
docker build -t fraud-detector-api:latest ./backend
docker build -t fraud-detector-ui:latest ./frontend
```

### Step 3: Apply Kubernetes Manifests

```powershell
# Create namespace
kubectl apply -f infra/k8s/namespace.yaml

# Apply all resources
kubectl apply -f infra/k8s/

# Or use Kustomize
kubectl apply -k infra/k8s/
```

### Step 4: Verify Deployment

```powershell
# Check all resources
kubectl get all -n fraud-detector

# Check pods
kubectl get pods -n fraud-detector

# Check services
kubectl get svc -n fraud-detector

# Check ingress
kubectl get ingress -n fraud-detector
```

### Step 5: Access the Application

```powershell
# Get Minikube IP
minikube ip

# Access frontend (add to hosts file for domain)
# Or use port-forward
kubectl port-forward svc/frontend -n fraud-detector 3000:80

# Access backend
kubectl port-forward svc/backend -n fraud-detector 8000:8000
```

### Step 6: Add to Hosts File (Optional)

For domain-based access:

```powershell
# Get Minikube IP
$minikubeIP = minikube ip

# Add to hosts file (run as Administrator)
Add-Content -Path C:\Windows\System32\drivers\etc\hosts -Value "$minikubeIP fraud-detector.local"
```

Access at: `http://fraud-detector.local`

### Kubernetes Files Structure

```
infra/k8s/
├── namespace.yaml         # Namespace definition
├── configmap.yaml         # Environment configuration
├── secrets.yaml           # Sensitive data (base64 encoded)
├── postgres-deployment.yaml  # PostgreSQL StatefulSet + PVC
├── backend-deployment.yaml   # Backend Deployment + Service
├── frontend-deployment.yaml  # Frontend Deployment + Service
├── ingress.yaml           # Ingress routing rules
└── kustomization.yaml     # Kustomize configuration
```

### Kubernetes Commands Reference

```powershell
# View pod logs
kubectl logs -f deployment/backend -n fraud-detector

# Execute command in pod
kubectl exec -it deployment/backend -n fraud-detector -- /bin/sh

# Scale deployment
kubectl scale deployment backend --replicas=3 -n fraud-detector

# Restart deployment
kubectl rollout restart deployment/backend -n fraud-detector

# Check resource usage
kubectl top pods -n fraud-detector

# Delete all resources
kubectl delete -f infra/k8s/

# Delete namespace (removes everything)
kubectl delete namespace fraud-detector
```

### Minikube Dashboard

```powershell
# Open Kubernetes dashboard
minikube dashboard
```

---

## Platform Comparison

| Feature | Vercel | Railway | Docker | Minikube |
|---------|--------|---------|--------|----------|
| **Best For** | Frontend only | Full-stack MVP | Self-hosted | K8s testing |
| **Setup Time** | 5 min | 15 min | 10 min | 20 min |
| **Cost** | Free tier | Free tier | Self-hosted | Local |
| **PostgreSQL** | ❌ | ✅ Built-in | ✅ Container | ✅ StatefulSet |
| **SSL** | ✅ Auto | ✅ Auto | ❌ Manual | ❌ Manual |
| **Scaling** | ✅ Auto | ✅ Auto | ❌ Manual | ✅ HPA |
| **Custom Domain** | ✅ | ✅ | ✅ | ❌ |

---

## Troubleshooting

### Vercel Issues

**Build fails with "Module not found"**
- Ensure all dependencies are in `dependencies` not `devDependencies`
- Check `vite.config.ts` paths

**API requests fail (CORS)**
- Verify `VITE_API_URL` is set correctly
- Check backend CORS configuration

### Railway Issues

**Backend won't start**
- Check logs: Railway Dashboard → Service → Logs
- Verify `DATABASE_URL` is linked correctly

**Database connection timeout**
- Use Railway's internal URL format for `DATABASE_URL`

### Docker Issues

**Container exits immediately**
- Check logs: `docker-compose logs api`
- Verify `.env` file exists and has valid values

**Port already in use**
- Change port mapping in `docker-compose.yml`

### Minikube Issues

**Pod stuck in ImagePullBackOff**
- Build images in Minikube's Docker: `minikube docker-env`
- Set `imagePullPolicy: Never` in deployments

**Ingress not working**
- Enable addon: `minikube addons enable ingress`
- Wait for ingress controller pod

---

## Security Recommendations

> [!WARNING]  
> Before deploying to production:

1. **Change all secrets** - Generate new values for JWT_SECRET, ADMIN_SECRET, API_TOKEN
2. **Enable HTTPS** - Use platform SSL or set up certificates
3. **Restrict CORS** - Update allowed origins in `app.py`
4. **Set resource limits** - Configure CPU/memory limits in K8s
5. **Enable rate limiting** - Already configured but adjust as needed
6. **Regular backups** - Set up database backup strategy

---

## Quick Reference

### Generate Secure Secrets (PowerShell)

```powershell
# 32-character random string
-join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object {[char]$_})
```

### Environment Variables Summary

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `JWT_SECRET` | ✅ | JWT signing key (32+ chars) |
| `ADMIN_SECRET` | ✅ | Admin authentication secret |
| `API_TOKEN` | ✅ | API authentication token |
| `REVIEW_THR` | ⚡ | Review fraud threshold (0.0-1.0) |
| `TX_THR` | ⚡ | Transaction fraud threshold (0.0-1.0) |
| `FLASK_DEBUG` | ⚡ | Debug mode (true/false) |
| `VITE_API_URL` | ✅ | Backend API URL (frontend) |

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
