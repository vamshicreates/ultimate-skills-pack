---
name: omnirush-swarm
description: "Required before starting 3 or more sub-agents for one request (a swarm, or the user asks for several agents): the shared-board procedure. Never for 1-2 sub-agents or a small request."
---

# Sub-agent swarm

Use this only for a real swarm: 3 or more sub-agents working in parallel, or the user asked for a swarm or for several agents. For 1-2 sub-agents, stop here: call spawn_agents directly and do not create or touch a board.

The board is `.omnirush/swarm.md` in the workspace, never a file in the project root. omnirush keeps `.omnirush/swarm.md` and `.omnirush/swarms/` out of git. Ignore any `swarm.md` in the project root: it is not this swarm's board.

1. If `.omnirush/swarm.md` already exists, it is left over from an earlier swarm: move it to `.omnirush/swarms/<YYYYMMDD-HHMMSS>.md` and start a fresh board.
2. Before delegating, create `.omnirush/swarm.md` with: `# Goal` (one paragraph), `## Tasks` (a table: id, task, owner, status, result; ids like T1, T2, and T1.1 for a sub-task of T1; status is todo, running, done or blocked), `## Findings` (shared facts, one bullet each, with the task id), `## Decisions` (choices every agent must follow).
3. Give each sub-agent one task id. Its spawn_agents task text names the id, the task, and says: read `.omnirush/swarm.md` first; set your row to running; when done, set it to done with a one-line result and append your findings under your id; edit only your own rows and sections; report back briefly.
4. Sub-agents may split their own task: they add sub-task rows (T1.1, T1.2) and give the same instructions to their own sub-agents. Keep nesting to at most 3 layers.
5. Start the independent tasks together in one spawn_agents call (one entry per task) with the default blocking wait, not wait:false: the board must be complete before you merge. Give tasks that edit the same files to one agent.
6. When every task is done, read `.omnirush/swarm.md`, check and merge the results, and answer the user.
7. Then archive the board: move `.omnirush/swarm.md` to `.omnirush/swarms/<YYYYMMDD-HHMMSS>.md` (create the folder if needed), so no later request picks it up. If the user asked to keep the board, name the archived path in your answer.
