# Care Circle Production Deployment On A Single Ubuntu Server

This document is for **Care Circle only**, not the broader Ink & Quill platform.

It assumes:

- we are deploying the current Care Circle backend, React frontend, scheduler, email delivery, daily cache, and PDF generation
- an AI provider is already provisioned and will continue to provide the AI models
- SMTP remains external for now
- cost control matters more than high availability

## Recommendation

The recommended first production shape is:

- **one Ubuntu server**
- **Docker Engine + Docker Compose plugin**
- the existing single-host bundle in [deployments/docker-host/README.md](C:/Code/inkandquill/inkquill/deployments/docker-host/README.md)
- persistent host storage for `cache/`, logs, and optionally Postgres data

That Ubuntu server can live on:

- Azure
- IONOS
- DigitalOcean
- Hetzner
- AWS
- Linode/Akamai
- another VPS provider

The key point is that the **server OS should be Ubuntu**, and the **deployment model should stay Docker Compose on one host**.

## Why This Path Fits The Repo

This repo already matches the Ubuntu single-host model well:

- the runtime is already split into `gateway`, `frontend`, `backend`, `scheduler`, and `db`
- the production bundle already exists in [deployments/docker-host](C:/Code/inkandquill/inkquill/deployments/docker-host)
- backend and scheduler already share the mounted cache path
- PDF generation already depends on the scheduler image and Playwright runtime
- the application already writes newsletter HTML, generated images, and PDFs to disk

That makes a single Ubuntu server the shortest path from the current local/test deployment shape to production.

## Recommended Architecture

### Option A: Single Ubuntu server, everything on one box

Run:

- `gateway`
- `frontend`
- `backend`
- `scheduler`
- `db`

on one Ubuntu host with Docker Compose.

Good fit when:

- traffic is still low
- you want the smallest hosting bill
- you want the fewest moving pieces

Tradeoffs:

- single point of failure
- you manage Docker, backups, patching, TLS, and monitoring
- Postgres is your responsibility if you keep it local

### Option B: Single Ubuntu server, managed PostgreSQL

Run on the Ubuntu host:

- `gateway`
- `frontend`
- `backend`
- `scheduler`

Use managed PostgreSQL separately.

Good fit when:

- you still want a simple single-host app deployment
- you want a safer database story
- you want easier backups and recovery

This is the safer hybrid variant, but it is not the selected path when you are committing to Option A.

## Suggested Starting Size

Start with one of these:

1. `2 vCPU / 4 GB RAM` for a light pilot
2. `2 vCPU / 8 GB RAM` for safer headroom
3. `4 vCPU / 16 GB RAM` only if PDF generation and scheduler load justify it

Recommended first production target:

- **`2 vCPU / 8 GB RAM`**
- **`80-160 GB SSD`**

## Persistent Storage Layout

Persist these paths:

- `cache/`
- logs
- Postgres data if Postgres runs on the same host

Suggested host layout:

```text
/srv/care-circle/
  prod/
    cache/
    logs/
      backend/
      scheduler/
    postgres/
    backups/
```

Purpose:

- `cache/`: provider output, cached images, newsletter HTML, newsletter PDF
- `logs/`: backend and scheduler logs
- `postgres/`: local Postgres data if self-managed
- `backups/`: database dumps and optional config snapshots

## Ubuntu Deployment Workflow

The clean production workflow is:

1. provision one Ubuntu server
2. install Docker Engine, Docker Compose plugin, Git, and optional `ufw`
3. clone the repo on the server
4. create production env files under `deployments/docker-host/env/`
5. create persistent directories under `/srv/care-circle/prod`
6. run Docker Compose directly on the server
7. run Alembic migrations
8. verify frontend, backend, scheduler, cache, PDF generation, and email

## Recommended Host Layout

Use:

- repo checkout in `/opt/inkquill` or `/srv/inkquill`
- persistent app data in `/srv/care-circle/prod`

Example:

```text
/opt/inkquill
/srv/care-circle/prod/cache
/srv/care-circle/prod/logs/backend
/srv/care-circle/prod/logs/scheduler
/srv/care-circle/prod/postgres
/srv/care-circle/prod/backups
```

## Production Task List

### Task 1: Provision the Ubuntu server

Goal:

- create one Ubuntu VM or VPS large enough to run `gateway`, `frontend`, `backend`, `scheduler`, and optionally `db`

