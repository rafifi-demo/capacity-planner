# Zava Capacity Planner

**AI-Powered Logistics Capacity Planning with Microsoft Foundry Agents**

A demo application showcasing Microsoft Foundry Agents V1 (Classic) working together in a sequential workflow for logistics capacity planning.

![Workflow Status](https://img.shields.io/badge/Agents-4%20Sequential-blue)
![Framework](https://img.shields.io/badge/Framework-Foundry%20V1-green)
![Model](https://img.shields.io/badge/Model-GPT--5--mini-purple)
![UI](https://img.shields.io/badge/UI-Dark%20Theme-black)

---

## Overview

Zava is a fictional global logistics company that manages air freight shipments from their main hub in Seattle, WA. This demo showcases how Microsoft Foundry Agents can work together to perform complex capacity planning tasks.

### What You'll Learn

- **Creating Foundry V1 Agents** with different tools (MCP, Code Interpreter, File Search)
- **Sequential Agent Workflows** - orchestrating multiple agents
- **Human-in-the-Loop** - requiring approval before critical actions
- **MCP Integration** - connecting agents to external data via Model Context Protocol
- **OpenTelemetry** - observability and monitoring with Application Insights
- **Azure Infrastructure** - deploying with Terraform

---

## Screenshots

The application features a modern dark theme with glassmorphism effects:

- **Dark Mode UI** - Professional enterprise-grade dark theme
- **Animated Pipeline** - Visual workflow with animated data flow between agents
- **Live Telemetry** - Real-time metrics with animated counters
- **Streaming Output** - Character-by-character text streaming effect
- **Confetti Celebration** - Success animation on workflow completion

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    ZAVA CAPACITY PLANNER                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────┐      ┌──────────┐      ┌──────────────────────┐ │
│   │  React   │ ───▶ │ FastAPI  │ ───▶ │   Foundry Agents     │ │
│   │ Frontend │ ◀─── │ Backend  │ ◀─── │  (GPT-5-mini)        │ │
│   └──────────┘      └──────────┘      └──────────────────────┘ │
│        │                 │                      │              │
│        │ WebSocket       │                      │              │
│        │                 │                      ▼              │
│        │           ┌─────────────────────────────────────┐     │
│        │           │       AGENT WORKFLOW                │     │
│        │           │                                     │     │
│        │           │  ┌─────────┐  ┌────────────────┐   │     │
│        │           │  │Agent 1  │──│ Data Analyst   │   │     │
│        │           │  │  MCP    │  │ Query shipments│   │     │
│        │           │  └────┬────┘  └────────────────┘   │     │
│        │           │       ▼                            │     │
│        │           │  ┌─────────┐  ┌────────────────┐   │     │
│        │           │  │Agent 2  │──│ Capacity Calc  │   │     │
│        │           │  │ Code    │  │ Python calcs   │   │     │
│        │           │  └────┬────┘  └────────────────┘   │     │
│        │           │       ▼                            │     │
│        │           │  ┌─────────┐  ┌────────────────┐   │     │
│        │           │  │Agent 3  │──│ Doc Researcher │   │     │
│        │           │  │ Files   │  │ Search policies│   │     │
│        │           │  └────┬────┘  └────────────────┘   │     │
│        │           │       ▼                            │     │
│        │           │  ┌─────────┐  ┌────────────────┐   │     │
│        │           │  │Agent 4  │──│ Planner        │   │     │
│        │           │  │Synthesis│  │ Create plan    │   │     │
│        │           │  └────┬────┘  └────────────────┘   │     │
│        │           │       ▼                            │     │
│        │           │  ┌─────────────────────────────┐   │     │
│        │           │  │   HUMAN APPROVAL REQUIRED   │   │     │
│        │           │  └─────────────────────────────┘   │     │
│        │           └─────────────────────────────────────┘     │
│        │                                                        │
│  ┌─────┴────────────────────────────────────────────────────┐  │
│  │                  AZURE INFRASTRUCTURE                    │  │
│  │  ┌────────┐  ┌────────┐  ┌──────────┐  ┌─────────────┐  │  │
│  │  │Container│  │  APIM  │  │PostgreSQL│  │ App Insights│  │  │
│  │  │  Apps  │  │Gateway │  │ Flexible │  │ (Telemetry) │  │  │
│  │  └────────┘  └────────┘  └──────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Quick Start - Local Development (Recommended)

The fastest way to see the demo in action.

**No Docker required. No Azure credentials required.**

Just run locally on `localhost` with Node.js and Python.

### Prerequisites

- **Node.js** >= 18
- **Python** >= 3.11

### Step 1: Start the Backend

```bash
# Navigate to backend directory
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start the server (Demo Mode enabled by default)
uvicorn app.main:app --reload --port 8000
```

The backend will start at http://localhost:8000

### Step 2: Start the Frontend

Open a **new terminal** and run:

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

### Step 3: Open the Application

Open your browser and navigate to:

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:3000 |
| **Backend API** | http://localhost:8000 |
| **API Docs** | http://localhost:8000/docs |

Click "Start Capacity Planning" to see the demo in action!

### What You'll See in Demo Mode

- **Business value intro** with data-driven metrics ($2.3M savings, etc.)
- **4 AI Agents** executing sequentially with simulated outputs
- **Real-time updates** via WebSocket streaming
- **Animated pipeline** showing data flow between agents
- **Live telemetry** with token counts, costs, and timing
- **Human approval flow** at the end of the workflow
- **Confetti celebration** on successful completion
- **Results dashboard** with animated flight map from Seattle to 8 destinations
- **Minimize/expand toggle** for the results dashboard

---

## The Agent Workflow

### 1. Data Analyst Agent (MCP)
Queries the PostgreSQL database via Model Context Protocol:
- Shipment volumes and destinations
- Aircraft fleet availability
- Historical trends
- Route information
- Crew availability

**File:** `backend/app/agents/data_analyst.py`

### 2. Capacity Calculator Agent (Code Interpreter)
Uses Python to perform calculations:
- Aircraft assignments
- Fuel requirements
- Crew scheduling
- Cost estimates

**File:** `backend/app/agents/capacity_calc.py`

### 3. Document Researcher Agent (File Search)
Searches policy documents:
- Aircraft specifications
- FAA regulations
- Crew policies
- Historical reports

**File:** `backend/app/agents/doc_researcher.py`

### 4. Planner Agent (Synthesis)
Creates the final capacity plan:
- Executive summary
- Detailed recommendations
- Risk mitigation
- Actions requiring approval

**File:** `backend/app/agents/planner.py`

### 5. Human Approval
Before executing the plan, a human must approve:
- Aircraft bookings
- Crew assignments
- Fuel orders
- Partner notifications

---

## UI Features

The application features an enterprise-grade dark theme UI:

### Visual Design
- **Dark Theme** - Deep dark backgrounds (#0a0a0f to #161625)
- **Glassmorphism** - Frosted glass card effects with blur
- **Gradient Accents** - Blue, purple, cyan color palette
- **Glow Effects** - Status-based glowing shadows

### Animations
- **Pipeline Visualization** - Animated connectors between agents
- **Data Flow** - Moving gradient showing active data transfer
- **Streaming Text** - Character-by-character output display
- **Animated Counters** - Smooth number transitions in telemetry
- **Confetti Celebration** - 100-particle celebration on completion
- **Floating Particles** - Ambient background animation
- **Flight Map Animation** - Aircraft flying from Seattle to 8 global destinations

### Components
- **Header** - Logo with gradient, status indicator, telemetry toggle
- **StartForm** - Business value intro + hero section with agent preview pipeline
- **WorkflowViewer** - Visual pipeline + detailed agent cards
- **AgentCard** - Expandable cards with streaming output
- **TelemetryPanel** - Real-time KPIs with charts
- **ApprovalPanel** - Human-in-the-loop decision interface
- **ResultsDashboard** - Post-approval visualization with flight map and business metrics

### Business Value Storytelling

The StartForm includes a data-driven business challenge section:

| Metric | Value | Purpose |
|--------|-------|---------|
| Route Optimization Savings | $2.3M | Shows revenue impact |
| Crew Efficiency Gains | 12% | Operational improvement |
| Planning Time | Minutes vs Days | Time savings |
| Reduced Overtime Costs | 22% | Cost reduction |

### Results Dashboard Features

After workflow approval, the ResultsDashboard displays:

**Animated Flight Map:**
- Seattle hub (SEA) with pulsing marker
- 8 destination routes (NRT, HKG, LHR, FRA, JFK, ORD, LAX, SIN)
- Aircraft animations with staggered departures
- Flight paths with gradient styling

**Operations Summary:**
- Aircraft Assigned: 6
- Crew Scheduled: 18
- Shipments Routed: 487
- Fuel Optimized: 12.5K gal

**Business Impact:**
- Estimated Savings: $127,450
- Planning Time: 4 min vs 3 days
- Efficiency Gain: +18%

**Minimize/Expand Toggle:**
- Click minimize button to collapse to small pill
- Click pill to expand back to full view
- Background remains interactive when minimized

### Presentation-Friendly Layout

The StartForm uses generous "slide-like" spacing between sections for storytelling:

| Slide | Content | Scroll to reveal |
|-------|---------|------------------|
| 1 | Business Challenge | Problem statement with metrics |
| 2 | AI-Powered Capacity Planning | Solution headline |
| 3 | Agent Pipeline Preview | Visual workflow |
| 4 | Configure Workflow | Call to action form |

This layout allows presenters to scroll through each section as a distinct slide when demoing to leadership.

---

## Deployment Options

You can run this application using any of these options:

| Option | Docker Required | Azure Required | Best For |
|--------|-----------------|----------------|----------|
| **Local Development** | No | No | Quick demos, development |
| **Azure with ACR** | No | Yes | Production, cloud deployment |
| **Local Docker** | Yes | Yes | Testing containers locally |

**Recommended for demos:** Use **Local Development** (described in Quick Start above) - just `npm` and `python`, no Docker needed!

---

## Deploy to Azure with ACR (Production)

### Prerequisites

- Azure subscription with Owner/Contributor access
- Azure CLI installed and logged in (`az login`)
- Terraform >= 1.5.0
- PostgreSQL client (`psql`) - install via `brew install libpq` on macOS

### Step 1: Configure Terraform Variables

```bash
cd infrastructure

# Copy the example file
cp terraform.tfvars.example terraform.tfvars

# Edit with your values
```

Edit `terraform.tfvars`:
```hcl
subscription_id         = "your-subscription-id"
postgres_admin_password = "YourSecurePassword123!"
apim_publisher_email    = "your-email@example.com"
```

### Step 2: Deploy Infrastructure

```bash
# Initialize Terraform
terraform init

# Preview changes
terraform plan

# Deploy (takes ~15-20 minutes)
terraform apply
```

### Step 3: Build and Push Containers to ACR

```bash
# Get the ACR name
ACR_NAME=$(terraform output -raw acr_login_server | cut -d'.' -f1)
BACKEND_URL=$(terraform output -raw backend_url)

# Build and push backend
az acr build --registry $ACR_NAME --image zava-backend:latest ../backend

# Build and push frontend (with backend URL baked in)
az acr build --registry $ACR_NAME --image zava-frontend:latest \
  --build-arg VITE_API_URL=$BACKEND_URL ../frontend
```

### Step 4: Add Firewall Rule for Database Access

```bash
# Get your public IP
MY_IP=$(curl -s ipv4.icanhazip.com)

# Add firewall rule to allow your IP
az postgres flexible-server firewall-rule create \
  --resource-group $(terraform output -raw resource_group_name) \
  --name $(terraform output -raw postgres_host | cut -d'.' -f1) \
  --rule-name AllowMyIP \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP
```

### Step 5: Seed the Database

```bash
# Get PostgreSQL host
export POSTGRES_HOST=$(terraform output -raw postgres_host)

# Run seed script (enter your password when prompted)
psql "postgresql://zava_admin@$POSTGRES_HOST:5432/zava_logistics?sslmode=require" < ../data/seed_database.sql
```

You should see output showing tables created and ~487 shipments inserted.

### Step 6: Restart Container Apps (to pick up new images)

```bash
# Restart frontend
az containerapp revision restart --name zava-frontend \
  --resource-group $(terraform output -raw resource_group_name) \
  --revision $(az containerapp revision list --name zava-frontend \
    --resource-group $(terraform output -raw resource_group_name) \
    --query "[0].name" -o tsv)

# Restart backend
az containerapp revision restart --name zava-backend \
  --resource-group $(terraform output -raw resource_group_name) \
  --revision $(az containerapp revision list --name zava-backend \
    --resource-group $(terraform output -raw resource_group_name) \
    --query "[0].name" -o tsv)
```

### Step 7: Access the Application

```bash
# Get the frontend URL
terraform output frontend_url
```

Open the URL in your browser!

---

## Local Docker Deployment (Alternative)

### Step 1: Deploy Infrastructure

Follow Steps 1-2 from "Deploy to Azure with ACR" section above.

### Step 2: Build Images Locally

```bash
# Get backend URL from Terraform
cd infrastructure
BACKEND_URL=$(terraform output -raw backend_url)
POSTGRES_HOST=$(terraform output -raw postgres_host)

# Build backend
cd ../backend
docker build -t zava-backend:latest .

# Build frontend with backend URL
cd ../frontend
docker build --build-arg VITE_API_URL=$BACKEND_URL -t zava-frontend:latest .
```

### Step 3: Push to ACR

```bash
# Login to ACR
ACR_NAME=$(cd ../infrastructure && terraform output -raw acr_login_server | cut -d'.' -f1)
az acr login --name $ACR_NAME

# Tag and push
docker tag zava-backend:latest $ACR_NAME.azurecr.io/zava-backend:latest
docker tag zava-frontend:latest $ACR_NAME.azurecr.io/zava-frontend:latest

docker push $ACR_NAME.azurecr.io/zava-backend:latest
docker push $ACR_NAME.azurecr.io/zava-frontend:latest
```

### Step 4: Seed Database and Access

Follow Steps 4-7 from "Deploy to Azure with ACR" section above.

---

## Connecting to Real Azure Services (Optional)

To use real Azure AI services instead of demo mode:

```bash
# Set environment variables
export DEMO_MODE=false
export AZURE_AI_PROJECT_ENDPOINT=https://<resource>.services.ai.azure.com/api/projects/<project>
export AZURE_AI_MODEL_DEPLOYMENT_NAME=gpt-5-mini
export POSTGRES_HOST=<your-postgres-host>
export POSTGRES_DATABASE=zava_logistics
export POSTGRES_USER=zava_admin
export POSTGRES_PASSWORD=<your-password>

# Run backend
uvicorn app.main:app --reload --port 8000
```

---

## Troubleshooting

### Common Issues

#### "Connection timed out" when seeding database
Your IP is not allowed by the PostgreSQL firewall. Add a firewall rule:
```bash
MY_IP=$(curl -s ipv4.icanhazip.com)
az postgres flexible-server firewall-rule create \
  --resource-group <resource-group> \
  --name <postgres-server-name> \
  --rule-name AllowMyIP \
  --start-ip-address $MY_IP \
  --end-ip-address $MY_IP
```

#### "host not found in upstream 'backend'" in nginx
This happens when the frontend container can't resolve the backend hostname. The frontend should call the backend directly via `VITE_API_URL`. Rebuild the frontend with:
```bash
az acr build --registry $ACR_NAME --image zava-frontend:latest \
  --build-arg VITE_API_URL=$BACKEND_URL ../frontend
```

#### "uuid-ossp extension not allowed" when seeding
The seed script uses `gen_random_uuid()` which is built into PostgreSQL 13+. If you see this error, ensure you have the latest `seed_database.sql`.

#### 504 Gateway Timeout on frontend
The container may need to restart to pick up the new image:
```bash
az containerapp revision restart --name zava-frontend \
  --resource-group <resource-group> \
  --revision <revision-name>
```

#### TypeScript errors during frontend build
Ensure the `src/vite-env.d.ts` file exists with Vite type definitions.

#### Frontend shows white/blank page
Check browser console for errors. The dark theme requires Tailwind CSS to be properly configured. Run `npm install` to ensure all dependencies are installed.

### View Container Logs

```bash
# Frontend logs
az containerapp logs show --name zava-frontend --resource-group <resource-group> --tail 50

# Backend logs
az containerapp logs show --name zava-backend --resource-group <resource-group> --tail 50
```

### Check Container Status

```bash
# Check if containers are running
az containerapp show --name zava-frontend --resource-group <resource-group> --query "properties.runningStatus"
az containerapp show --name zava-backend --resource-group <resource-group> --query "properties.provisioningState"
```

---

## Agent Data Sources

### Database Schema (Data Analyst Agent)

The Data Analyst Agent queries the PostgreSQL database via MCP tools:

| Table | Description | Records |
|-------|-------------|---------|
| `shipments` | Incoming shipment records | ~487 |
| `aircraft` | Fleet information | 10 |
| `routes` | Route definitions from Seattle | 16 |
| `crew_members` | Crew availability | 15 |
| `historical_volumes` | Historical trend data | 12 |

### Policy Documents (Document Researcher Agent)

| Document | Contents |
|----------|----------|
| `aircraft_specs.md` | Fleet technical specifications |
| `faa_regulations.md` | FAA cargo regulations (simplified) |
| `crew_policies.md` | Crew scheduling policies |
| `historical_reports.md` | Q3-Q4 2025 capacity reports |

---

## Authentication: Managed Identity

The application supports **Azure AD Managed Identity** for passwordless PostgreSQL authentication.

### How It Works

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Container App  │────▶│    Azure AD     │────▶│   PostgreSQL    │
│  (System MI)    │     │  Token Service  │     │  (Entra Auth)   │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Post-Deployment Setup (Optional)

After deploying, enable Managed Identity for passwordless auth:

```bash
# Connect as Azure AD admin
psql "host=$POSTGRES_HOST dbname=zava_logistics user=<your-azure-email> sslmode=require"

# Run the setup script
\i data/create_managed_identity_user.sql
```

---

## Cost Estimates

| Resource | Estimated Monthly Cost |
|----------|----------------------|
| PostgreSQL Flexible (B1ms) | ~$13 |
| Container Apps | Pay per use (scale to zero) |
| APIM Consumption | ~$4 per million calls |
| Application Insights | ~$2.30/GB |
| Storage | < $1 |
| **GPT-5-mini usage** | ~$0.05 per workflow run |

**Total for demo purposes:** < $50/month with minimal usage

---

## Clean Up

To delete all Azure resources:

```bash
cd infrastructure
terraform destroy
```

---

## Technology Stack

### Backend
- **Python 3.11+** with FastAPI
- **Microsoft Agent Framework** - Foundry V1 agents
- **OpenTelemetry** - Observability
- **asyncpg** - PostgreSQL driver

### Frontend
- **React 18+** with TypeScript
- **Vite** - Build tool
- **TailwindCSS** - Dark theme with glassmorphism
- **Recharts** - Telemetry charts
- **Lucide React** - Icons

### Infrastructure
- **Terraform** - Infrastructure as Code
- **Azure Container Apps** - Hosting
- **Azure AI Foundry** - GPT-5-mini model
- **Azure PostgreSQL Flexible** - Database

---

## Resources

### Microsoft Agent Framework
- [Agent Framework Overview](https://learn.microsoft.com/en-us/agent-framework/)
- [Azure AI Foundry Agents](https://learn.microsoft.com/en-us/agent-framework/user-guide/agents/agent-types/azure-ai-foundry-agent)

### Azure AI Foundry
- [Foundry V1 Documentation](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview?view=foundry-classic)
- [Code Interpreter Tool](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools/code-interpreter)
- [File Search Tool](https://learn.microsoft.com/en-us/azure/ai-foundry/agents/how-to/tools-classic/file-search-upload-files)

### MCP (Model Context Protocol)
- [MCP Documentation](https://modelcontextprotocol.io/)

---

## License

This demo is provided for educational purposes. See LICENSE for details.

---

**Built with Microsoft Foundry Agents | GPT-5-mini | Dark Theme UI | v1.3.0**
