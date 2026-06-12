# Neural SOC Analyst Dashboard

A cybersecurity automation dashboard that leverages AI and threat intelligence engines to analyze domains, hashes, and network logs for potential vulnerabilities.

##Features
- **AI-Powered Threat Analysis:** Integrates with the **Groq LLM Engine** to provide human-readable risk explanations and remediation suggestions.
- **Threat Intel Integrations:** Built-in hooks for scanning artifacts against the **VirusTotal API**.
- **Automated Reporting:** Generates downloadable, dynamic executive summaries in PDF format using **ReportLab**.
- **Dockerized Architecture:** Fully containerized backend and service layers for easy, reliable deployment.

## Tech Stack
- **Front-end:** HTML5, CSS3 (Custom Cyberpunk UI), JavaScript
- **Back-end framework:** Flask (Python)
- **AI & Workflow Automation:** Groq LLM API, n8n automation pipelines
- **Infrastructure & Tools:** Docker, Docker Compose, VirusTotal API, ReportLab

---

## Installation & Setup

### Prerequisites
Make sure you have [Docker & Docker Compose](https://docker.com) installed on your machine.

### 1. Clone the Repository
```bash
git clone https://github.com
cd neural-soc-analyst
```

### 2. Set Up Environment Variables
Create a file named `.env` in the root folder and add your specific API tokens:
```ini
GROQ_API_KEY=your_groq_api_key_here
VIRUSTOTAL_API_KEY=your_virustotal_api_key_here
```

### 3. Build and Run via Docker
Launch the entire infrastructure with a single command:
```bash
docker-compose up --build
```
Once initialized, open your browser and navigate to `http://localhost:5000` to view the running security dashboard.

---

## Interface Preview
<img width="1862" height="882" alt="Screenshot 2026-05-19 132722" src="https://github.com/user-attachments/assets/12701af2-0ba4-44b6-a324-d55a64f0a3d9" />

---

## University Project Context
This project was developed as a university assignment to demonstrate practical AI integration in cybersecurity triage workflows, microservices architectures, and asynchronous data processing.