Recommended shape:

- Ubuntu 22.04 LTS or Ubuntu 24.04 LTS
- `2 vCPU / 8 GB RAM`
- `80-160 GB SSD`

Instructions:

1. Create the Ubuntu VM with a public IP.
2. Use SSH key authentication.
3. Point your DNS record at the server IP.
4. Keep the host in the same region as managed dependencies when practical.

Exit criteria:

- you can SSH into the host
- the domain resolves to the host
- the host has enough RAM and disk for the selected footprint

### Task 2: Harden the base host

Goal:

- make the Ubuntu host safe enough for an internet-facing production deployment

Instructions:

1. Update packages:

```bash
sudo apt update
sudo apt upgrade -y
```

2. Install and enable a simple firewall:

```bash
sudo apt install -y ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

3. In `/etc/ssh/sshd_config`, prefer:
   - `PasswordAuthentication no`
   - `PermitRootLogin no`
4. Restart SSH if you changed SSH config:

```bash
sudo systemctl restart ssh
```

5. Set the server timezone if needed:

```bash
timedatectl
sudo timedatectl set-timezone America/Los_Angeles
```

Exit criteria:

- only required ports are open
- SSH is key-based
- the host is patched and reachable

### Task 3: Install Docker and Git

Goal:

- prepare the Ubuntu host to build and run the Care Circle compose stack

Instructions:

1. Install dependencies:

```bash
sudo apt update
sudo apt install -y ca-certificates curl gnupg git
```

2. Install Docker Engine and Compose plugin using Docker’s official Linux repository:

```bash
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo \"$VERSION_CODENAME\") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

3. Add your deployment user to the `docker` group:

```bash
sudo usermod -aG docker "$USER"
newgrp docker
```

4. Confirm the install:

```bash
docker --version
docker compose version
git --version
```

Exit criteria:

- `docker` works
- `docker compose` works
- `git` works

### Task 4: Create persistent directories

Goal:

- ensure `cache`, logs, and optional Postgres data survive restarts and rebuilds

Instructions:

```bash
sudo mkdir -p /srv/care-circle/prod/cache
sudo mkdir -p /srv/care-circle/prod/logs/backend
sudo mkdir -p /srv/care-circle/prod/logs/scheduler
sudo mkdir -p /srv/care-circle/prod/postgres
sudo mkdir -p /srv/care-circle/prod/backups
sudo chown -R "$USER":"$USER" /srv/care-circle
```

Exit criteria:

- the directory tree exists
- the deployment user can read and write it

### Task 5: Clone the repo

Goal:

- put a known checkout of the application on the production host

Instructions:

```bash
sudo mkdir -p /opt
sudo chown -R "$USER":"$USER" /opt
cd /opt
git clone <your-repo-url> inkquill
cd /opt/inkquill
git checkout <branch-or-tag>
```

Confirm these files exist:

- `deployments/docker-host/docker-compose.base.yml`
- `deployments/docker-host/docker-compose.prod.yml`
- `scripts/deploy_care_circle_docker_host.ps1`

Exit criteria:

- the repo is present on the server
- the target commit is selected
- the deployment assets exist

### Task 6: Prepare host env files

Goal:

- configure server-specific paths and ports without editing committed compose files

Instructions:

1. Copy:

- `deployments/docker-host/env/prod.host.env.example`
- `deployments/docker-host/env/prod.runtime.env.example`

2. Save them as:

- `deployments/docker-host/env/prod.host.env`
- `deployments/docker-host/env/prod.runtime.env`

3. In `prod.host.env`, use Linux paths:

```dotenv
CARE_CIRCLE_PROJECT_NAME=care-circle-prod
CARE_CIRCLE_PUBLIC_PORT=8083
CARE_CIRCLE_BACKEND_PORT=48000
CARE_CIRCLE_SCHEDULER_PORT=48001
CARE_CIRCLE_DATA_ROOT=/srv/care-circle/prod
CARE_CIRCLE_RUNTIME_ENV_FILE=./env/prod.runtime.env
```

Notes:

- `CARE_CIRCLE_DATA_ROOT` must be a Linux path
- ports can be changed if your reverse proxy design requires it

Exit criteria:

- both prod env files exist
- `CARE_CIRCLE_DATA_ROOT` matches the real host path
- ports are intentionally chosen

