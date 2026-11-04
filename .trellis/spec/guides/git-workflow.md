# Git Workflow

## Separate ordinary work from Trellis records

Use the `git-commit` workflow for ordinary work commits.
Ordinary work includes source, tests, configuration, dependencies, specs, workflow files, and authorized project documentation.
Trellis manages its task, archive, journal, and index bookkeeping commits.
The ordinary-commit approval procedure does not apply to those native bookkeeping commits.

Inspect the current changes and staging state before you prepare a commit.
Preserve unrelated changes and staged files.
Group related changes into coherent commits.
A proposed batch does not authorize all its commits.

Before each ordinary commit, show the final staged files, final message, and effective signing settings.
Get the user's explicit approval for that commit.
Preserve the user's signing configuration.
Complete ordinary work commits before archive and journal commits.

## Use the actual branch mode

Create a branch or worktree only when the user explicitly requests one.
For work without a separate task branch, archive with this command:

```bash
python3 ./.trellis/scripts/task.py archive <task> --skip-branch-validation
```

For an explicitly used task branch, retain the normal archive branch checks.
An explicit request to archive that task branch authorizes a local merge into its recorded base branch.
Return to the recorded base branch after the merge.
That authorization does not include a remote push.

## Approve authenticated GitHub operations

Get explicit approval before you use GitHub credentials, including authenticated reads through an existing `gh` login.
Identify the credential source, account, repository, operations, and repository visibility in the request.
Do not request approval again for actions already covered by that approval.
