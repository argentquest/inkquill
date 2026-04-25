# Care Circle Production Deployment On A Single Ubuntu Server

This document is for **Care Circle only**, not the broader Ink & Quill platform.

It assumes:

- we are deploying the current Care Circle backend, React frontend, scheduler, email delivery, daily cache, and PDF generation
- an AI provider is already provisioned and will continue to provide the AI models
- SMTP remains external for now
- cost control matters more than high availability

Hosting notes:

- the recommended first production shape is **one Ubuntu server** running Docker Compose
- that server can live in **Azure**, **IONOS**, **DigitalOcean**, **Hetzner**, **AWS**, **Linode/Akamai**, or another VPS provider
- keep the app server and database in the same region or datacenter when possible
- if your AI provider is hosted elsewhere, choose the closest practical server region to reduce latency

Pricing notes:

- exact monthly cost depends on provider, region, disk size, bandwidth, backup plan, and whether PostgreSQL is self-managed or managed
- Azure examples later in this document are only one possible provider-specific mapping
- validate final numbers in your provider's pricing calculator before purchase

## Recommended Low-Cost Architecture

### Option A: Recommended now

Use **one Ubuntu server with Docker Compose** for the first production rollout.

This is the best fit for the way Care Circle already runs in this repo:

- the app already has a dedicated single-host deployment bundle in [deployments/docker-host/README.md](C:/Code/inkandquill/inkquill/deployments/docker-host/README.md)
- the stack is already split into `gateway`, `frontend`, `backend`, `scheduler`, and `db` in [deployments/docker-host/docker-compose.base.yml](C:/Code/inkandquill/inkquill/deployments/docker-host/docker-compose.base.yml)
- the repo already includes a host deployment script in [scripts/deploy_care_circle_docker_host.ps1](C:/Code/inkandquill/inkquill/scripts/deploy_care_circle_docker_host.ps1)
- PDF generation already works in the scheduler container via the existing scheduler image
- the current Care Circle flow is naturally file-centric because it writes cache, newsletter HTML, and newsletter PDFs to disk

Recommended starting shape:

1. **Ubuntu server or VPS**
2. **Docker Engine + Docker Compose**
3. **Nginx gateway container**
4. **Frontend container**
5. **Backend container**
6. **Scheduler container**
7. **PostgreSQL**, either:
   - inside Docker on the server for the absolute cheapest setup
   - as a managed PostgreSQL service for a safer hybrid setup
8. **Persistent host storage** for `cache/`, logs, and optionally Postgres data
9. **DNS + TLS**
10. **Optional secret store** for secret management

Why this is recommended now:

- it matches the deployment model you already have
- it avoids a platform rewrite while Care Circle is still stabilizing
- it keeps operating cost low
- it is the shortest path from the current local Docker server to production

### Option B: Managed container hosting later

Use a **managed container platform** later if you want more managed infrastructure without fully redesigning the application.

Managed container hosting is a reasonable next step because Care Circle currently has:

- a Python backend
- a separate frontend container
- a scheduler process
- PDF generation that depends on **Node + Playwright**
- a local `cache/` artifact model that needs persistent shared storage

Recommended components:

1. **Managed container environment**
2. **Frontend container**
3. **Backend API container**
4. **Scheduler container or job**
5. **Managed PostgreSQL**
6. **Persistent shared file storage**
7. **Container registry**
8. **Secret store**
9. **Centralized logging**

Examples:

- Azure Container Apps
- AWS App Runner / ECS
- Google Cloud Run for parts of the stack
- DigitalOcean Apps Platform

### Option C: Cheaper managed runtime after a small refactor

Replace the always-on scheduler app with **scheduled jobs** on your chosen platform:

- one scheduled job for session generation
- one scheduled job for email delivery
- one scheduled job for PDF generation

This is cheaper because jobs do not sit idle all month.

### Lowest-cost generic profile

Run the full Care Circle stack on **one Ubuntu server** with Docker Compose:

- frontend container
- backend container
- scheduler container
- nginx gateway container
- postgres container
- local disk or attached managed disk for persistent `cache/`, logs, and database volume

This is the **lowest infrastructure cost** option if you want to get to production quickly and accept more operational responsibility.

Good fit when:

- you want the smallest hosting bill
- user count is still low
- you are comfortable managing a server
- you are fine with a single point of failure for now

Tradeoffs:

- less managed than a hosted container platform
- you manage OS patching, Docker updates, backups, monitoring, and restarts
- server failure affects the full Care Circle stack
- scaling is manual

## Why The Ubuntu Server Path Is The Right Starting Point

For Care Circle specifically, the dedicated Ubuntu server path is the strongest first production choice because:

- the repo already contains a production-oriented single-host deployment bundle in [deployments/docker-host](C:/Code/inkandquill/inkquill/deployments/docker-host)
- the deployment script already prepares persistent directories for `cache`, logs, and Postgres data in [scripts/deploy_care_circle_docker_host.ps1](C:/Code/inkandquill/inkquill/scripts/deploy_care_circle_docker_host.ps1)
- backend and scheduler already share the same mounted `/app/cache` path in [deployments/docker-host/docker-compose.base.yml](C:/Code/inkandquill/inkquill/deployments/docker-host/docker-compose.base.yml)
- the scheduler image already carries the Playwright runtime needed for PDF generation
- the current operational model is easier to reason about on one host while delivery volume is still modest

The practical takeaway is:

- **a single Ubuntu server is the recommended production entry point**
- **managed container hosting is the likely later upgrade path**