### Task 7: Fill in runtime secrets and settings

Goal:

- provide production values for database, domain, SMTP, AI provider, and app secrets

Instructions:

1. Update `deployments/docker-host/env/prod.runtime.env`.
2. At minimum, review and set:

```dotenv
APP_PROJECT_NAME=Care Circle Production
APP_ENV=production
APP_URL=https://care-circle.example.com

# Option A local Postgres container
DATABASE_URL=postgresql+asyncpg://inkquill:inkandquill_password@db:5432/inkquill

BACKEND_CORS_ORIGINS=["https://care-circle.example.com"]

APP_LOG_DIR=/app/logs
LOG_LEVEL_CONSOLE=INFO
LOG_LEVEL_FILE=INFO

SCHEDULER_BASE_URL=http://backend:8000
```

3. Also set:

- app secret keys
- SMTP credentials
- AI provider endpoint and key
- OAuth credentials if used
- any Care Circle production feature flags

Exit criteria:

- the runtime env file is complete
- no placeholder secrets remain
- `APP_URL` and CORS match the production domain

### Task 8: Configure TLS and public routing

Goal:

- make the site reachable over HTTPS

Instructions:

1. Decide whether TLS terminates:
   - directly on the host
   - upstream at a provider load balancer or reverse proxy
2. If terminating on the host, use Let’s Encrypt.
3. If using host-level Nginx, proxy to the compose gateway port.
4. If using provider-level TLS, still keep only `80/443` public.

Exit criteria:

- the domain resolves correctly
- HTTPS works
- the browser shows a valid certificate

### Task 9: Build and start the stack

Goal:

- bring up the Care Circle production services

On Ubuntu, use direct Docker Compose commands. That is the recommended path.

From the repo root:

```bash
docker compose \
  --project-name care-circle-prod \
  --env-file deployments/docker-host/env/prod.host.env \
  -f deployments/docker-host/docker-compose.base.yml \
  -f deployments/docker-host/docker-compose.prod.yml \
  up -d --build
```

Check status:

```bash
docker compose \
  --project-name care-circle-prod \
  --env-file deployments/docker-host/env/prod.host.env \
  -f deployments/docker-host/docker-compose.base.yml \
  -f deployments/docker-host/docker-compose.prod.yml \
  ps
```

Notes:

- the repo includes a PowerShell deployment script, but on Ubuntu the simplest production path is to run `docker compose` directly
- install PowerShell on Ubuntu only if you specifically want to reuse the `.ps1` helper

Exit criteria:

- expected containers are created
- `gateway`, `frontend`, `backend`, and `scheduler` stay running
- `db` stays running too if you chose local Postgres

### Task 10: Run migrations

Goal:

- align the production schema with the deployed code

Run:

```bash
docker compose \
  --project-name care-circle-prod \
  --env-file deployments/docker-host/env/prod.host.env \
  -f deployments/docker-host/docker-compose.base.yml \
  -f deployments/docker-host/docker-compose.prod.yml \
  run --rm --no-deps backend alembic upgrade head
```

Exit criteria:

- Alembic completes successfully
- the app can start against the migrated schema

### Task 11: Verify the stack

Goal:

- confirm site, API, scheduler, cache, and PDF generation behave correctly

Checks:

1. Open the public site.
2. Check the backend health path.
3. Verify a primary Care Circle page loads.
4. Trigger one manual newsletter generation for a known patient.
5. Confirm expected files appear in the mounted `cache/` path.
6. Confirm a PDF is generated.
7. Confirm email sends or reaches the expected test route.
8. Review container logs.

Useful commands:

```bash
docker compose \
  --project-name care-circle-prod \
  --env-file deployments/docker-host/env/prod.host.env \
  -f deployments/docker-host/docker-compose.base.yml \
  -f deployments/docker-host/docker-compose.prod.yml \
  logs --tail=200 backend

docker compose \
  --project-name care-circle-prod \
  --env-file deployments/docker-host/env/prod.host.env \
  -f deployments/docker-host/docker-compose.base.yml \
  -f deployments/docker-host/docker-compose.prod.yml \
  logs --tail=200 scheduler
```

Exit criteria:

- frontend loads
- backend responds
- newsletter generation completes
- HTML and PDF outputs exist on disk
- logs do not show critical startup failures

