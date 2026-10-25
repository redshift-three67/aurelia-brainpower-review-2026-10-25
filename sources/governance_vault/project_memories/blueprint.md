# Hermes Agent — Architecture Blueprint

Comprehensive overview of the Hermes Agent codebase architecture, core design principles, runtime flow, subsystem topology, and storage layers.

---

## 1. System Invariants & Core Design Philosophy

Hermes Agent is built around two primary architectural invariants:

1. **Per-Conversation Prompt Caching is Sacred**
   - The prefix cache must remain valid across turns in long-running conversations.
   - Any mutation to past context, dynamic tool swapping, reloading memories, or rebuilding the system prompt mid-conversation breaks caching and multiplies LLM latency/token costs.
   - Operations that mutate state (e.g. installing skills, enabling tools) defer invalidation until the next session by default (or explicitly via `--now`).
   - Strict message role alternation (never two assistant or user messages adjacent) is enforced.

2. **The Core is a Narrow Waist; Capabilities Live at the Edges**
   - Every core tool model schema is transmitted on every LLM API call.
   - The Footprint Ladder guides capability additions:
     1. Extend existing modules (zero schema footprint).
     2. CLI command + Skill pattern.
     3. Service-gated tool (`check_fn` activated only when prerequisites exist).
     4. Dynamic Plugins (`~/.hermes/plugins/` or pip entry points).
     5. MCP (Model Context Protocol) servers.
     6. Core tools (reserved for foundational, universal operations).

---

## 2. High-Level Directory & Component Topology

```
hermes-agent/
├── run_agent.py               # AIAgent loop facade; orchestrates turn phases
├── agent/                     # Core conversation loop, prompt assembly, compression, providers
│   ├── turn_*.py              # Modular loop phases (input, invoke, tool exec, finish)
│   ├── prompt_builder.py      # System prompt constructor & environment hints
│   ├── context_compressor.py  # Intelligent context truncation & compaction
│   └── memory/                # Memory providers & memory injection hooks
├── cli.py                     # HermesCLI REPL, prompt_toolkit UI, slash command dispatch
├── hermes_cli/                # Subcommands, config loaders, skin engine, update pipeline
│   ├── commands.py            # Canonical COMMAND_REGISTRY (source of truth)
│   ├── config.py              # Configuration parsing & defaults
│   └── web_routers/           # FastAPI backend routers for the dashboard
├── model_tools.py             # Built-in tool discovery & execution dispatch
├── toolsets.py                # Toolset definitions & _HERMES_CORE_TOOLS
├── tools/                     # Modular tool implementations
│   ├── registry.py            # Central tool registry with check_fn & caching
│   └── environments/          # Terminal backends (local, docker, ssh, modal, singularity)
├── gateway/                   # Multi-platform messaging gateway (Telegram, Discord, Slack, etc.)
│   ├── run.py                 # Gateway lifecycle, event loops, session routing
│   └── platforms/             # Adapter per messaging platform
├── tui_gateway/               # JSON-RPC server bridging agent core to TUI and Desktop UI
├── ui-tui/                    # Terminal UI built with React / Ink
├── apps/desktop/              # Electron desktop application
├── cron/                      # Durable job scheduler, intervals, and execution logs
├── plugins/                   # External provider plugins, specialized toolsets, and bridges
├── skills/                    # Bundled skill library organized by category
└── hermes_state*.py           # SQLite SessionDB facade & modular topic siblings
```

---

## 3. Structural Decomposition: Facade + Siblings Pattern

To maintain modularity and avoid monolithic files, major components are structured as a public **facade** supported by topic-specific **sibling modules**:

### A. State Storage (`hermes_state.py` & siblings)
- `hermes_state.py`: Primary interface for session metadata, message history, and search.
- `hermes_state_schema.py`: Database schema definitions, migrations, and index maintenance.
- `hermes_state_sessions.py`: Session CRUD and lifecycle management.
- `hermes_state_messages.py`: Message append, retrieval, token counting, and role alternation checks.
- `hermes_state_fts.py` / `hermes_state_search.py`: Full-text search (SQLite FTS5) across past exchanges.
- `hermes_state_compression.py`: Compaction checkpoints and snapshot history.
- `hermes_state_wal.py` / `hermes_state_repair.py`: WAL management, integrity validation, and recovery.

### B. Agent Turn Loop (`agent/turn_*.py`)
- `run_agent.py` acts as the facade for `AIAgent`.
- Turn phases are partitioned across `agent/turn_prepare.py`, `agent/turn_invoke.py`, `agent/turn_dispatch.py`, and `agent/turn_finish.py`.
- Enforces tool-use constraints, manages mid-turn user steering injections, and manages context compaction triggers.

### C. CLI & Slash Command Dispatch (`hermes_cli/`)
- `hermes_cli/commands.py` defines the immutable `COMMAND_REGISTRY`.
- Features mixins on `HermesCLI` (`cli_commands_mixin.py`, `cli_stream_mixin.py`, `cli_status_bar_mixin.py`).
- All slash commands resolve to deterministic handlers without conditional branching ladders.

---

## 4. Execution Flow & Runtime Lifecycle

```
[User Input / Gateway Event / Cron Trigger]
                     │
                     ▼
             [Command Resolution]
       ┌─────────────┴─────────────┐
 [Slash Command (/...)]     [Standard Message]
       │                           │
       ▼                           ▼
[Execute CLI/Gateway Action]   [AIAgent.run_turn()]
                                   │
                                   ├─► 1. Assemble context & prompt (preserve cache)
                                   ├─► 2. Check token budget & run compaction if needed
                                   ├─► 3. Call LLM provider (streaming API)
                                   ├─► 4. If Tool Call:
                                   │     ├── Check permissions / check_fn
                                   │     ├── Execute tool in configured environment
                                   │     └── Loop back with tool result
                                   └─► 5. Persist turn to SQLite state.db
```

---

## 5. Storage & Configuration Topology

- **Configuration:** `~/.hermes/config.yaml` (profile-aware via `get_hermes_home()`). Controls agent settings, providers, model parameters, and tool enablement.
- **Secrets & Credentials:** `~/.hermes/.env` (secrets only).
- **Session DB:** `~/.hermes/state.db` (SQLite + WAL mode + FTS5 search).
- **Installed Skills:** `~/.hermes/skills/` (dynamically loaded per session).
- **Logs:** `~/.hermes/logs/agent.log` and `~/.hermes/logs/gateway.log`.
- **Profiles:** Isolated under `~/.hermes/profiles/<name>/` with distinct state, skills, and configuration.

---

## 6. Desktop Toolchain & Dependency Status

The Electron desktop client is located in `apps/desktop/`. Its current development-toolchain versions are locked through the root `package-lock.json`:

- **Electron:** `41.10.3`
- **Vitest:** `4.1.11`
- **js-yaml:** `4.3.2` (root override)

`package-lock.json` is the canonical resolved dependency graph for the workspaces and deduplicates redundant workspace-local Vitest resolutions.