## Why A Single Server Is Better Than App-Service-Style Hosting First

For Care Circle specifically, a Docker host is the better first fit because:

- the repo already has separate `backend`, `frontend`, and `scheduler` containers in [docker-compose.yml](C:/Code/inkandquill/inkquill/docker-compose.yml)
- PDF generation uses the Playwright Python library directly in [newsletter_pdf_service.py](C:/Code/inkandquill/inkquill/app/services/care_circle/newsletter_pdf_service.py), which launches a headless Chromium browser — the scheduler image must include Chromium and its system library dependencies
- newsletter content and images are written to the local cache in [provider_cache.py](C:/Code/inkandquill/inkquill/app/services/care_circle/provider_cache.py)
- backend and scheduler already benefit from shared persistent storage on a single host

That means if the goal is strictly **lowest monthly spend** and the fewest moving pieces, a single Docker server is the better fit than app-service-style hosting.

## Single-Server Docker Option

This section describes the all-in-one server option.

### Core idea

Option A is basically:

- take the Docker-based runtime model you already have locally
- move it to **one persistent Ubuntu server**
- keep the same container boundaries
- keep the same Docker Compose operational model
- add only the minimum production hardening around it

This is important because you already have a Docker server running locally. That means Option A is not a new platform decision so much as a **promotion strategy**:

- local Docker server proves the stack works
- the hosted Ubuntu server becomes the production version of that same stack
- your deployment process becomes a controlled copy of what you already know

### Mental model

Think of Option A as a small private appliance dedicated to Care Circle:

- one server
- one repo checkout
- one compose project
- one reverse proxy
- one database
- one scheduler
- one place where newsletter files are generated and stored

It is the most straightforward way to get to production without re-architecting the application.

### Recommended shape

Use:

- **1 Ubuntu server**
- **Docker Engine + Docker Compose**
- the existing host deployment bundle in [deployments/docker-host](C:/Code/inkandquill/inkquill/deployments/docker-host)
- the deployment helper in [scripts/deploy_care_circle_docker_host.ps1](C:/Code/inkandquill/inkquill/scripts/deploy_care_circle_docker_host.ps1)
- enough attached disk space for persistence

### How this maps to your current local Docker server

If your local Docker server already runs this style of stack, the production move can follow the same pattern:

1. provision one Ubuntu server
2. install Docker and Docker Compose
3. clone the repo onto the server
4. create a production `.env`
5. copy the `deployments/docker-host/env/*.example` files into real host/runtime env files
6. mount persistent directories for database, cache, and logs
7. run the existing compose project on the server

That means your local Docker server can act as:

- the model for production
- the dress rehearsal environment
- the place where you validate compose changes before shipping them to the hosted server

### What stays the same

With Option A, these things can stay very close to your current setup:

- container layout
- scheduler process model
- nginx gateway pattern
- file-based newsletter cache
- local PDF generation model
- SMTP integration
- Alembic migration flow

### What changes for production

These are the main production additions:

- public DNS
- TLS certificate management
- restricted firewall rules
- host-level backups
- service restart policy after reboot
- secret handling
- monitoring and alerting

### Suggested starting server size

Start with one of these:

1. around `2 vCPU / 4 GB RAM` if traffic is light and PDF generation volume is low
2. around `2 vCPU / 8 GB RAM` if you want more memory headroom
3. around `4 vCPU / 16 GB RAM` only if newsletter generation and PDF rendering become noticeably slow

For the first rollout, `2 vCPU / 4-8 GB RAM` is the right place to start.

### What runs on the server

Using the current compose model:

- `gateway`
- `frontend`
- `backend`
- `scheduler`
- `db`

This is the closest match to your current working local/prod compose setup, so it requires the fewest code changes.

### Recommended Option A topology

Inside the server, the topology should look like this:

1. `nginx` receives public traffic on `80/443`
2. `frontend` serves the React app on the internal Docker network
3. `backend` serves the API on the internal Docker network
4. `scheduler` runs newsletter generation and delivery jobs
5. `db` stores Care Circle state if you choose self-managed Postgres
6. host-mounted storage keeps:
   - database files
   - `cache/`
   - `logs/`

The most important design principle is:

- **only nginx is internet-facing**

Everything else should stay private on the Docker bridge network.

### Two sub-variants of Option A

#### Variant C1: Full single-box

Everything stays on one server:

- nginx
- frontend
- backend
- scheduler
- postgres
- cache and PDFs on disk

Best for:

- cheapest footprint
- fastest first deployment

Biggest downside:

- database and app share the same failure domain

#### Variant C2: Single-box app, managed database

Run on the server:

- nginx
- frontend
- backend
- scheduler

Use Azure Database for PostgreSQL Flexible Server for the database.

Best for:

- still simple
- less risky than self-managed Postgres
- easier backup story

This is the version I would usually recommend if you want Option A but want to avoid database pain.

### Persistence

Persist these paths:

- PostgreSQL data volume
- `cache/`
- `logs/`

Recommended mapping:

- mount a host path like `/srv/care-circle/cache` to the app cache location
- mount a host path like `/srv/care-circle/logs` to logs
- use a named Docker volume or host path for postgres data

Suggested host layout:

```text
/srv/care-circle/
  compose/
  env/
  cache/
  logs/
  postgres/
  backups/
```

Recommended purpose:

- `compose/`: checked-out repo or deployment bundle
- `env/`: production env files not committed to git
- `cache/`: generated provider output, local images, newsletter HTML, newsletter PDF
- `logs/`: application and scheduler logs
- `postgres/`: self-managed DB files if using Variant C1
- `backups/`: compressed database dumps and optional cache snapshots

