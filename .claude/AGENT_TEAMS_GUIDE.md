# Agent Teams — Master Reference Guide

Source: https://code.claude.com/docs/en/agent-teams.md (Claude Code docs, as of v2.1.178+)

> **Status in this project:** Enabled locally via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=true` in `.claude/settings.local.json` (personal, gitignored — each teammate must enable it themselves to use the feature).

---

## Table of Contents

1. [What agent teams are](#what-agent-teams-are)
2. [Agent teams vs. subagents](#agent-teams-vs-subagents)
3. [Enabling the feature](#enabling-the-feature)
4. [Starting your first team](#starting-your-first-team)
5. [Controlling a team](#controlling-a-team)
6. [How it works under the hood](#how-it-works-under-the-hood)
7. [Use case examples](#use-case-examples)
8. [Best practices](#best-practices)
9. [Troubleshooting](#troubleshooting)
10. [Known limitations](#known-limitations)
11. [Related features](#related-features)

---

## What agent teams are

Agent teams coordinate **multiple independent Claude Code sessions** working together on one problem:

- One session is the **team lead** — it coordinates work, assigns tasks, and synthesizes results.
- **Teammates** work independently, each with its own context window, and can message each other directly (not just report back to the lead).
- You can talk to any teammate directly, not only through the lead.

⚠️ **Experimental and disabled by default.** Without the env var, no team is created, no team directories are written, and Claude never proposes or spawns teammates.

---

## Agent teams vs. subagents

| | Subagents | Agent teams |
|---|---|---|
| **Context** | Own context window; result returns to caller | Own context window; fully independent |
| **Communication** | Report back to the main agent only | Teammates message each other directly |
| **Coordination** | Main agent manages all work | Shared task list, self-coordinating |
| **Best for** | Focused tasks where only the result matters | Complex work needing discussion/collaboration |
| **Token cost** | Lower — summarized back to main context | Higher — each teammate is a full Claude instance |

**Rule of thumb:** use subagents for quick, focused workers that report back; use agent teams when workers need to share findings, challenge each other, and coordinate on their own.

---

## Enabling the feature

Set the environment variable to `1` (or `"true"`), either in your shell or in `settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

As of v2.1.178, spawning a teammate needs **no separate setup step** — just enable the flag and ask. (Before that version, you had to explicitly create/name a team via now-removed `TeamCreate`/`TeamDelete` tools.)

---

## Starting your first team

Describe the task and the roles you want, in plain language:

> "I'm designing a CLI tool that helps developers track TODO comments across their codebase. Spawn three teammates to explore this from different angles: one on UX, one on technical architecture, one playing devil's advocate."

This works well because the three roles are independent and don't block on each other. Claude will:

1. Populate a shared task list
2. Spawn a teammate per perspective
3. Have them explore in parallel
4. Synthesize findings when done

**Agent panel** (below the prompt input, in the lead's terminal):
- **↑ / ↓** — select a teammate
- **Enter** — open that teammate's transcript / message it directly
- **Esc** — interrupt its current turn

Idle teammates stay visible while anyone in the panel is still working; once everyone is idle, idle rows hide after 30s (teammate keeps running, addressable by name). More than 3 idle teammates collapse into one `N idle agents` row — Enter to expand.

---

## Controlling a team

### Display modes

| Mode | Description | Requirements |
|---|---|---|
| `in-process` (default) | All teammates run in your main terminal; select via agent panel | None |
| `auto` | Split panes when already in tmux, or iTerm2 + `it2` CLI; else falls back to in-process | tmux or iTerm2 |
| `tmux` | Split-pane mode, auto-detects tmux/iTerm2 | tmux or iTerm2 |
| `iterm2` (v2.1.186+) | iTerm2 native split panes explicitly | [`it2` CLI](https://github.com/mkusaka/it2) |

Set persistently:
```json
{ "teammateMode": "auto" }
```
Or per-session:
```bash
claude --teammate-mode auto
```

### Specify teammates & models

> "Spawn 4 teammates to refactor these modules in parallel. Use Sonnet for each teammate."

Teammates do **not** inherit the lead's `/model` by default — set **Default teammate model** in `/config` (or choose "Default (leader's model)" to follow the lead). Teammates do inherit the lead's **effort level**.

### Require plan approval

> "Spawn an architect teammate to refactor the authentication module. Require plan approval before they make any changes."

The teammate plans in read-only mode, submits to the lead for approval, and only implements once approved. The lead approves/rejects autonomously — give it explicit criteria in your prompt if you want to steer its judgment (e.g., "only approve plans that include test coverage").

### Talk to teammates directly

- **In-process:** ↑/↓ to select, Enter to view/message, `x` to stop, Ctrl+T to toggle task list.
- **Split-pane:** click into the pane directly.

A teammate's model and fast mode are fixed at spawn — `/model` and `/fast` only affect the lead. `/effort` still applies to the viewed teammate (since it follows the lead's effort level).