### Task 12: Add minimum safeguards

Goal:

- reduce operational risk after first successful launch

Instructions:

1. Set up database backups.
2. Back up env files and any host-level proxy config.
3. Monitor disk usage.
4. Document deployment and rollback commands.
5. Reboot the host once to confirm services recover cleanly.

Exit criteria:

- backups exist
- restore steps are documented
- reboot behavior is known
- disk growth is being watched

## Suggested Production Rollout Order

1. Provision the Ubuntu server
2. Use the local Postgres container that is part of Option A
3. Configure DNS, firewall rules, and TLS
4. Create persistent directories
5. Prepare runtime env files and secrets
6. Build and deploy containers
7. Run Alembic migrations
8. Trigger one patient newsletter generation manually
9. Verify cache, newsletter HTML, newsletter PDF, and email

## Minimum Validation Checklist

- frontend opens successfully
- backend health endpoint responds
- patient list or primary Care Circle screen loads
- manual newsletter send works
- scheduler generates today’s newsletter
- `newsletter.html` exists in mounted storage
- `newsletter.pdf` exists in mounted storage
- images resolve from mounted cache
- email sends with the expected date reference

## Azure-Specific Notes

Azure is still a valid host choice. If you use Azure for Option A, the recommendation is:

- **Azure Ubuntu VM**
- optional **Azure managed disk** mounted under `/srv/care-circle`
- local **Postgres container** inside the Docker Compose stack

Recommended Azure mapping for Option A:

- VM image: `Ubuntu Server 22.04 LTS - Gen2` or newer Ubuntu LTS
- App VM size: `Standard_B2s` or `Standard_B2ms` depending on RAM needs
- Managed disk: `128 GB` if you want separate persistent app data storage
- Database: local Postgres container from the compose stack

What not to do for this deployment:

- do not center the rollout on Azure App Service
- do not treat Windows Server as the primary host OS for this Care Circle path
- do not expose backend or Postgres ports publicly

For Azure NSG or firewall rules:

- allow inbound `22` only for admin access
- allow inbound `80`
- allow inbound `443`
- do not expose `48000`, `48001`, or `5432` publicly

## Exact Azure CLI Provisioning For Option A

This is the recommended Azure shape for this repo when you choose Option A:

- one **Ubuntu VM** for `gateway`, `frontend`, `backend`, `scheduler`, and `db`
- one **managed data disk** mounted at `/srv/care-circle`

These commands are written for **Azure CLI in Bash**.

### Single Copy-Paste Script

This block provisions the Azure infrastructure for Option A with your subscription ID already filled in.

Edit these values before running:

- `DNS_LABEL`
- `SSH_KEY`

Recommended to edit before running:

- `ADMIN_USER`
- `LOCATION`
- `ZONE`

The script provisions:

- resource group
- VNet and subnet
- NSG with SSH, HTTP, and HTTPS rules
- public IP
- NIC
- Ubuntu VM
- managed data disk

It does **not** install Docker or deploy the app. That happens after SSHing into the VM.

This script now:

- checks a shortlist of preferred VM sizes in `eastus2`
- picks the first size Azure reports as available in your selected zone
- stops with a clear message if none of the preferred sizes are available