### Why Option A fits Care Circle particularly well

Care Circle benefits from Option A because several features are naturally file-centric:

- provider cache
- cached images
- generated HTML newsletters
- generated PDFs
- scheduler-driven daily processing

On a single Docker host, all of that is naturally local, simple, and fast.

There is no extra network hop between:

- backend and scheduler
- scheduler and generated files
- email assembly and cached local images

### Minimal infrastructure for this option

1. **One Ubuntu server**
2. **Public IP**
3. **Attached disk or sufficient local SSD/NVMe**
4. **Firewall rules / security group**
5. **DNS record** for your domain
6. **Optional secret store** or securely managed env files

Optional:

- provider snapshots or server backup service
- external monitoring and centralized logs

### Production responsibilities in Option A

Option A is cheap because the infrastructure provider is doing less for you. That means you must own:

- OS patching
- Docker Engine updates
- compose rollout process
- certificate renewal if not automated
- disk space monitoring
- database backups
- restore testing
- server restart behavior
- intrusion surface reduction

### Recommended deployment workflow

Since you already have a local Docker server, the cleanest workflow is:

1. validate changes locally on the Docker server
2. tag a release or deploy from a known git commit
3. pull that exact commit on the server
4. update the host/runtime env files under `deployments/docker-host/env/` on the server if needed
5. run the deployment script against `prod`
6. run Alembic migrations if they were not included in the deployment flow
7. verify newsletter generation for one patient
8. verify scheduler and email flow

That gives you a very understandable release motion with low tooling overhead.

### Suggested release mechanics

For Option A, one of these is enough:

1. `git pull` on the server, then `docker compose up -d --build`
2. ship a tarball or zip deployment bundle to the server
3. build images on the server directly from the checked-out repo

If you want the simplest path, use:

