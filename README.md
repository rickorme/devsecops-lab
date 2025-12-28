[![Automated Testing Workflow](https://github.com/rickorme/devsecops-lab/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/rickorme/devsecops-lab/actions/workflows/ci-tests.yml)

# Project description
Lab project for DevSecOps course: this is a full-stack DevSecOps Lab demonstrating a secure social media architecture. It features a high-performance FastAPI backend with asynchronous SQLModel integration, a reactive Streamlit frontend, and a robust automated pipeline that handles unit testing with Pytest, API integration tests via Newman, end-to-end UI testing with Playwright, security auditing via pip-audit, and Static Application Security Testing (SAST) via CodeQL. 

## 🛠️ Development Environment

This project is built using **Visual Studio Code Dev Containers**. This ensures that everyone working on the project uses the exact same OS, tools, and dependencies (Python, Node.js, Playwright browsers, etc.) without needing to install them manually on their local machine.

### Prerequisites

Before you begin, ensure you have the following installed:

1.  **Container Runtime** (Choose one):
    * [**Docker Desktop**](https://www.docker.com/products/docker-desktop/)
    * [**Rancher Desktop**](https://rancherdesktop.io/) (Ensure `dockerd` (moby) is selected in Kubernetes Settings if using this)
2.  [**Visual Studio Code**](https://code.visualstudio.com/)
3.  **Dev Containers Extension** for VS Code (id: `ms-vscode-remote.remote-containers`)

### 🚀 Quick Start

1.  **Clone the repository**:
    ```bash
    git clone [https://github.com/rickorme/devsecops-lab.git](https://github.com/rickorme/devsecops-lab.git)
    cd devsecops-lab
    ```

2.  **Open in VS Code**:
    Open the folder in Visual Studio Code. You should see a notification in the bottom right corner saying *"Folder contains a Dev Container configuration file. Reopen to develop in a container."*

3.  **Click "Reopen in Container"**:
    * If you miss the notification, press `F1` (or `Ctrl+Shift+P`), type **"Dev Containers: Reopen in Container"**, and hit Enter.

4.  **Wait for the Build**:
    VS Code will build the Docker image and install all dependencies.
    * *Note: The first time you run this, it may take a few minutes to download the Python and Playwright images.*

Once the terminal opens, you are ready to go! All tools (`make`, `pytest`, `newman`, `playwright`) are pre-installed and configured.

---

### 💡 Why use this?
* **Zero "Works on my machine" issues:** The environment is identical for every developer and the CI pipeline.
* **Isolated Database:** Includes a pre-configured configuration for running tests against in-memory databases.
* **Visual Testing:** Includes a virtual desktop (Fluxbox) accessible via browser for watching Playwright tests run in real-time.

# Instructions for running the backend and opening API documentation
make install
make run
URL: http://localhost:8000/docs

# Instructions for running the full app locally
make install
make run
make run-frontend
URL: http://localhost:8501/

# Instructions for running tests
make test-unit
make test-api
make test-e2e

# Instructions for security audit
make audit

# Link to security analysis document
SECURITY-ANAlYSIS.MD