```bash
set -euo pipefail

SUBSCRIPTION_ID="a78befd0-e20a-4c41-97e3-f830a5bb1006"
LOCATION="eastus2"
RG="rg-care-circle-prod"

VNET="vnet-care-circle-prod"
SUBNET_APP="snet-app"
NSG="nsg-care-circle-prod"
PIP="pip-care-circle-prod"
NIC="nic-care-circle-prod"
VM="vm-care-circle-prod"
VM_IMAGE="Ubuntu2204"
ADMIN_USER="azureuser"
SSH_KEY="$HOME/.ssh/id_ed25519.pub"
DNS_LABEL="carecircle-prod-$(date +%s)"
ZONE="1"

DATA_DISK_NAME="disk-care-circle-prod-data"
DATA_DISK_SIZE_GB="128"

MY_IP="$(curl -s https://api.ipify.org)"

PREFERRED_VM_SIZES=(
  "Standard_B2ms"
  "Standard_B2s"
  "Standard_D2as_v5"
  "Standard_D2s_v5"
)

az account set --subscription "$SUBSCRIPTION_ID"

az group create \
  --name "$RG" \
  --location "$LOCATION"

az network vnet create \
  --resource-group "$RG" \
  --name "$VNET" \
  --location "$LOCATION" \
  --address-prefixes 10.30.0.0/16 \
  --subnet-name "$SUBNET_APP" \
  --subnet-prefixes 10.30.1.0/24

az network nsg create \
  --resource-group "$RG" \
  --name "$NSG" \
  --location "$LOCATION"

az network nsg rule create \
  --resource-group "$RG" \
  --nsg-name "$NSG" \
  --name allow-ssh-admin \
  --priority 1000 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes "$MY_IP" \
  --source-port-ranges "*" \
  --destination-address-prefixes "*" \
  --destination-port-ranges 22

az network nsg rule create \
  --resource-group "$RG" \
  --nsg-name "$NSG" \
  --name allow-http \
  --priority 1010 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes Internet \
  --source-port-ranges "*" \
  --destination-address-prefixes "*" \
  --destination-port-ranges 80

az network nsg rule create \
  --resource-group "$RG" \
  --nsg-name "$NSG" \
  --name allow-https \
  --priority 1020 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes Internet \
  --source-port-ranges "*" \
  --destination-address-prefixes "*" \
  --destination-port-ranges 443

az network public-ip create \
  --resource-group "$RG" \
  --name "$PIP" \
  --location "$LOCATION" \
  --version IPv4 \
  --sku Standard \
  --zone "$ZONE" \
  --dns-name "$DNS_LABEL"

az network nic create \
  --resource-group "$RG" \
  --name "$NIC" \
  --location "$LOCATION" \
  --vnet-name "$VNET" \
  --subnet "$SUBNET_APP" \
  --public-ip-address "$PIP" \
  --network-security-group "$NSG"

echo
echo "Checking VM size availability in $LOCATION zone $ZONE..."
VM_SIZE=""
for SKU in "${PREFERRED_VM_SIZES[@]}"; do
  if az vm list-skus \
    --location "$LOCATION" \
    --resource-type virtualMachines \
    --zone \
    --query "[?name=='${SKU}' && contains(locationInfo[0].zones, '${ZONE}')].name | [0]" \
    --output tsv | grep -qx "$SKU"; then
    VM_SIZE="$SKU"
    break
  fi
done

if [ -z "$VM_SIZE" ]; then
  echo "No preferred VM sizes are currently available in $LOCATION zone $ZONE."
  echo "Checked sizes: ${PREFERRED_VM_SIZES[*]}"
  echo "Try a different zone or location, then rerun."
  exit 1
fi

echo "Using VM size: $VM_SIZE"

az vm create \
  --resource-group "$RG" \
  --name "$VM" \
  --location "$LOCATION" \
  --nics "$NIC" \
  --image "$VM_IMAGE" \
  --size "$VM_SIZE" \
  --admin-username "$ADMIN_USER" \
  --authentication-type ssh \
  --ssh-key-values "$SSH_KEY" \
  --zone "$ZONE" \
  --os-disk-size-gb 64 \
  --no-wait

echo
echo "VM create request submitted. Waiting for Azure to finish provisioning..."
az vm wait \
  --resource-group "$RG" \
  --name "$VM" \
  --created

az vm disk attach \
  --resource-group "$RG" \
  --vm-name "$VM" \
  --name "$DATA_DISK_NAME" \
  --new \
  --size-gb "$DATA_DISK_SIZE_GB"

echo
echo "Provisioning complete."
echo
echo "Public endpoint:"
az network public-ip show \
  --resource-group "$RG" \
  --name "$PIP" \
  --query "{ip:ipAddress,fqdn:dnsSettings.fqdn}" \
  --output table

echo
echo "VM status:"
az vm show -d \
  --resource-group "$RG" \
  --name "$VM" \
  --query "{privateIps:privateIps,publicIps:publicIps,fqdns:fqdns,powerState:powerState}" \
  --output table

echo
echo "SSH command:"
echo "ssh ${ADMIN_USER}@$(az network public-ip show --resource-group "$RG" --name "$PIP" --query ipAddress -o tsv)"
```

### After Provisioning

SSH into the VM and mount the data disk:

