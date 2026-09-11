# 🌌 Hubscape Agent Development Shell

Welcome to the official **Hubscape Agent Development Template**. This repository serves as a lightweight, sandboxed environment for designing, testing, and developing custom agents for the Hubscape platform using skeleton templates.

---

## 🚀 Getting Started (Zero-Config Connection)

### 1. Install the Hubscape ADK CLI
Make sure you have Python 3.10+ and `pipx` installed. If you do not have `pipx`, install it and configure your global path:
*   **macOS (Homebrew):** `brew install pipx && pipx ensurepath`
*   **Linux (APT):** `sudo apt update && sudo apt install pipx && pipx ensurepath`
*   **Windows:** `python -m pip install --user pipx && python -m pipx ensurepath`

*(Note: If you just installed `pipx`, close and restart your terminal to apply the path changes).*

Once `pipx` is ready, run the installation command:
```bash
pipx install git+https://github.com/Zco-AI-Labs/Hubscape-ADK-Studio.git
```
*(This command installs the global `hubscape-adk` CLI runner, along with the Holodeck frontend and database gateway dependencies).*

### 2. Bootstrap / Clone the Agent Repository
To clone this template repository directly into your active IDE workspace directory (or any empty folder), open your terminal and run:
```bash
hubscape-adk clone https://github.com/Zco-AI-Labs/your-agent-repo
```
*(If your active folder already contains editor workspaces or config files, the smart CLI will warn you and prompt for confirmation before executing a safe merge).*

### 3. Launch & Connect
From the root of your cloned repository, execute the runner command:
```bash
hubscape-adk
```
The Holodeck console will automatically open in your default browser at **http://localhost:8090**. 

> [!TIP]
> **Simulating Conversational Routing (Google Gemini API Key):**
> Local testing lets you talk to your agent through a simulated platform **Host AI** that dynamically routes query intents. To enable this conversational routing simulation locally:
> 1. Get a free API key from [Google AI Studio](https://aistudio.google.com/).
> 2. Paste the key directly in the **Holodeck Settings** panel in your browser, or add it to `.env` in the root of your agent folder as `GEMINI_API_KEY=your_gemini_api_key_here`.
> This enables the sandbox host to organically route user queries to your agent.

---

## 📂 Repository Structure

The Hubscape ingestion pipeline enforces the **Pure Agent Principle**, copying only the core files and ignoring all local database or environment configs. Organize your code using the structure below:

*   **`.agent/`**: Contains workspace configurations, rules, and custom AI skills that guide coding agents (e.g., ADK Expert, ADK Update Auditor).
*   **`pyproject.toml`**: Defines workspace project dependencies, dev groups, linters, and python configurations.
*   **`app/`**: Contains the core agent application logic and instructions.
    *   **`__init__.py`**: Entry-level package exposure.
    *   **`agent.py`**: Initializes the ADK Agent, sets up prompts, and registers tools dynamically.
    *   **`SKILL.md`**: Houses system instruction strings and capability descriptions.
    *   **`privileges.json`**: Specifies zero-trust role-based privilege mappings for tool execution.
    *   **`scripts/`**: Directory for custom standalone python tool scripts (filenames must match function names).
    *   **`ui/`**: Directory for custom layout files.
        *   **`widgets/`**: Houses custom JSON Lego UI widget templates (e.g. `contact_form.json`).
        *   **`sidekick/`**: Custom sidekick UI panels.
    *   **`core/`**: Central ADK integration, runtime application, and internal helper utilities.
        *   **`hubscape_adk.py`**: Platform context manager implementing database (`save`, `get`) and GCS scopes.
        *   **`agent_runtime_app.py`**: Local and production A2A executor server hosting the agent.
        *   **`geap_agent_wrapper.py`**: Integration layer executing the runner inside Vertex AI.
        *   **`system_tools/`**: Built-in system tools for subagent discovery (`discover_agents.py`, `consultAgent.py`).
*   **`tests/`**: Contains python test files, structured into `unit/` and `integration/` tests.
*   **`docs/`**: Comprehensive developer guides (Manuals, Workflows, UI Catalogs).

---

## 💡 Reference Implementations (Blueprints)

To keep this template clean and production-ready, it is configured with barebones skeleton files by default. If you are looking for a complete, functional reference agent to learn from, you can check out:

*   **Nova Agent:** [nova-agent](https://github.com/Zco-AI-Labs/nova-agent) — Demonstrates tools, database scopes, permissions, and generative dynamic UI rendering.

To test a blueprint, simply clone its repository and run `hubscape-adk` inside its root folder.

---

## 🛠️ Advanced / Manual Configuration (Optional)

If you prefer to configure your workspace manually before booting the sandbox:
1.  Copy the environment template:
    ```bash
    cp .env.example .env
    ```
2.  Open `.env` and configure your API key:
    ```env
    GEMINI_API_KEY=your_gemini_api_key_here
    ```

---

## 🤖 AI Assistant Support

If you open this repository using an AI-assisted IDE (like Cursor or VSCode with Gemini), the editor will automatically detect the custom rules and templates in the `.agent/` folder:
*   **ADK Expert**: Guides the AI to write correct tool schemas, layout widgets, and Python handlers.
*   **ADK Librarian**: Audits and updates documentation in `docs/` and `README.md` whenever core template files are modified.
*   **Agent Plan Creator**: Automatically structures your development checklist.
*   **Agent Tool Creator**: Helps implement secure, isolated, and correctly formatted custom tools.
*   **Agent UI Creator**: Guides the creation of custom dynamic JSON widget templates using Lego UI elements.
*   **GEAP Agent Expert**: Assists in building and packaging agents for Vertex AI Reasoning Engines (GEAP).
*   **Project Plan Archiver**: Safely archives current project plans to the documentation archive with versioning.
*   **Hubscape ADK Update Auditor**: Guides the update process of the `hubscape-adk` tool and audits incoming changes to infrastructure files for compatibility issues.

For detailed development lifecycle guides, please refer to:
*   [docs/Hubscape-ADK-Manual/CHAPTER_1_OVERVIEW.md](docs/Hubscape-ADK-Manual/CHAPTER_1_OVERVIEW.md) (Standard Onboarding SOP & Overview)
*   [docs/Hubscape-ADK-Manual/CHAPTER_9_GEAP_DEVELOPER_WORKFLOW.md](docs/Hubscape-ADK-Manual/CHAPTER_9_GEAP_DEVELOPER_WORKFLOW.md) (Advanced GEAP Developer Workflow)
*   [docs/Hubscape-ADK-Manual/CHAPTER_6_LEGO_WIDGETS_AND_IFRAMES.md](docs/Hubscape-ADK-Manual/CHAPTER_6_LEGO_WIDGETS_AND_IFRAMES.md) (Lego UI Element & Widget Reference)