### Task list

- States: **pending → in progress → completed**; tasks can depend on other tasks (blocked until dependencies complete).
- **Lead assigns** tasks explicitly, or **teammates self-claim** the next unblocked task after finishing one.
- Uses file locking to prevent race conditions on simultaneous claims.

### Shutting down teammates

> "Ask the researcher teammate to shut down"

The lead sends a shutdown request; the teammate can accept (exits gracefully) or reject with a reason. Team directories clean up automatically when the session ends — no manual cleanup step.

### Quality gates via hooks

| Hook | Fires when | Exit 2 effect |
|---|---|---|
| `TeammateIdle` | Teammate about to go idle | Send feedback, keep it working |
| `TaskCreated` | Task being created | Prevent creation, send feedback |
| `TaskCompleted` | Task being marked complete | Prevent completion, send feedback |

---

## How it works under the hood

### Team formation
A team forms the moment the first teammate spawns; the main session becomes the lead. Either **you ask** for teammates, or **Claude proposes** them (always requires your confirmation).

### Architecture

| Component | Role |
|---|---|
| Team lead | Main session; spawns teammates, coordinates work |
| Teammates | Separate Claude Code instances working assigned tasks |
| Task list | Shared work items teammates claim/complete |
| Mailbox | Inter-agent messaging system |

- Mailbox file: `~/.claude/teams/{team-name}/inboxes/{agent-name}.json` (malformed entries are dropped with an error; valid ones still deliver — fixed a stuck-mailbox bug from before v2.1.207).
- Team name = `session-` + first 8 chars of session ID.
- **Team config:** `~/.claude/teams/{team-name}/config.json` — removed when session ends. Don't hand-edit; it's overwritten on every state update.
- **Task list:** `~/.claude/tasks/{team-name}/` — persists locally (never uploaded), so resumed sessions keep tasks. Retention follows `cleanupPeriodDays`.
- No project-level team config equivalent — a `.claude/teams/teams.json` in your repo is just an ordinary file, not recognized configuration.

### Reusable roles via subagent definitions

> "Spawn a teammate using the security-reviewer agent type to audit the auth module."

- Honors that subagent's `tools` allowlist and `model`; its body is **appended** to the teammate's system prompt (not a replacement).
- `SendMessage` and task-management tools are always available regardless of the `tools` restriction.
- **Not applied:** the subagent definition's `skills` and `mcpServers` frontmatter — teammates load skills/MCP servers from your project/user settings like a normal session.

### Permissions

- Teammates start with the **lead's permission settings** (e.g., `--dangerously-skip-permissions` propagates to all teammates). Per-teammate mode can be changed after spawn, not at spawn time.
- A teammate cannot approve permission prompts or supply consent on your behalf; a denied action can't be relayed through another teammate to bypass the check. Auto mode's classifier treats a relayed "approval" claim from another agent as **untrusted input**.
- Teammate permission prompts surface in the **lead session** — approve there. Plan approval is the one exception where the lead itself grants without pinging you.

### Context & communication

- Each teammate gets fresh project context at spawn (CLAUDE.md, MCP servers, skills) + the lead's spawn prompt — **not** the lead's conversation history.
- Messages deliver automatically; no polling needed.
- A teammate that finishes/stops notifies the lead automatically (as of v2.1.198, a turn that ends on an API error reports as a failure with the error text, not a silent normal finish).
- To reach everyone, send one message per recipient by name — names are assigned by the lead at spawn (tell it what names to use if you want predictable references later).