```bash
lsblk
sudo parted /dev/sdc --script mklabel gpt mkpart xfspart xfs 0% 100%
sudo partprobe /dev/sdc
sudo mkfs.xfs /dev/sdc1
sudo mkdir -p /srv/care-circle
sudo mount /dev/sdc1 /srv/care-circle
sudo blkid
```

Then add the disk UUID to `/etc/fstab`, install Docker, clone the repo, and continue with the production deployment steps in this document.

### Variables

Set your values first:

```bash
SUBSCRIPTION_ID="<your-subscription-id>"code
LOCATION="eastus2"
RG="rg-care-circle-prod"

VNET="vnet-care-circle-prod"
SUBNET_APP="snet-app"
NSG="nsg-care-circle-prod"
PIP="pip-care-circle-prod"
NIC="nic-care-circle-prod"
VM="vm-care-circle-prod"
VM_SIZE="Standard_B2ms"
VM_IMAGE="Ubuntu2204"
ADMIN_USER="azureuser"
SSH_KEY="$HOME/.ssh/id_ed25519.pub"
DNS_LABEL="<globally-unique-dns-label>"
ZONE="1"

DATA_DISK_NAME="disk-care-circle-prod-data"
DATA_DISK_SIZE_GB="128"

MY_IP="$(curl -s https://api.ipify.org)"
```

### 1. Select subscription and create resource group

```bash
az account set --subscription "$SUBSCRIPTION_ID"

az group create \
  --name "$RG" \
  --location "$LOCATION"
```

### 2. Create VNet and subnet

```bash
az network vnet create \
  --resource-group "$RG" \
  --name "$VNET" \
  --location "$LOCATION" \
  --address-prefixes 10.30.0.0/16 \
  --subnet-name "$SUBNET_APP" \
  --subnet-prefixes 10.30.1.0/24
```

### 3. Create NSG and inbound rules

Allow:

- SSH from your current public IP only
- HTTP from anywhere
- HTTPS from anywhere

```bash
az network nsg create \
  --resource-group "$RG" \
  --name "$NSG" \
  --location "$LOCATION"

az network nsg rule create \
  --resource-group "$RG" \
  --nsg-name "$NSG" \
  --name allow-ssh-admin \
  --priority 1000 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes "$MY_IP" \
  --source-port-ranges "*" \
  --destination-address-prefixes "*" \
  --destination-port-ranges 22

az network nsg rule create \
  --resource-group "$RG" \
  --nsg-name "$NSG" \
  --name allow-http \
  --priority 1010 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes Internet \
  --source-port-ranges "*" \
  --destination-address-prefixes "*" \
  --destination-port-ranges 80

az network nsg rule create \
  --resource-group "$RG" \
  --nsg-name "$NSG" \
  --name allow-https \
  --priority 1020 \
  --direction Inbound \
  --access Allow \
  --protocol Tcp \
  --source-address-prefixes Internet \
  --source-port-ranges "*" \
  --destination-address-prefixes "*" \
  --destination-port-ranges 443
```

### 4. Create a Standard public IP

For a zonal VM, use a Standard SKU zonal public IP in the same zone:

```bash
az network public-ip create \
  --resource-group "$RG" \
  --name "$PIP" \
  --location "$LOCATION" \
  --version IPv4 \
  --sku Standard \
  --zone "$ZONE" \
  --dns-name "$DNS_LABEL"
```

### 5. Create NIC

```bash
az network nic create \
  --resource-group "$RG" \
  --name "$NIC" \
  --location "$LOCATION" \
  --vnet-name "$VNET" \
  --subnet "$SUBNET_APP" \
  --public-ip-address "$PIP" \
  --network-security-group "$NSG"
```

### 6. Create the Ubuntu VM

```bash
az vm create \
  --resource-group "$RG" \
  --name "$VM" \
  --location "$LOCATION" \
  --nics "$NIC" \
  --image "$VM_IMAGE" \
  --size "$VM_SIZE" \
  --admin-username "$ADMIN_USER" \
  --authentication-type ssh \
  --ssh-key-values "$SSH_KEY" \
  --zone "$ZONE" \
  --os-disk-size-gb 64
```

### 7. Attach a managed data disk for `/srv/care-circle`

This creates and attaches a new managed disk:

```bash
az vm disk attach \
  --resource-group "$RG" \
  --vm-name "$VM" \
  --name "$DATA_DISK_NAME" \
  --new \
  --size-gb "$DATA_DISK_SIZE_GB"
```

