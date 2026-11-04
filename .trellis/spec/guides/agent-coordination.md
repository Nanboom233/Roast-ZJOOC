# Agent Coordination

## Use the selected execution mode

In subagent mode, the main session owns requirements, planning, task artifacts, coordination, and result integration.
Assign implementation and code rework to the implement agent.
Use the check agent to verify the work under its role contract.
The main session must not take implementation ownership because a change is small.
Inline workflows permit the main session to implement and repair code.

Subagents must not create Git commits.
This ban includes temporary baseline commits and indirect commits through archive or journal scripts.
The main session owns authorized Git operations.

## Keep the active owner

Do not interrupt an active Trellis research, implement, or check agent because its response is slow.
Missing progress messages do not authorize replacement or takeover.
Use status queries, messages, and waits to coordinate the work.

If an agent fails, is canceled, or returns incomplete work, first resume the same agent.
After two failed resume attempts, report the failure to the user.
If resumption fails or is unavailable, get user approval before replacement or takeover.
Preserve agent state and workspace changes after a user interruption.
On continuation, resume the same agent and workflow when available.

## Share the task environment

Reuse the task's existing test environment.
The main session coordinates environment ownership and conflicting operations.
Preserve active services, caches, diagnostic files, and valid evidence that another owner still uses.
Remove only obsolete resources that belong to the current task.