### Token usage

Scales with number of active teammates — each is a full separate context window. Worthwhile for research/review/new-feature work; a single session is more cost-effective for routine tasks.

---

## Use case examples

### Parallel code review
```
Spawn three teammates to review PR #142:
- One focused on security implications
- One checking performance impact
- One validating test coverage
Have them each review and report findings.
```
Each teammate applies a different lens to the same PR; the lead synthesizes all three afterward.

### Competing-hypothesis debugging
```
Users report the app exits after one message instead of staying connected.
Spawn 5 agent teammates to investigate different hypotheses. Have them talk to
each other to try to disprove each other's theories, like a scientific
debate. Update the findings doc with whatever consensus emerges.
```
The adversarial structure counters anchoring bias — a theory that survives active attempts at disproof is more likely the real root cause than one from sequential investigation.

---

## Best practices

1. **Give teammates enough context.** They don't inherit the lead's conversation history — spell out task-specific details in the spawn prompt (file paths, relevant constraints, what "done" looks like).
2. **Right-size the team.** Start with **3–5 teammates** for most workflows. Token cost scales linearly, coordination overhead grows, and returns diminish beyond a point. Aim for **5–6 tasks per teammate** (e.g., 15 independent tasks → 3 teammates).
3. **Right-size tasks.** Too small → coordination overhead dominates. Too large → teammates go too long without check-ins. Aim for self-contained units with a clear deliverable (a function, a test file, a review).
4. **Make the lead wait**, if it starts doing the work itself instead of delegating:
   > "Wait for your teammates to complete their tasks before proceeding"
5. **Start with research/review**, not parallel implementation — lower coordination risk while you learn the feature.
6. **Avoid file conflicts** — assign each teammate a distinct set of files.
7. **Monitor and steer** — don't let a team run unattended for long stretches.

---

## Troubleshooting

| Symptom | Fix |
|---|---|
| Teammates not appearing | Check agent panel (↑/↓, Enter); a hidden idle row isn't stopped — message it by name to bring it back; confirm the task was complex enough for Claude to spawn a team; for split panes, verify `which tmux` or that `it2` + iTerm2 Python API is set up |
| Too many permission prompts | Pre-approve common operations in permission settings before spawning |
| Teammate stops on error | Select it in the panel (Enter) or click its pane; give it more instructions, or spawn a replacement. As of v2.1.198, a message wakes a teammate waiting to retry a failed API call immediately |
| Lead shuts down too early | Tell it to keep going / wait for teammates before proceeding |
| Orphaned tmux sessions | `tmux ls` then `tmux kill-session -t <session-name>` |

---

## Known limitations

- **No session resumption for in-process teammates** — `/resume`/`/rewind` don't restore them; tell the lead to respawn if it tries messaging a teammate that's gone.
- **Task status can lag** — teammates sometimes fail to mark tasks complete, blocking dependents; check manually or nudge the lead.
- **Shutdown can be slow** — teammates finish their current turn/tool call first.
- **One team per session**, scoped to that session only.
- **No nested teams** — only the lead manages the team; teammates can't spawn their own teammates.
- **No background subagents from in-process teammates** — a teammate's own subagents run in the foreground only (background subagent work can't outlive the lead's process).
- **Lead is fixed** for the session's lifetime — no promoting a teammate or transferring leadership.
- **Permissions fixed at spawn** — per-teammate mode changes only apply after spawn.
- **Split panes need tmux or iTerm2** — not supported in VS Code's integrated terminal, Windows Terminal, or Ghostty (in-process mode works everywhere).
- ✅ `CLAUDE.md` works normally — teammates read it from their working directory, so it's a reliable way to brief the whole team.

---

## Related features

- **Subagents** — lightweight, in-session delegation for tasks that don't need inter-agent coordination.
- **Git worktrees** — manual parallel sessions without automated team coordination.
- See the Claude Code docs' subagent-vs-agent-team comparison for a full side-by-side.
