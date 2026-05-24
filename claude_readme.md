# Working with Claude on this Project

## Why this repo exists

This project builds a home telemetry system on top of a TP-Link TCB72 camera — streaming video and events to a home PC and writing custom applications on top of that data, bypassing the Tapo app entirely.

The repo is also structured for a dual-machine Claude workflow: planning happens on a Windows desktop using the Cowork desktop app, implementation happens on a separate development machine using Claude Code CLI. `CLAUDE.md` is the shared context file that bridges both.

## How Claude is set up here

- **`CLAUDE.md`** — The primary project context file. It captures camera specs, confirmed connectivity details, architectural decisions, constraints, and a running status checklist. It is the source of truth for both planning and development sessions.
- **`p_hta.skill`** — A Cowork skill that loads this project context on demand. Install it by double-clicking the file. Once installed, invoke `/p_hta` at the start of any Cowork session to enter project mode: Claude reads `CLAUDE.md`, orients the session, and actively tracks decisions made during the conversation, prompting to update `CLAUDE.md` as things get confirmed or decided.

## Starting work on a new computer

1. Clone this repo
2. Double-click `p_hta.skill` to install the skill in Cowork
3. Open a new Cowork session and type `/p_hta`
4. Claude will read `CLAUDE.md` and orient you on current project state

For the development machine running Claude Code CLI, no skill setup is needed — Claude Code reads `CLAUDE.md` automatically when you run `claude` inside the repo directory.

## Keeping context current

When working in Cowork with `/p_hta` active, Claude will flag decisions and discoveries during the session and offer to update `CLAUDE.md` inline. At natural stopping points it will prompt to commit and push, so the development machine always has the latest planning state.

If you update `CLAUDE.md` manually or via Claude Code on the dev machine, pull the changes before starting a Cowork planning session.
