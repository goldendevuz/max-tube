# CLAUDE.md

> **How to use:** Run the bootstrap prompt below once when starting a new project. It auto-fills sections 1–6. The agent guidelines at the bottom are permanent — never remove or summarize them.

---

## Project Bootstrap Prompt
> Run this once. Delete this block after the sections are filled in.

```
Analyze the entire project — folder structure, technologies, key files, and how they connect.
Fill in the CLAUDE.md at the project root with:

1. What the project does (2–3 sentences)
2. Full tech stack: languages, frameworks, database, hosting, external APIs
3. Folder structure — only the meaningful parts, with a one-line description each
4. Environment variables required to run the project
5. How to run it: install, dev server, build, deploy, background processes
6. Code conventions you observe: naming, file organization, state management
7. Important gotchas — fragile areas, things NOT to touch carelessly, known quirks

Write concisely. This file is the agent's reference — it shouldn't need to re-explore the project each session.
```

---

## 1. Project Summary

<!-- What this project does in 2–3 sentences. Who uses it and why. -->

_[Fill in after bootstrap]_

---

## 2. Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | |
| Framework | |
| Styling | |
| Database | |
| Auth | |
| Hosting | |
| External APIs | |

---

## 3. Folder Structure

<!-- Only folders that matter. Skip node_modules, .git, boilerplate. -->

```
/
├── ...    # [what it does]
├── ...    # [what it does]
└── ...    # [what it does]
```

---

## 4. Environment Variables

<!-- List all required .env keys. Never put actual values here. -->

```bash
# Required
KEY_NAME=          # what it's for

# Optional
OPTIONAL_KEY=      # what it does, default behavior if missing
```

---

## 5. Running the Project

```bash
# Install
npm install          # or pip install -r requirements.txt

# Development
npm run dev

# Build / production
npm run build
npm start

# Background processes (if any)
# e.g. python bot.py > bot.log 2>&1 &

# Deploy
# e.g. railway up --detach
```

---

## 6. Conventions & Patterns

<!-- Naming rules, file organization, state management, API patterns, etc. -->

_[Fill in after bootstrap]_

---

## 7. Important Notes

<!-- Gotchas, fragile areas, things NOT to change without care. -->

_[Fill in after bootstrap]_

---

## Keeping This File Current

Update CLAUDE.md when something **structurally meaningful** changes:
- New feature area or major dependency added
- Folder structure or naming convention changed
- New required environment variable
- Deployment process changed

**Do NOT update for:** bug fixes, style changes, copy tweaks, or anything that wouldn't matter to someone reading the project for the first time.

---

## Working in Parallel

When making **independent** changes across multiple files, launch all Agent tool calls in a **single message** so they run concurrently. Do not serialize work that can be parallelized — one agent per independent change, all dispatched at once.

---

## Pre-Push Sync Check (MANDATORY — runs BEFORE any commit/push/deploy)

<!-- Fill in team size. If solo project, remove this section. -->

Multiple developers may push to `main` between sessions. Local can fall behind silently. Claude must always sync with origin BEFORE any commit/push/deploy workflow — otherwise local work overwrites teammates' commits or push gets rejected and Claude force-resolves it the wrong way.

### Sequence (run in order, always)

**1. Refresh remote refs without merging:**
```bash
git fetch origin --prune
```

**2. Check if local is behind origin:**
```bash
git log HEAD..origin/main --oneline
git diff HEAD origin/main --stat
```

**3. If step 2 prints NOTHING** → local is current. Proceed to push.

**4. If step 2 prints any commits** → STOP. Do this:
- Print the commit list to the user verbatim ("origin/main has these N new commits from teammates: …").
- If there are uncommitted local changes:
  - Move them to a feature branch first: `git checkout -b sync-<timestamp>`, then `git add <specific files>`, then `git commit -m "WIP"`. **NEVER `git add -A`.**
- Rebase local onto origin/main:
  ```bash
  git pull --rebase origin main
  ```