- git checkout on the server
- local Docker build on the server
- the existing host deploy command:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\deploy_care_circle_docker_host.ps1 -Environment prod -Action up -Build -Detached -AutoMigrate
```

That removes the need for a separate container registry entirely.

### Backup strategy for Option A

If using Variant C1 with Postgres in Docker:

- take scheduled `pg_dump` backups daily
- write them to `/srv/care-circle/backups`
- copy backups off the server to another location
- keep at least 7 to 14 days

If using Variant C2 with managed Postgres:

- rely on managed PostgreSQL backups
- still back up:
  - `.env`
  - deployment config
  - nginx config
  - optional cache snapshots

### Recovery expectations

Recovery is different depending on the sub-variant.

Variant C1:

- rebuild server
- restore repo + env + Docker
- restore Postgres from backup
- restart compose

Variant C2:

- rebuild server
- reconnect app containers to managed Postgres
- restart compose

Variant C2 is much easier to recover from.

### Security posture for Option A

At minimum:

- disable password SSH, use keys only
- restrict SSH to your IP
- expose only `80` and `443`
- keep Postgres closed to the public internet
- keep backend and scheduler off public ports
- put secrets in a host env file or a provider-backed secret store
- use TLS for the public site

### Where Option A breaks down

Option A stops being a good fit when:

- many patients depend on time-sensitive newsletter delivery
- you need strong uptime guarantees
- you need easy horizontal scaling
- PDF generation and scheduler load start competing with web traffic
- you want rolling deployments without downtime

At that point, the natural upgrade path is:

- keep the same containers
- move from one server to managed container hosting
- optionally keep the same managed PostgreSQL server

### Cost profile for Option A

This option removes:

- managed container environment
- managed container runtime costs
- container registry if you build directly on the server
- managed PostgreSQL if you keep Postgres in Docker on the server

Typical low-cost monthly pattern:

| Resource | Assumption | Estimated monthly cost |
|---|---:|---:|
| Ubuntu VPS/server | `2 vCPU / 4-8 GB` class | roughly **$20 to $80/month** |
| Extra disk or snapshot storage | small extra storage if needed | roughly **$5 to $20/month** |
| Public IP | often included, sometimes extra | low single digits |
| Optional secret store | light use | low single digits or included |

Expected total:

- roughly **$35 to $75/month**

This range depends mostly on the server size and storage plan you choose.

### When this option is cheaper

Option A is often cheaper than a managed container platform + managed PostgreSQL setup when:

- you keep everything on one server
- you do not use a container registry
- you do not use managed Postgres

### When this option is riskier

Option A is operationally riskier because:

- Postgres is now your responsibility
- a single server outage takes down everything
- backups must be explicitly configured
- patching and security hardening are on you

### Recommended use of Option A

Use this option if:

- you want to prove out production with the smallest number of Azure resources
- you need a cheap private pilot deployment
- uptime requirements are modest

Do **not** use this option long term if:

- many families depend on daily delivery
- downtime tolerance is low
- you want managed backup and recovery with less effort

### Best practical version of Option A

The best compromise is:

- **one server for app containers**
- **managed PostgreSQL**

That keeps costs lower than full managed container hosting while avoiding self-managed database risk.

In that hybrid setup you would run:

- frontend
- backend
- scheduler
- nginx

on the server, while keeping Postgres managed.

That usually lands around:

- roughly **$45 to $85/month**

depending on server size.

## Azure Mapping For The Managed Azure Path

### 1. Resource Group

Example:

- `rg-care-circle-prod`

### 2. Azure Container Registry

Use:

- **Basic**

Purpose:

- store the frontend image
- store the backend image
- optionally store a scheduler/worker image

### 3. Azure Container Apps Environment

Purpose:

- hosts the frontend, backend, and scheduler apps
- provides shared networking and logging

Notes:

- use one environment for the whole Care Circle production stack
- connect it to a Log Analytics Workspace

### 4. Frontend Container App

Purpose:

- run the Next.js app from `frontendv1/`

Suggested starting size:

- `0.25 vCPU`
- `0.5 GiB RAM`
- ingress enabled

Scaling:

- lowest cost: `min replicas = 0`
- smoother UX: `min replicas = 1`

If you want the absolute lowest spend, set `min replicas = 0` and accept cold starts.

### 5. Backend API Container App

Purpose:

- run FastAPI
- serve Care Circle APIs
- serve cached images

Suggested starting size:

- `0.5 vCPU`
- `1.0 GiB RAM`
- ingress enabled
- `min replicas = 1`

This one should stay warm in production.

### 6. Scheduler Runtime

Purpose:

- generate sessions
- send newsletters
- build PDFs

Two ways to run it:

- **Now:** separate always-on scheduler Container App running `python -m app.scheduler.main`
- **Later / cheaper:** split it into scheduled Container Apps Jobs

Suggested starting size if always-on:

- `0.25 vCPU`
- `0.5 GiB RAM`
- `min replicas = 1`

### 7. Azure Database For PostgreSQL Flexible Server

Use:

- **Burstable tier**
- start at the smallest production-capable size

Suggested starting point:

- compute: **Burstable B1MS**
- storage: **32 GB**
- HA: **disabled**
- backup retention: **7 days**

This is the cheapest reasonable managed database starting point.

### 8. Azure Storage Account

Use:

- **Standard LRS**

Purpose:

- mount an **Azure Files** share into backend and scheduler
- persist:
  - `cache/`
  - generated `newsletter.html`
  - generated `newsletter.pdf`
  - logs if desired

Suggested shares:

- `care-circle-cache`
- `care-circle-logs`

Recommended mount targets:

- `/app/cache`
- `/app/logs`

### 9. Azure Key Vault

Use:

- **Standard**

Store:

- database connection string
- SMTP credentials
- Azure Foundry key and endpoint
- app secret key
- OAuth secrets if Google login stays enabled

### 10. Log Analytics Workspace

Purpose:

- container logs
- job execution logs
- platform diagnostics

Keep retention small at first to control cost.

## External Services Still Needed

These are not new Azure resources if you already have them:

- **Azure Foundry project / model deployments**
- **SMTP provider**

If you later want to move email fully into Azure, you can evaluate Azure Communication Services Email, but that is not required for the first Care Circle production rollout.

## Azure Example Monthly Cost

These are rough low-cost estimates for **East US 2**, using official Azure list pricing.

### Fixed-ish monthly items

| Resource | Assumption | Estimated monthly cost |
|---|---:|---:|
| Container Registry Basic | `0.1666/day` | about **$5.00** |
| Container Registry storage | `2 GB x $0.10/GB` | about **$0.20** |
| PostgreSQL compute | `0.017/hour x 730 hours` | about **$12.41** |
| PostgreSQL storage | `32 GB x $0.115/GB` | about **$3.68** |
| Azure Files share | `20 GB x $0.06/GB` | about **$1.20** |
| Key Vault operations | light usage | about **$0.30 or less** |

Subtotal for core stateful resources:

- about **$22.79/month**

### Container Apps runtime estimate

Using East US 2 standard idle pricing:

- vCPU idle: `$0.000003 / second`
- memory idle: `$0.000003 / GiB-second`

Estimated monthly idle runtime:

| App | Size | Min replicas | Estimated monthly idle cost |
|---|---|---:|---:|
| Frontend | `0.25 vCPU / 0.5 GiB` | 1 | about **$5.91** |
| Backend | `0.5 vCPU / 1.0 GiB` | 1 | about **$11.83** |
| Scheduler | `0.25 vCPU / 0.5 GiB` | 1 | about **$5.91** |

Always-on app subtotal:

- about **$23.65/month**

### Total estimate: Container Apps always-on

Managed Container Apps baseline = frontend + backend + always-on scheduler + database + storage + ACR + Key Vault

- about **$46 to $52/month**

That range assumes:

- modest Azure Files usage
- light log volume
- low request volume

### Total estimate: Container Apps jobs

If you later switch the scheduler from an always-on app to scheduled Container Apps Jobs:

- remove about **$5.91/month** of idle scheduler cost
- scheduler executions should typically land in the **low single digits per month**

Expected range after that improvement:

- about **$39 to $46/month**

### Total estimate: Single VM on Azure

Single VM, Docker Compose, self-managed Postgres:

- about **$35 to $75/month**

Hybrid single VM plus managed PostgreSQL:

- about **$45 to $85/month**

### Cheapest workable configuration

If you also set the frontend app to `min replicas = 0`:

- you save most of the frontend idle cost
- first page load after idle will cold start

Expected range:

- about **$33 to $40/month**

That is the lowest-cost production-style Azure setup I would recommend without cutting into managed Postgres or persistent newsletter storage.

## Mandatory Deployment Notes For This Repo

### 1. Shared persistent storage is required

Care Circle writes newsletters and provider payloads to disk. On any provider, that storage must not be ephemeral.

Mount persistent storage to:

- backend
- scheduler

Without that, generated newsletters and images will disappear on restart or redeploy.

Examples:

- Azure Container Apps storage mounts: https://learn.microsoft.com/en-us/azure/container-apps/storage-mounts
- on a single VM or VPS, this is typically just a host-mounted directory or attached disk

### 2. PDF generation requires Chromium in the scheduler image

PDF generation uses the **Playwright Python library** (`playwright.async_api`) to launch a headless Chromium browser and render newsletter HTML to PDF. There is no Node.js involved.

That means the **scheduler image must include Chromium and its system library dependencies**. A plain `python:slim` base image will not work.

This is already handled in [`Dockerfile.scheduler`](C:/Code/inkandquill/inkquill/Dockerfile.scheduler):

- the runtime stage manually installs all required Chromium system libraries via `apt-get`
- `python -m playwright install chromium` downloads the Chromium binary into the image

**Do not replace `Dockerfile.scheduler` with a plain Python base image.** PDF generation will fail at runtime if the Chromium dependencies are missing.

If you want to split PDF creation out later, the alternative is:

1. Keep the scheduler image as-is with Chromium included
2. Or split PDF creation into a dedicated worker image that carries the same Chromium dependencies

For long-term cleanliness, option 2 is better — but option 1 is what the repo ships today and it works.

### 3. Use scheduled jobs for the scheduler later

The current long-running scheduler service works, but it is not the cheapest long-term shape.

Best future cleanup:

- daily session job
- daily send-email job
- daily PDF job

Azure example reference:

- Azure Container Apps jobs: https://learn.microsoft.com/en-us/azure/container-apps/jobs

### 4. Prefer managed PostgreSQL if you want easier recovery

If you do not want to own Postgres backups, upgrades, and restore testing yourself, use a managed PostgreSQL service from your provider.

Azure example reference:

- Flexible Server overview: https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/overview

## Recommended Generic Environment Layout

### Logical components

- public DNS name
- Ubuntu server
- reverse proxy
- frontend container
- backend container
- scheduler container
- persistent cache/log storage
- PostgreSQL, self-managed or managed
- optional secret store
- optional monitoring/log aggregation

### Networking

For the first low-cost version on any provider:

- expose only the reverse proxy publicly
- keep backend and scheduler private on the Docker network
- keep PostgreSQL private or firewall-restricted

Later hardening:

- private networking for PostgreSQL
- internal-only backend ingress with frontend-to-backend private routing
- CDN, WAF, or load balancer in front if needed

For Option A:

- expose only `80` and `443`
- block direct external access to Postgres
- restrict SSH to your IP only

## Azure Example Environment Layout

If you do choose Azure later, a matching resource layout could be:

- Resource group: `rg-care-circle-prod`
- Container registry: `acrcarecircleprod`
- Container Apps environment: `acae-care-circle-prod`
- Frontend app: `care-circle-frontend`
- Backend app: `care-circle-api`
- Scheduler app: `care-circle-scheduler`
- PostgreSQL server: `psql-care-circle-prod`
- Storage account: `stcarecircleprod`
- Key Vault: `kv-care-circle-prod`
- Log Analytics: `log-care-circle-prod`

## Azure VM Build Specifics

This section keeps the single-host plan provider-neutral while giving you a concrete Azure VM implementation path.

### Recommended Azure shape

For this repo, the most practical Azure version of the single-host plan is:

- **1 Azure Ubuntu VM** for `gateway`, `frontend`, `backend`, and `scheduler`
- **1 Azure managed disk** for persistent app data under `/srv/care-circle`
- **optional Azure Database for PostgreSQL Flexible Server** if you do not want Postgres inside Docker
- **1 public IP**
- **1 network security group**
- **1 DNS record**

Recommended first production footprint on Azure:

- VM size: `2 vCPU / 8 GB RAM`
- OS image: `Ubuntu Server 22.04 LTS - Gen2`
- OS disk: `64 GB` or larger
- Data disk: `128 GB` managed disk for `/srv/care-circle`

Practical Azure mapping:

- use the **OS disk** for Ubuntu, Docker binaries, and temporary build activity
- use the **data disk** for `cache/`, logs, and optionally local Postgres data
- if using Azure Database for PostgreSQL Flexible Server, keep Postgres off the VM and use the data disk only for app artifacts and logs

### Azure portal build checklist

Official Azure VM quickstart reference:

- Microsoft Learn: https://learn.microsoft.com/en-us/azure/virtual-machines/linux/quick-create-portal

When creating the VM in Azure portal, use these choices:

1. Create a new **resource group** such as `rg-care-circle-prod`.
2. Region:
   - use the same Azure region as your main dependencies when practical
   - if Azure Foundry is already in `East US 2`, keeping the VM nearby is a reasonable latency choice
3. Image:
   - `Ubuntu Server 22.04 LTS - Gen2`
4. Size:
   - start around `2 vCPU / 8 GB RAM`
5. Authentication:
   - use **SSH public key**
   - do not use password authentication for the production VM unless you have a specific operational reason
6. Inbound ports:
   - allow `22` for SSH during setup
   - allow `80` and `443` for the site
7. Public IP:
   - keep a public IP only if this VM will terminate public web traffic directly
8. Disks:
   - keep the OS disk separate from app data
   - add a managed data disk for persistent storage
9. Networking:
   - keep the VM in its own virtual network/subnet unless you already have a shared production network design

### Azure CLI build example

Official Azure CLI environment reference:

- Microsoft Learn: https://learn.microsoft.com/en-us/azure/virtual-machines/linux/create-cli-complete

If you want a scripted Azure build instead of clicking through the portal, the Azure CLI flow can look like this:

```bash
az group create --name rg-care-circle-prod --location eastus2