### 8. Useful output values

Public IP:

```bash
az network public-ip show \
  --resource-group "$RG" \
  --name "$PIP" \
  --query "{ip:ipAddress,fqdn:dnsSettings.fqdn}" \
  --output table
```

VM private/public IPs:

```bash
az vm show -d \
  --resource-group "$RG" \
  --name "$VM" \
  --query "{privateIps:privateIps,publicIps:publicIps,fqdns:fqdns,powerState:powerState}" \
  --output table
```

### 9. SSH into the VM

```bash
ssh "$ADMIN_USER@$(az network public-ip show --resource-group "$RG" --name "$PIP" --query ipAddress -o tsv)"
```

### 10. Inside the VM: format and mount the data disk

After SSHing into the VM:

```bash
lsblk

sudo parted /dev/sdc --script mklabel gpt mkpart xfspart xfs 0% 100%
sudo partprobe /dev/sdc
sudo mkfs.xfs /dev/sdc1

sudo mkdir -p /srv/care-circle
sudo mount /dev/sdc1 /srv/care-circle

sudo blkid
```

Then add the disk to `/etc/fstab` using the UUID returned by `blkid`.

Example:

```bash
UUID=<disk-uuid-from-blkid> /srv/care-circle xfs defaults,nofail 0 2
```

Then:

```bash
sudo mount -a
df -h
```

### What this provisions

This Azure CLI flow creates:

- resource group
- virtual network
- subnet
- network security group
- SSH/HTTP/HTTPS NSG rules
- public IP
- NIC
- Ubuntu VM
- managed data disk

### What it does not provision

You still do these next on the VM:

- install Docker Engine and Docker Compose plugin
- clone the repo
- create `deployments/docker-host/env/prod.host.env`
- create `deployments/docker-host/env/prod.runtime.env`
- run the production compose deployment
- let the compose stack create and run the local `db` container

## Standalone Postgres Docker Container

For local development, testing, or a dedicated single-VM database host, use [docker-compose.postgres-single.yml](C:/Code/inkandquill/inkquill/docker-compose.postgres-single.yml).

Quick start:

```bash
docker compose -f docker-compose.postgres-single.yml up -d
```

Details:

- container name: `postgres-single-vm`
- host port: `5433` to container `5432`
- database: `inkquill`
- user: `inkquill`
- password: `inkandquill_password`
- persistent volume: `postgres_single_vm`
- image: `postgres:16-alpine`
- healthcheck: built-in `pg_isready`
- restart policy: `unless-stopped`

Connect:

```bash
psql -h localhost -p 5433 -U inkquill -d inkquill
```

Management:

- stop: `docker compose -f docker-compose.postgres-single.yml down`
- logs: `docker compose -f docker-compose.postgres-single.yml logs -f`
- status: `docker compose -f docker-compose.postgres-single.yml ps`

## Frontend Browser Smoke Checklist

Run these browser checks after every production deployment to verify the React frontend is working end to end. Go through each item in order. If a check fails, review container logs before proceeding.

### Auth and platform shell

- [ ] Open the root URL. The public landing page or login page loads without a blank screen or 500 error.
- [ ] Navigate to a protected route while unauthenticated (e.g. `/care-circle-family`). You are redirected to login.
- [ ] Log in with a known test account. You are redirected to the family landing page.
- [ ] Reload the page. The session is preserved (no redirect to login).
- [ ] Open the account edit page at `/care-circle-family/account/edit`, make a minor change, and save. The profile saves and a success toast appears.
- [ ] Log out. You are redirected to login. Navigating to a protected route confirms the session is gone.

### Family: core flows

- [ ] Go to `/care-circle-family/patients`. At least one patient profile row loads.
- [ ] Click a patient row. The patient detail page loads with name, stage, timezone, and image sign-in keys visible.
- [ ] Open the edit view (`?edit=1`). Provider toggles for that patient are visible and respond to clicks.
- [ ] Go to `/care-circle-family/providers`. The provider catalog loads with at least two provider cards.
- [ ] Click a provider. The provider detail page loads with the patient mapping table and enabled/disabled toggles.

### Family: account and membership

