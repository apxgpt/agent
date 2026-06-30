# JINX Enterprise Agent System & Web Dashboard

An intelligent autonomous agent system **JINX** with an interactive web control dashboard for real-time visualization of the cognitive loop, logs, plan execution status, and architectural decisions.

---

## Project Directory Structure

When integrating into your working repository, the project directory layout should be structured as follows:

```text
Your_Project/
├── .agent/                    # JINX Agent Folder
│   ├── JINX.yaml              # Current agent state (automatically updated)
│   ├── jinx.py                # Main CLI entrypoint to run the agent
│   ├── jinx_run_state.yaml    # Active runtime status and dialogue/tool-call logs
│   ├── src/
│   │   └── jinx/              # Core logic and JINX modules
│   │
│   └── webagent/              # Web Visualization Dashboard (this web app)
│       ├── package.json       # Web app package scripts & dependencies
│       ├── server.ts          # Express + Vite backend server
│       ├── tsconfig.json
│       ├── vite.config.ts
│       ├── index.html
│       ├── src/               # React (TypeScript) client application
│       └── ...
```

---

## 1. Setting Up and Running the Python Agent (JINX)

### Prerequisites
* Python 3.10 or higher
* Installed package manager `pip`

### Initialization and Execution
Navigate to the root directory of your main repository (`Your_Project/`) and start the agent by passing the target task. On the first run, the bootstrap script will automatically install missing dependencies (`pydantic` and `pyyaml`):

```bash
python .agent/jinx.py "Create a custom user authentication system"
```

The agent will initialize its cognitive loop, perform development iterations, edit/write code files via tools, and persist its active progress to `.agent/JINX.yaml` and `.agent/jinx_run_state.yaml`.

---

## 2. Setting Up and Running the Web Dashboard (webagent)

The web dashboard is powered by **React + Express + Vite** to track the JINX agent's background activities, displaying interactive timelines, execution steps, terminal consoles, and source code diffs in real-time.

### Step 1: Navigate to the Web Agent directory
From the root of your main project, go to the webapp directory:
```bash
cd .agent/webagent
```

### Step 2: Install Node.js dependencies
Make sure Node.js (v18+ recommended) is installed. Install the project dependencies:
```bash
npm install
```

### Step 3: Run the Development Server (Vite HMR + Express)
Start the development server. This launches the Express backend and Vite client on port **3301**:
```bash
npm run dev
```
Open your browser and navigate to: **`http://localhost:3301`**

### Step 4: Build and Run in Production
To build the optimized client bundle and compile the server:
```bash
# Compile the project
npm run build

# Start the Production server
npm run start
```

---

## Core Dashboard Features

1. **Cognitive Loop**:
   Real-time monitoring of the active agent phases (Perceive, Plan, Execute, Verify), elapsed run-time, process PID, and system resources.
2. **Multi-Step Plan**:
   Interactive visualization of the plan checklist, test outcomes, and functional requirements passed for each optimization round.
3. **Workspace Insights (Facts, Debt, and Open)**:
   * **Scope Facts** — constraints and facts identified about the workspace.
   * **Open Requirements** — unresolved goals or task criteria.
   * **Design Debt** — technical trade-offs or temporary workarounds accepted.
4. **Terminal Console & RPC Log**:
   Full trace of LLM tool interactions (file reads/writes, bash commands) and standard output streamed in real-time.
5. **File Browser & Diff Viewer**:
   Explore source code files created or modified by the agent, highlighting live changes (`diff`) with side-by-side color indicators.
