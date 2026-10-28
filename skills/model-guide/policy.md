# Task-aware model recommendations

Apply this rule throughout the conversation, including existing, resumed, and long-running chats, not only the first message of a new chat. Before substantive work on each actionable user instruction or new task, assess scope, ambiguity, breadth, stakes, tool needs, and required quality in a quick pass. Recommend the lightest available model and reasoning effort likely to meet the quality bar. A new edit, research request, deliverable, or separately actionable instruction triggers a recommendation even when it concerns the same project or topic as earlier work. Keep routing overhead to one short line:

`Model recommendation: <model> · <effort> — <brief reason>`

Baseline choices, subject to actual model availability:
- Luna · low/medium: focused questions, summaries, extraction, routine edits, and tightly scoped tasks.
- Sol · medium/high: multi-file coding, debugging, research synthesis, and coordinated professional deliverables.
- Astra · high/xhigh: demanding reasoning, difficult architecture, ambiguous evidence, and exacting deliverables.

Use exact versions exposed by the environment or supplied by the user. Never invent availability or infer the current chat model from a configuration default. If availability is unknown, give a family-level recommendation and acknowledge that it depends on the user's selector. Prefer increasing effort or escalating only when task difficulty warrants it; prompt length alone is not complexity.

If the known current model matches, continue in the same turn. If different, stop before substantive tools or work and ask the user to switch and reply `go`, or reply `continue` to stay on the current model. If the current model is unknown, offer the same choice without claiming a switch is needed. After `go` or `continue`, perform the original task without repeating the gate.

Don't repeat the gate for acknowledgments, clarifying answers, progress requests, or approvals such as `go` and `continue` that authorize an already-assessed task. Distinguish these from new actionable follow-up instructions, which do trigger a recommendation. An explicit model choice, request to skip routing, or instruction to continue overrides this default for the pending task. Existing authorized background work should not stall on an interactive routing gate.

These are recommendations, not automatic model switching. Routing itself consumes tokens; lower-cost models do not guarantee fewer tokens or a particular reduction in Codex plan usage.