- If rebase succeeds clean → proceed to push.
- If rebase produces conflicts → **STOP.** List each conflicted file. Ask the user how to resolve. **NEVER auto-pick "ours" or "theirs" without explicit instruction.**

**5. After conflict resolution**, verify the merged tree compiles before pushing:
```bash
npm run build   # or equivalent for this project
```

### Hard rules

- **NEVER `git push --force` or `--force-with-lease` to `main`/`master`.** If push is rejected, re-fetch and re-rebase — never force.
- **NEVER `git reset --hard origin/main` while uncommitted changes exist.** That deletes the user's work.
- **NEVER `git checkout .` or `git restore .`** to "clean up" — same risk.
- **NEVER rebase or merge silently when conflicts exist.** Resolution requires the user's input.
- **When in doubt, stop and ask.** A 30-second clarification beats a force-push that loses an hour of someone else's work.

### When this runs

- **Triggers on:** `deploy`, `push`, `merge to main`, `ship`, `git-shipper` agent invocation, `deployer` agent invocation, any prompt mentioning push-to-production.
- **Skipped only when:** the user explicitly says "skip sync check" or "just push, I already pulled".

---

## Model & Impact Routing

Before executing, declare in **one line** at the top of your reply:
> 🤖 `<haiku|sonnet|opus>` · 🎯 `<🟢low | 🟡med | 🔴high>` · ⚙️ `<one-line reason>`

**Model selection (cheapest tier that fits):**

| Use | For |
|-----|-----|
| **haiku** | Reads, greps, status checks, deploys, git workflows, env edits, find/replace, "continue"/"go" signals |
| **sonnet** | Code generation, debugging, multi-file features, refactors, plan decomposition |
| **opus** | Cross-system architecture, novel design, security-critical tradeoffs (rare) |

Rule: when unsure, use the cheaper tier. Escalate only if it struggles.

**Impact level (state blast radius for 🔴):**

| Tag | Means | Examples |
|-----|-------|----------|
| 🟢 low | Read-only / trivially undone | Read, Grep, status, Q&A |
| 🟡 med | Single-file / local config | Bug fix, doc edit, env var |
| 🔴 high | Multi-file / prod / irreversible | Deploy, merge to main, delete, secret rotation, 3+ files |

For 🔴 tasks: **list affected files/services before acting.**

---

## Behavioral Guidelines

These rules reduce common LLM coding mistakes. They bias toward caution — use judgment on trivial tasks.

### 1. Think Before Coding

**Don't assume. Surface tradeoffs. Ask when unclear.**

- State your assumptions explicitly before implementing.
- If multiple interpretations exist, name them — don't pick silently.
- If a simpler approach exists, say so and push back.
- If something is genuinely unclear, stop and ask. Don't guess.

### 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "extensibility" that wasn't requested.
- No error handling for scenarios that can't happen.
- If you wrote 200 lines and it could be 50, rewrite it.

> Ask: "Would a senior engineer call this overcomplicated?" If yes — simplify.

### 3. Surgical Changes

**Touch only what you must.**

When editing existing code:
- Don't improve adjacent code, comments, or formatting unless asked.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you spot unrelated dead code, mention it — don't delete it.

When your changes create orphans:
- Remove imports, variables, and functions that **your** changes made unused.
- Don't remove pre-existing dead code unless explicitly asked.

> Test: every changed line should trace directly to the user's request.

### 4. Verify Before Reporting Done

**Define success criteria upfront. Loop until verified.**

For multi-step tasks, state a brief plan first:
```
1. [What] → verify: [how to confirm it worked]
2. [What] → verify: [how to confirm it worked]
3. [What] → verify: [how to confirm it worked]
```

Run the check before saying "done." If you can't verify (e.g. needs a browser), say so explicitly and describe what the user should check.

---

**These guidelines are working when:** diffs are clean, rewrites are rare, and questions come before implementation — not after.