- [ ] Go to `/care-circle-family/account`. The join code is visible. The invite-by-email field and "Send invite email" button are present.
- [ ] Go to `/care-circle-family/members`. The member list loads (even if empty for a new family).
- [ ] Go to `/care-circle-family/billing`. The billing surface loads without an error state.
- [ ] Go to `/care-circle-family/referrals`. The referrals surface loads without an error state.

### Family: activity feed and media

- [ ] Go to `/care-circle-family/events`. The activity feed loads. If events exist they are listed; if not, the empty state is shown.
- [ ] Go to `/care-circle-family/media`. The media library loads. If no photos exist the empty-state card is shown with the upload button.
- [ ] Upload a small JPEG. A success toast appears and the new photo appears in the grid.
- [ ] Delete the uploaded photo. A success toast appears and the photo is removed from the grid.

### Family: admin surfaces

- [ ] Go to `/care-circle-family/admin`. The admin dashboard loads.
- [ ] Go to `/care-circle-family/admin/scheduler`. The Scheduler Console heading is visible, jobs are listed, and "Run now" buttons are present.
- [ ] Click "Run now" for one job. A success or in-progress response toast appears.
- [ ] Go to `/care-circle-family/admin/template-studio?provider=weather&theme=classic`. The GrapesJS editor frame loads and the "Save template" button is visible.
- [ ] Go to `/care-circle-family/admin/families` (admin accounts only). The families table loads.

### Patient: sign-in and daily session

- [ ] Go to `/care-circle-patient/login`. The image-based sign-in grid loads with emoji tiles.
- [ ] Select the correct image combination for a known patient. The patient home page loads.
- [ ] Verify provider highlights are shown on `/care-circle-patient/home` (at least one card).
- [ ] Submit a like or dislike feedback on a highlight card. The UI updates without a full page reload.

### Backend and scheduler health

- [ ] Open `/health` on the backend port. The health JSON response shows `status: ok`.
- [ ] Open `/api/admin/scheduler/health`. The scheduler health JSON response shows `scheduler_running: true`.
- [ ] Open `/api/admin/scheduler/status`. At least two scheduled task entries are listed.

### Cache, PDF, and email

- [ ] Trigger manual provider pre-cache from the scheduler console ("Run now" on the precache task).
- [ ] Confirm expected HTML or image output appears in the mounted `cache/` path on the host within 60 seconds.
- [ ] Trigger newsletter generation for one patient from the scheduler console or API.
- [ ] Confirm a `.pdf` file appears in `cache/` for that patient.
- [ ] If SMTP is configured, confirm the email arrives or appears in the test email route/log.

---

## Frontend Verification Commands

### Run Playwright e2e tests locally (against the local build)

These tests use mocked API responses and verify UI behavior without a live backend.

```bash
cd frontendv1
npm run test:e2e
```

To open the interactive Playwright UI:

```bash
cd frontendv1
npm run test:e2e:ui
```

### Run e2e tests against a specific deployed URL

Point `PLAYWRIGHT_BASE_URL` at the deployed gateway and run against live API responses:

```bash
cd frontendv1
PLAYWRIGHT_BASE_URL=https://care-circle.example.com npx playwright test
```

Note: live-API runs will fail auth-dependent tests unless you add a test user setup fixture or disable auth-only specs. For production smoke purposes, use the manual browser checklist above and reserve Playwright for pre-deployment CI verification.

### Run backend unit and integration tests before deployment

```powershell
# Unit tests only
.\.venv\Scripts\python.exe -m pytest tests\unit -q

# Unit + integration (skip heavy AI/storage tests)
.\.venv\Scripts\python.exe -m pytest tests\unit tests\integration `
  --ignore=tests/integration/shared/test_document_upload_integration.py `
  --ignore=tests/integration/shared/test_image_generation_integration.py -q
```

---

## Final Recommendation

If you are moving Care Circle to production now and have chosen Option A, the best fit for this repo is:

- **one dedicated Ubuntu server**
- **the existing `deployments/docker-host` compose bundle**
- **direct Docker Compose commands on Linux**
- **host-mounted persistent storage for `cache/` and logs**
- **the local Postgres container in the compose stack**

The practical recommendation is:

- choose the **single Ubuntu server** path for the first production rollout
- keep **Postgres in Docker on the same host** for the first rollout because that is the Option A path
- keep Azure as an optional infrastructure provider, not as the deployment model itself
- revisit managed container hosting only after uptime, scaling, or operational needs justify it