az network vnet create \
  --resource-group rg-care-circle-prod \
  --name vnet-care-circle-prod \
  --address-prefix 10.20.0.0/16 \
  --subnet-name snet-app \
  --subnet-prefix 10.20.1.0/24

az network public-ip create \
  --resource-group rg-care-circle-prod \
  --name pip-care-circle-prod

az network nsg create \
  --resource-group rg-care-circle-prod \
  --name nsg-care-circle-prod

az network nsg rule create \
  --resource-group rg-care-circle-prod \
  --nsg-name nsg-care-circle-prod \
  --name allow-ssh \
  --protocol tcp \
  --priority 1000 \
  --destination-port-range 22 \
  --access allow

az network nsg rule create \
  --resource-group rg-care-circle-prod \
  --nsg-name nsg-care-circle-prod \
  --name allow-http \
  --protocol tcp \
  --priority 1010 \
  --destination-port-range 80 \
  --access allow

az network nsg rule create \
  --resource-group rg-care-circle-prod \
  --nsg-name nsg-care-circle-prod \
  --name allow-https \
  --protocol tcp \
  --priority 1020 \
  --destination-port-range 443 \
  --access allow

az network nic create \
  --resource-group rg-care-circle-prod \
  --name nic-care-circle-prod \
  --vnet-name vnet-care-circle-prod \
  --subnet snet-app \
  --network-security-group nsg-care-circle-prod \
  --public-ip-address pip-care-circle-prod

