# Docker Setup Guide — OrderFlow Backend

This document covers every supported way to run the PostgreSQL and Redis dependencies for OrderFlow, depending on your development environment. Follow the section that matches your setup.

---

## Table of Contents

1. [Quick Reference](#quick-reference)
2. [Setup A — Docker installed locally](#setup-a--docker-installed-locally)
3. [Setup B — Docker running on a remote VM (Docker context)](#setup-b--docker-running-on-a-remote-vm-docker-context)
4. [Setup C — No Docker at all (native PostgreSQL + Redis)](#setup-c--no-docker-at-all-native-postgresql--redis)
5. [Environment Variables](#environment-variables)
6. [Common Commands](#common-commands)
7. [Troubleshooting](#troubleshooting)

---

## Quick Reference

| Your situation | Go to |
|---|---|
| Docker Desktop installed and working locally | [Setup A](#setup-a--docker-installed-locally) |
| Docker running inside VirtualBox / VMware VM | [Setup B](#setup-b--docker-running-on-a-remote-vm-docker-context) |
| Windows + VirtualBox conflict (Hyper-V / watchdog crashes) | [Setup B](#setup-b--docker-running-on-a-remote-vm-docker-context) |
| No Docker at all, want native services | [Setup C](#setup-c--no-docker-at-all-native-postgresql--redis) |

---

## docker-compose.yml

All setups use the same file. Place it at the project root.

```yaml
services:
  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_USER: orderflow
      POSTGRES_PASSWORD: orderflow
      POSTGRES_DB: orderflow
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

---

## Setup A — Docker installed locally

**Prerequisites:** Docker Desktop (Mac/Linux) or Docker Engine (Linux) installed and running.

### Start services
```bash
docker compose up -d
```

### Verify both containers are running
```bash
docker compose ps
```

Expected output:
```
NAME                        STATUS      PORTS
orderflow-backend-db-1      running     0.0.0.0:5432->5432/tcp
orderflow-backend-redis-1   running     0.0.0.0:6379->6379/tcp
```

### .env for local Docker
```
DATABASE_URL=postgresql+asyncpg://orderflow:orderflow@localhost:5432/orderflow
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

---

## Setup B — Docker running on a remote VM (Docker context)

Use this when Docker runs inside a VM (VirtualBox, VMware) and you want to issue
Docker commands from your dev machine without SSH-ing in every time.

> **Windows users:** if Docker Desktop causes Hyper-V / synthetic watchdog timeout
> crashes with VirtualBox, install the Docker CLI standalone binary only — no Engine,
> no Hyper-V. See Step 1B below.

---

### Step 1A — Install Docker CLI on macOS / Linux dev machine

```bash
# macOS (Homebrew)
brew install docker docker-compose

# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install docker-ce-cli docker-compose-plugin -y
```

---

### Step 1B — Install Docker CLI on Windows (no Docker Desktop, no Hyper-V)

Open PowerShell as Administrator:

```powershell
# Download the official 64-bit Docker CLI binary
curl.exe -L -o "$env:TEMP\docker.zip" "https://download.docker.com/win/static/stable/x86_64/docker-26.1.4.zip"

# Extract and move to permanent location
Expand-Archive "$env:TEMP\docker.zip" -DestinationPath "$env:TEMP\docker-cli"
New-Item -ItemType Directory -Force -Path "C:\docker-cli"
Move-Item "$env:TEMP\docker-cli\docker\docker.exe" "C:\docker-cli\docker.exe"

# Download docker-compose binary
curl.exe -L -o "C:\docker-cli\docker-compose.exe" "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-windows-x86_64.exe"

# Add C:\docker-cli to the FRONT of PATH (so it takes priority over any old docker.exe)
[System.Environment]::SetEnvironmentVariable(
  "Path",
  "C:\docker-cli;" + [System.Environment]::GetEnvironmentVariable("Path", "Machine"),
  [System.EnvironmentVariableTarget]::Machine
)
```

Open a **new** PowerShell window and verify:

```powershell
docker --version        # Docker version 26.x.x
docker-compose --version  # Docker Compose version v2.24.5
```

> **Conflict with old docker.exe in System32?**
> ```powershell
> # Remove the broken binary (run as Administrator)
> takeown /f "C:\Windows\System32\docker.exe"
> icacls "C:\Windows\System32\docker.exe" /grant administrators:F
> Remove-Item "C:\Windows\System32\docker.exe" -Force
> ```

---

### Step 2 — Prepare the VM (Ubuntu/Debian)

SSH into the VM:
```bash
ssh your_username@YOUR_VM_IP
```

Install OpenSSH server if not already installed:
```bash
sudo apt update
sudo apt install openssh-server -y
sudo systemctl start ssh
sudo systemctl enable ssh
sudo ufw allow ssh
```

Install Docker and the Compose plugin:
```bash
sudo apt install docker.io docker-compose-plugin -y
sudo systemctl start docker
sudo systemctl enable docker
```

Add your user to the docker group (avoids needing sudo):
```bash
sudo usermod -aG docker $USER
newgrp docker

# Verify docker works without sudo
docker ps
```

Get the VM's IP address:
```bash
hostname -I | awk '{print $1}'
# Note this IP — e.g. 192.168.1.105
```

---

### Step 3 — Set up SSH key authentication (Windows)

On your dev machine (PowerShell):

```powershell
# Generate an SSH key pair
ssh-keygen -t ed25519 -C "orderflow-vm"
# Press Enter 3 times to accept defaults

# Copy the public key to the VM (last time you type a password)
type $env:USERPROFILE\.ssh\id_ed25519.pub | ssh your_username@192.168.1.105 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"

# Test passwordless login
ssh your_username@192.168.1.105
# No password prompt = success, type exit to return
```

On macOS / Linux:
```bash
ssh-keygen -t ed25519 -C "orderflow-vm"
ssh-copy-id your_username@192.168.1.105
ssh your_username@192.168.1.105   # verify no password prompt
```

---

### Step 4 — Create the Docker context on your dev machine

```bash
# Create context pointing to the VM
docker context create orderflow-vm --docker "host=ssh://your_username@192.168.1.105"

# Switch to it
docker context use orderflow-vm

# Verify — this runs on the VM
docker ps
```

---

### Step 5 — Start services

From your project root on the dev machine:

```bash
docker compose up -d
docker compose ps
```

All commands now execute transparently on the VM.

---

### VirtualBox network mode

For SSH and port access to work, the VM network adapter must **not** be in NAT mode.

| Mode | SSH from host? | Recommended |
|---|---|---|
| NAT (default) | ❌ Requires port forwarding | No |
| Bridged Adapter | ✅ Yes | ✅ Best for dev |
| Host-only | ✅ Yes | OK |

**To switch to Bridged in VirtualBox:**
1. Select VM → Settings → Network → Adapter 1
2. Change "Attached to" → **Bridged Adapter**
3. Select your active network interface (WiFi or Ethernet)
4. Click OK, reboot the VM, run `hostname -I` again to get the new IP

---

### Step 6 — Switching contexts

```bash
docker context ls                    # see all contexts (* = active)
docker context use orderflow-vm      # use VM
docker context use default           # use local Docker
```

---

### .env for VM-hosted Docker

Replace `192.168.1.105` with your actual VM IP:

```
DATABASE_URL=postgresql+asyncpg://orderflow:orderflow@192.168.1.105:5432/orderflow
REDIS_URL=redis://192.168.1.105:6379
LOG_LEVEL=INFO
```

> **VM IP changed?** Router DHCP can reassign the IP after a reboot. To fix permanently either:
> - Assign a static IP in your router (reserve the VM's MAC address)
> - Or set a static IP on the VM via `/etc/netplan/00-installer-config.yaml`

---

## Setup C — No Docker at all (native PostgreSQL + Redis)

Use this if you cannot run Docker at all and prefer native services.

### Install PostgreSQL 15 (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install postgresql-15 -y
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create user and database
sudo -u postgres psql -c "CREATE USER orderflow WITH PASSWORD 'orderflow';"
sudo -u postgres psql -c "CREATE DATABASE orderflow OWNER orderflow;"
```

### Install PostgreSQL 15 (macOS)
```bash
brew install postgresql@15
brew services start postgresql@15

createuser -s orderflow
createdb -O orderflow orderflow
psql -U orderflow -d orderflow -c "ALTER USER orderflow WITH PASSWORD 'orderflow';"
```

### Install Redis 7 (Ubuntu/Debian)
```bash
sudo apt install redis-server -y
sudo systemctl start redis
sudo systemctl enable redis

# Verify
redis-cli ping   # PONG
```

### Install Redis 7 (macOS)
```bash
brew install redis
brew services start redis
redis-cli ping   # PONG
```

### .env for native services
```
DATABASE_URL=postgresql+asyncpg://orderflow:orderflow@localhost:5432/orderflow
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
```

---

## Environment Variables

Full `.env` reference:

```
# Database
DATABASE_URL=postgresql+asyncpg://orderflow:orderflow@<host>:5432/orderflow

# Redis
REDIS_URL=redis://<host>:6379

# App
LOG_LEVEL=INFO                  # DEBUG | INFO | WARNING | ERROR
SECRET_KEY=your-secret-key-here # Used for JWT signing — change in production
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7
```

Replace `<host>` with:
- `localhost` — local Docker or native services (Setups A and C)
- `192.168.1.105` — VM-hosted Docker (Setup B) — use your actual VM IP

---

## Common Commands

```bash
# Start all services (detached)
docker compose up -d

# Stop all services
docker compose down

# Stop and wipe all data (destructive — deletes postgres_data volume)
docker compose down -v

# View logs
docker compose logs db        # PostgreSQL logs
docker compose logs redis     # Redis logs
docker compose logs -f db     # Follow logs in real time

# Open a PostgreSQL shell
docker compose exec db psql -U orderflow -d orderflow

# Open a Redis shell
docker compose exec redis redis-cli

# Check container resource usage
docker stats

# Restart a single service
docker compose restart db
docker compose restart redis
```

---

## Troubleshooting

### `docker compose up -d` → `unknown shorthand flag: 'd' in -d`
Docker Compose v1 is installed. Either upgrade to v2:
```bash
sudo apt install docker-compose-plugin -y   # Linux VM
```
Or use the v1 syntax as a temporary workaround:
```bash
docker-compose up -d
```

### Port 5432 already in use
A local PostgreSQL instance is running on the same port.
```bash
# Find and stop it
sudo lsof -i :5432
sudo systemctl stop postgresql
```
Or change the host port in `docker-compose.yml` to `5433`:
```yaml
ports:
  - "5433:5432"
```
Then update `DATABASE_URL` to use port `5433`.

### `docker ps` returns permission denied (Linux)
Your user is not in the docker group yet:
```bash
sudo usermod -aG docker $USER
newgrp docker
```

### SSH connection refused when using Docker context
1. Verify SSH server is running on the VM: `sudo systemctl status ssh`
2. Verify VM is on Bridged or Host-only network (not NAT)
3. Verify you can SSH manually: `ssh your_username@VM_IP`
4. Verify passwordless auth works (SSH key copied)

### VM IP changed after reboot
```bash
# On the VM, get the new IP
hostname -I | awk '{print $1}'

# Update the Docker context on your dev machine
docker context rm orderflow-vm
docker context create orderflow-vm --docker "host=ssh://your_username@NEW_IP"
docker context use orderflow-vm

# Update .env with the new IP
```

### `docker compose` not found on Windows
The Compose plugin is separate from the CLI binary. Download it manually:
```powershell
curl.exe -L -o "C:\docker-cli\docker-compose.exe" "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-windows-x86_64.exe"
```

---

*Last updated: March 2026 — OrderFlow Backend v1*
