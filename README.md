# N.S.A // NEURAL SOC ANALYST — GUIDE
**Project by:** T3MP3R3R  
**Stack:** Flask · Groq LLM · Docker · ReportLab · n8n · VirusTotal

---

## Project Status: Proof of Concept (PoC)
This repository hosts a functional Proof of Concept focused on interface design, core AI pipelines, and backend service orchestration. 

### What is Fully Functional
- **Flask Backend:** Handles server-side API routing and asset serving.
- **Groq LLM Pipeline:** Connects to the Llama model engine to parse and analyze threat prompts.
- **Dynamic PDF Generation:** Compiles and downloads structured SOC summaries using ReportLab.
- **Container Architecture:** Orchestrates deployment environments via Docker Compose.

### What is Simulated / In Development (UI Only)
- **THREAT_MAP Topology Display:** The visual node map graph is a styled static CSS mockup. It does not map real-world nodes live yet.
- **IOC_SCANNER & SOC_REPORTS Navigation Modules:** These menu links are visual placeholders in the frontend sidebar routing layer.

---

## STEP 0 — PREREQUISITES
*(Install once on any new PC)*

### Python
- **Download:** [python.org/downloads](https://python.org)
- **Version:** 3.10 or higher
- **Windows:** Check **"Add Python to PATH"** during installation.
- **Verify:** `python --version`

### Docker Desktop
- **Download:** [docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
- **Windows:** Enable **WSL2** when prompted.
- **After install:** Open Docker Desktop and wait for *"Engine running"* to appear in the bottom-left corner.
- **Verify:** `docker --version`

### Git *(Optional but recommended)*
- **Download:** [git-scm.com/install/](https://git-scm.com/install/)
- **Verify:** `git --version`

### API Keys
- **Groq API Key (Free):** Sign up at [://groq.com](https://console.groq.com/home), go to *API Keys -> Create API Key*.
- **VirusTotal API Key (Free):** Sign up at [virustotal.com](https://virustotal.com), go to your profile *-> API key*.

---

## STEP 1 — GET THE PROJECT

### Option A — Copy from USB / ZIP
Extract the project folder anywhere, for example:  
`C:\Users\YourName\Desktop\Neural-SOC-Analyst\`

### Option B — Clone from Git
```bash
git clone https://github.com/T3MP3R3R/Neural-SOC-Analyst.git
cd Neural-SOC-Analyst
```

---

## STEP 2 — CONFIGURE YOUR API KEYS

In the **PROJECT ROOT** folder, create a file called exactly: `.env`

Open it in Notepad and add your secret keys:
```ini
GROQ_API_KEY=your_actual_groq_key_here
VIRUSTOTAL_API_KEY=your_actual_virustotal_key_here
```

> ⚠️ **IMPORTANT:** Never share this file. Never upload it to GitHub. The `.gitignore` file is already configured to exclude it.

---

## STEP 3A — RUN LOCALLY
*(No Docker, fastest for development)*

Open a terminal (Command Prompt or PowerShell) and navigate to your project:
```bash
cd "C:\Users\YourName\Desktop\Neural-SOC-Analyst"
```

Install Python dependencies *(only needed once)*:
```bash
pip install -r requirements.txt
```

Start the backend:
```bash
cd backend
python app.py
```
Open your browser and navigate to: **[http://127.0.0.1:5000](http://127.0.0.1:5000)**  
*To stop the server, press `Ctrl+C` in your terminal.*

---

## STEP 3B — RUN WITH DOCKER
*(For clean, portable deployment)*

1. Make sure **Docker Desktop** is open and the engine is running.
2. Open a terminal from the **PROJECT ROOT** folder (not the backend folder):
```bash
cd "C:\Users\YourName\Desktop\Neural-SOC-Analyst"
```

Build and launch the container structure:
```bash
docker compose up --build
```
*(Note: The first run downloads the base Python environment (~200MB) and may take a moment. Subsequent launches are instant).*

Open your browser and navigate to: **[http://localhost:5000](http://localhost:5000)**

### Docker Management Commands
- **Stop containers:** Press `Ctrl+C` in the terminal, then clean up with `docker compose down`.
- **Run in background (Detached mode):** `docker compose up --build -d`
- **Stop background instances:** `docker compose down`

---

## STEP 4 — n8n AUTOMATION
*(Optional SOAR Workflow Integration)*

n8n is a workflow automation tool used here to auto-submit suspicious items, trigger alerts, schedule dynamic PDFs, or pipe intelligence feeds.

To include n8n, append this service configuration block directly under your `services:` section inside `docker-compose.yaml`:

```yaml
  n8n:
    image: n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=changeme
    volumes:
      - n8n_data:/home/node/.n8n
    restart: unless-stopped
```

Also, define the named volume at the very bottom of your `docker-compose.yaml`:
```yaml
volumes:
  n8n_data:
```

Rebuild your architecture to launch both components together:
```bash
docker compose up --build
```
- **n8n Dashboard:** [http://localhost:5678](http://localhost:5678)
- **NSA Dashboard:** [http://localhost:5000](http://localhost:5000)

### Example Automation Pipeline — "Alert on High Risk"
1. **Trigger:** Webhook node (receives email or log payload details).
2. **HTTP Request Node:** Send a `POST` network request out to `http://backend:5000/analyze`.
3. **IF Node:** Evaluate conditional filter mapping `analysis.risk_level == "High"`.
4. **Action Node:** Push a critical message event straight to an Email, Slack, or Discord webhook.

---

## STEP 5 — RUNNING UNIT TESTS
*(Optional Validation Suite)*

The project includes an automated test framework containing 42 unique validation checkpoints covering risk engines, VirusTotal lookup routines, Flask API routing edge cases, and ReportLab PDF compilation states.

To execute the full test suite using `pytest` from the **PROJECT ROOT** folder:
```bash
python -m pytest backend/tests/test_nsa.py -v
```

---

## QUICK REFERENCE — COMMON COMMANDS

| Action | Command |
| :--- | :--- |
| **Install Dependencies** | `pip install -r requirements.txt` |
| **Run Locally** | `cd backend && python app.py` |
| **Run Container Deployment** | `docker compose up --build` |
| **Run Containers in Background** | `docker compose up --build -d` |
| **Stop Active Container Instances** | `docker compose down` |
| **Tail Live Container Stream Logs**| `docker compose logs -f` |
| **Force Container Code Rebuild** | `docker compose up --build` |
| **View Active Docker Containers** | `docker ps` |

---

## FILE STRUCTURE REFERENCE

```text
project/
├── .env                  ← Local environment keys (never share or commit)
├── .gitignore            ← Excludes system configs, .env, and caches
├── requirements.txt      ← Explicit list of Python dependencies
├── Dockerfile            ← Image building definitions 
├── docker-compose.yaml   ← Orchestrates multiple software layers
├── README.md             ← Main user guide and installation document
├── LICENSE               ← MIT Open-Source legal usage agreement
├── CONTRIBUTING.md       ← Guidelines for open-source project collaboration
├── CHANGELOG.md          ← Chronological log of version updates and fixes
├── backend/
│   ├── app.py            ← Flask web app router & static asset server
│   ├── analyzer.py       ← Core Groq LLM workflow parser
│   ├── config.py         ← API keys and verification engine
│   ├── history.py        ← Read/write operations handler for files
│   ├── history.json      ← Persistent JSON file log of incidents
│   ├── report.py         ← Dynamic PDF generator via ReportLab
│   └── tests/            
│       └── test_nsa.py   ← 42 Unit tests validating backend logic
└── frontend/
    ├── index.html        ← HTML application skeletal layout
    └── static/           
         ├── style.css    ← Cyberpunk dark-themed style sheet
         └── script.js    ← State handling asynchronous AJAX controller
```

---

## TROUBLESHOOTING

- **`ModuleNotFoundError`**
  - Run `pip install -r requirements.txt` inside your terminal environment.
- **`GROQ_API_KEY is not set`**
  - Ensure your `.env` layout file resides exactly in your root path. Ensure no invalid spacing characters exist near assignments (e.g., `GROQ_API_KEY=yourkey`).
- **`Port 5000 already in use`**
  - You have conflicting backend services running simultaneously. Find and kill the active process identifier:
    - **Windows:** Run `netstat -ano | findstr :5000`, then terminate using `taskkill /PID <number> /F`.
- **`Docker: 500 Internal Server Error` / Connection Timeout**
  - Docker Desktop engine is offline. Open the interface app and verify the bottom left green status icon says *"Engine running"* before retrying.
- **`docker-compose: command not found`**
  - Legacy syntax. Drop the hyphen tool connection character and use modern formatting layout rules: `docker compose up --build`.
- **`Backend offline` in the visual UI**
  - Flask process instance dropped out. Initialize it using `cd backend && python app.py`.
- **`history.json` write access permission failure in Docker**
  - Manually create an initial blank array format on your device host by typing `echo [] > backend/history.json`.

---

## FUTURE INTEGRATIONS (ROADMAP)

- [ ] **Docker Sandbox:** Add safe runtime analysis for structural validation of unknown payload files.
- [ ] **PostgreSQL Target:** Migrate persistent telemetry from file objects to relational tracking databases.
- [ ] **Auth Layer:** Enforce individual user profiles protected behind signed JSON Web Tokens (JWT).
- [ ] **WebSocket Stream:** Implement bidirectional sockets to push real-time threat items dynamically.
- [ ] **MITRE ATT&CK Engine:** Correlate detected artifacts straight to global exploit frameworks.
- [ ] **Pydantic/Instructor Schema Validation Layer:** To enforce structured JSON outputs from Groq.
- [ ] **System Prompt Guardrail:** To sanitize input strings before passing them to the model context.