az vm create \
  --resource-group rg-care-circle-prod \
  --name vm-care-circle-prod \
  --location eastus2 \
  --nics nic-care-circle-prod \
  --image Ubuntu2204 \
  --size Standard_B2ms \
  --admin-username azureuser \
  --generate-ssh-keys \
  --os-disk-size-gb 64
```

Notes:

- `Standard_B2ms` is the closest Azure SKU to the recommended `2 vCPU / 8 GB RAM` starting point
- if you expect heavier PDF generation, move up to a larger VM family instead of trying to run close to the memory limit

### Attach and mount an Azure managed data disk

Official Azure disk references:

- Portal attach: https://learn.microsoft.com/en-us/azure/virtual-machines/linux/attach-disk-portal
- Format and mount: https://learn.microsoft.com/en-us/azure/virtual-machines/linux/disks-format-mount-data-disks-linux

Recommended Azure disk plan:

- OS disk: `64 GB`
- Data disk: `128 GB` managed disk mounted at `/srv/care-circle`

High-level steps:

1. Attach a new managed disk to the VM in Azure.
2. SSH into the VM.
3. Identify the correct disk.
4. Partition and format it.
5. Mount it at `/srv/care-circle`.
6. Persist the mount in `/etc/fstab` using the **UUID**, not the raw device path.

Example Linux commands after the disk is attached:

```bash
lsblk

sudo parted /dev/sdc --script mklabel gpt mkpart xfspart xfs 0% 100%
sudo partprobe /dev/sdc
sudo mkfs.xfs /dev/sdc1

sudo mkdir -p /srv/care-circle
sudo mount /dev/sdc1 /srv/care-circle

sudo blkid
```

Then add the disk to `/etc/fstab` using the disk UUID with the `nofail` option so the VM can still boot if the disk mount has an issue.

Azure-specific note:

- Microsoft explicitly recommends using the **UUID** in `/etc/fstab` because device paths can change after reboot

### Azure network security group guidance

Official NSG reference example:

- Microsoft Learn: https://learn.microsoft.com/en-us/azure/virtual-machines/linux/create-cli-complete

For the Azure VM version of this deployment:

- allow inbound `22` only for admin access, and ideally scope it to your IP
- allow inbound `80` and `443`
- do **not** expose `48000`, `48001`, or `5432` publicly
- keep `backend`, `scheduler`, and local Postgres reachable only inside the VM or Docker network

### Azure managed PostgreSQL variant

Official Azure PostgreSQL reference:

- Microsoft Learn: https://learn.microsoft.com/en-us/azure/postgresql/overview

If you want the safer Azure production shape:

- keep `gateway`, `frontend`, `backend`, and `scheduler` on the Azure VM
- move Postgres to **Azure Database for PostgreSQL Flexible Server**

Reasons this is attractive on Azure:

- automated backups are included
- Azure documents a default backup retention of **7 days**, configurable up to **35 days**
- the **Burstable** tier exists for lower-cost workloads

If you choose this variant:

- update `prod.runtime.env` to point the backend and scheduler at the Azure PostgreSQL hostname
- keep the PostgreSQL server firewall or private access restricted to the VM network path
- do not leave the database wide open to public internet ranges

## Explicit Deployment Task List

This section turns the generic host plan into an actionable task list for one Ubuntu server.

### Task 1: Provision the server

Goal:

- create one Ubuntu host large enough to run `gateway`, `frontend`, `backend`, `scheduler`, and optionally `db`

Recommended starting size:

- `2 vCPU / 8 GB RAM / 120 GB SSD` for the safest first rollout
- `2 vCPU / 4 GB RAM / 80 GB SSD` only if traffic is light and you want the cheapest pilot

Instructions:

1. Create an Ubuntu 22.04 or 24.04 server with a public IP.
2. Add your SSH public key during provisioning.
3. Reserve enough disk for:
   - OS and packages
   - Docker images and build cache
   - `cache/`
   - `logs/`
   - optional local Postgres data
4. Point your DNS record at the server IP.

Exit criteria:

- you can SSH into the server
- the server has enough RAM and disk for the selected footprint
- the domain resolves to the server

### Task 2: Harden the base host

Goal:

- make the server safe enough for an internet-facing first production deployment

Instructions:

1. Update the OS packages:

```bash
sudo apt update
sudo apt upgrade -y
```

2. Install a basic firewall and allow only SSH, HTTP, and HTTPS:

```bash
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

3. Restrict SSH access:
   - disable password login if possible
   - use SSH keys only
   - if your provider supports it, restrict SSH by source IP
4. Set the server timezone and confirm clock sync.
5. Create a non-root deployment user if you do not want to deploy as `root`.

Exit criteria:

- only required ports are open
- SSH is key-based
- the host is patched and reachable

### Task 3: Install Docker and Git

Goal:

- prepare the host to build and run the Care Circle compose stack

Instructions:

1. Install required packages:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg git
```

2. Install Docker Engine and the Compose plugin using Docker's Ubuntu instructions.
3. Confirm the install:

```bash
docker --version
docker compose version
git --version
```

4. If needed, add your deployment user to the `docker` group:

```bash
sudo usermod -aG docker $USER
```

Exit criteria:

- `docker` works
- `docker compose` works
- `git` works

### Task 4: Create the persistent directory layout

Goal:

- ensure `cache`, logs, and optional Postgres data survive rebuilds and restarts

Instructions:

1. Create the data directories:

```bash
sudo mkdir -p /srv/care-circle/prod/cache
sudo mkdir -p /srv/care-circle/prod/logs/backend
sudo mkdir -p /srv/care-circle/prod/logs/scheduler
sudo mkdir -p /srv/care-circle/prod/postgres
```

2. Set ownership so your deployment user can manage them.
3. If you are using a separate disk, mount it under `/srv/care-circle`.

Recommended layout:

```text
/srv/care-circle/
  prod/
    cache/
    logs/
      backend/
      scheduler/
    postgres/
```

Exit criteria:

- the full directory tree exists
- the deployment user can read and write these paths

### Task 5: Clone the repo onto the server

Goal:

- put a known checkout of the application on the production host

Instructions:

1. Clone the repository into a stable location such as `/opt/inkquill` or `/srv/inkquill`.
2. Check out the exact branch or commit you want to deploy.
3. Confirm the deployment assets exist:
   - `deployments/docker-host/docker-compose.base.yml`
   - `deployments/docker-host/docker-compose.prod.yml`
   - `scripts/deploy_care_circle_docker_host.ps1`

Exit criteria:

- the repo is present on the server
- the target commit is selected
- the deployment files are available

### Task 6: Prepare the host-level env files

Goal:

- configure the server-specific paths and ports without editing committed compose files

Instructions:

1. Copy:
   - `deployments/docker-host/env/prod.host.env.example`
   - `deployments/docker-host/env/prod.runtime.env.example`
2. Save them as:
   - `deployments/docker-host/env/prod.host.env`
   - `deployments/docker-host/env/prod.runtime.env`
3. In `prod.host.env`, set the key values:

```dotenv
CARE_CIRCLE_PROJECT_NAME=care-circle-prod
CARE_CIRCLE_PUBLIC_PORT=8083
CARE_CIRCLE_BACKEND_PORT=48000
CARE_CIRCLE_SCHEDULER_PORT=48001
CARE_CIRCLE_DATA_ROOT=/srv/care-circle/prod
CARE_CIRCLE_RUNTIME_ENV_FILE=./env/prod.runtime.env
```

4. Change ports if your host routing needs different values.

Exit criteria:

- both prod env files exist
- `CARE_CIRCLE_DATA_ROOT` matches the real persistent host path
- ports are chosen intentionally

### Task 7: Fill in runtime secrets and app settings

Goal:

- provide production values for database, domain, SMTP, AI provider, and app secrets

Instructions:

1. Update `deployments/docker-host/env/prod.runtime.env`.
2. At minimum, review and set:

```dotenv
APP_PROJECT_NAME=Care Circle Production
APP_ENV=production
APP_URL=https://care-circle.example.com

POSTGRES_USER=care_circle_prod
POSTGRES_PASSWORD=change-me
POSTGRES_DB=care_circle_prod

BACKEND_CORS_ORIGINS=["https://care-circle.example.com"]

APP_LOG_DIR=/app/logs
LOG_LEVEL_CONSOLE=INFO
LOG_LEVEL_FILE=INFO
```

3. Add the rest of the required production secrets:
   - app secret keys
   - SMTP credentials
   - AI provider endpoint and key
   - OAuth credentials if used
   - any Care Circle feature flags needed in production
4. Replace every placeholder value before launch.

Exit criteria:

- the runtime env file is complete
- no placeholder passwords or example domains remain
- CORS and `APP_URL` match the real domain

### Task 8: Configure TLS and public routing

Goal:

- make the site reachable over HTTPS through your public domain

Instructions:

1. Decide whether TLS will terminate:
   - directly on this server with nginx and Let's Encrypt
   - at a provider load balancer or reverse proxy
2. If TLS terminates on the server:
   - issue a certificate with Let's Encrypt
   - update nginx configuration as needed
3. If TLS terminates upstream:
   - keep only the reverse proxy publicly exposed
   - make sure the app still sees the correct public URL
4. Verify DNS, HTTP, and HTTPS before application launch.

Exit criteria:

- the production domain resolves correctly
- HTTPS is working
- the browser does not show certificate warnings

### Task 9: Build and start the stack

Goal:

- bring up the Care Circle production services on the host

Instructions:

1. From the repo root on the server, run the deployment flow that matches your environment.
2. If you are running from Linux, execute the equivalent compose commands directly or run the repo deployment flow from your preferred shell.
3. The intended production bring-up behavior is equivalent to:

```bash
docker compose \
  --project-name care-circle-prod \
  --env-file deployments/docker-host/env/prod.host.env \
  -f deployments/docker-host/docker-compose.base.yml \
  -f deployments/docker-host/docker-compose.prod.yml \
  up -d --build
```

4. Confirm the containers are up:

```bash
docker compose \
  --project-name care-circle-prod \
  --env-file deployments/docker-host/env/prod.host.env \
  -f deployments/docker-host/docker-compose.base.yml \
  -f deployments/docker-host/docker-compose.prod.yml \
  ps
```

Exit criteria:

- all expected containers are created
- `gateway`, `frontend`, `backend`, and `scheduler` stay running
- `db` is running too if you chose local Postgres

### Task 10: Run migrations

Goal:

- align the production database schema with the deployed code

Instructions:

1. Run Alembic migrations before calling the deployment complete.
2. The equivalent direct command is:

```bash
docker compose \
  --project-name care-circle-prod \
  --env-file deployments/docker-host/env/prod.host.env \
  -f deployments/docker-host/docker-compose.base.yml \
  -f deployments/docker-host/docker-compose.prod.yml \
  run --rm --no-deps backend alembic upgrade head
```

3. If migrations fail, stop and fix that before traffic is sent to the app.

Exit criteria:

- Alembic completes successfully
- the app can start against the migrated schema

### Task 11: Verify the application stack

Goal:

- confirm the site, API, scheduler, cache, and PDF generation behave correctly

Instructions:

1. Open the public site in the browser.
2. Check the backend health endpoint.
3. Verify a patient list or primary Care Circle screen loads.
4. Trigger one manual newsletter generation for a known patient.
5. Confirm all expected artifacts are created in the mounted `cache/` path.
6. Confirm a PDF is generated successfully.
7. Confirm email sends or reaches the expected test path if email test mode is enabled.
8. Review container logs for obvious errors.

Exit criteria:

- the frontend loads
- the backend responds
- a newsletter run finishes successfully
- HTML and PDF outputs exist on disk
- logs do not show critical startup failures

### Task 12: Add the minimum operational safeguards

Goal:

- reduce production risk after the first successful launch

Instructions:

1. Set up backup coverage for:
   - Postgres
   - env files
   - nginx or reverse proxy config
2. Set up disk usage monitoring.
3. Set up container and app log review.
4. Document the deployment command and rollback approach.
5. Test a reboot to confirm services come back cleanly.

Exit criteria:

- backups exist
- restore steps are documented
- reboot behavior is known
- disk growth is being watched

## Suggested Production Rollout Order

1. Provision the Ubuntu server
2. Choose Option A, Option B, or Option C
3. Configure DNS, firewall rules, and TLS
4. Create persistent directories or attach persistent storage
5. Prepare runtime env files and secrets
6. Build and deploy containers
7. Run Alembic migrations
8. Trigger one patient newsletter generation manually
9. Verify:
    - cache files are written
    - newsletter HTML is written
    - newsletter PDF is written
    - email sends

## Minimum Validation Checklist

- frontend opens successfully
- backend health endpoint responds
- patient list loads
- patient preview renders
- manual newsletter send works
- scheduler generates today's newsletter
- `newsletter.html` exists in mounted storage
- `newsletter.pdf` exists in mounted storage
- images resolve from mounted cache
- email sends with today's reference date

## What Is Not Needed For Care Circle Right Now

Because this plan is **Care Circle only**, you do **not** need these extra platform resources for the first production rollout unless you later enable broader platform features:

- search infrastructure
- blob-based document ingestion pipeline
- Story-world importer infrastructure
- general forum/blog feature hosting separation

## Final Recommendation

If you are planning to host Care Circle on **one dedicated Ubuntu server**, that is a sound choice and it should be the primary deployment path for this repo right now.

Start with:

- **one Ubuntu server or VPS**
- **the existing `deployments/docker-host` compose bundle**
- **the existing `scripts/deploy_care_circle_docker_host.ps1` deployment script**
- **host-mounted persistent storage for `cache/` and logs**
- **managed PostgreSQL if you want the safer hybrid version**

Use self-managed Postgres on the server only if minimizing cost matters more than recovery simplicity.

The practical recommendation is:

- choose the **single Ubuntu server** path for the first production rollout
- choose the **hybrid server + managed PostgreSQL** variant if you want the best balance of simplicity and operational safety
- keep the plan provider-neutral so you can run this on Azure, IONOS, or another host
- revisit managed container hosting only after you need higher uptime, easier scaling, or less host-level maintenance

## Sources

- Azure Container Apps Jobs: https://learn.microsoft.com/en-us/azure/container-apps/jobs
- Azure Container Apps storage mounts: https://learn.microsoft.com/en-us/azure/container-apps/storage-mounts
- Azure Files mount tutorial for Container Apps: https://learn.microsoft.com/en-us/azure/container-apps/storage-mounts-azure-files
- Azure Database for PostgreSQL Flexible Server overview: https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/overview
- Azure Database for PostgreSQL compute options: https://learn.microsoft.com/en-us/azure/postgresql/flexible-server/concepts-compute
- Azure Retail Prices API: https://prices.azure.com/api/retail/prices
