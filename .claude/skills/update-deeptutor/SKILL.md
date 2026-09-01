---
name: update-deeptutor
description: Safely bring HKUDS/DeepTutor upstream changes into this customized Korean DeepTutor fork while preserving and extending Korean localization. Use this skill whenever the user asks to update DeepTutor, receive original/upstream Git changes, sync with the source repository, merge a new release, check whether updates exist, or says phrases such as "업데이트해줘", "원본 업데이트", "업스트림 업데이트", "새 버전 받아줘", "DeepTutor 업데이트 받아줘", or "최신 버전으로 맞춰줘" in this repository. Do not treat an ordinary dependency update or a request to edit one feature as an upstream-sync request.
compatibility: Requires git, gh, Python 3.11-3.13 with the project virtualenv, Node.js, and the web package dependencies.
---

# DeepTutor upstream update

Update the customized Korean fork without turning new upstream UI into untranslated English or losing local behavior during conflict resolution.

## Repository contract

Treat this layout as intentional:

- `upstream` is `HKUDS/DeepTutor`, the original repository.
- `origin` is the user's fork, currently `geuneda/DeepTutor`.
- `main` is a clean mirror of `upstream/main` and tracks it.
- `custom/korean` contains the Korean customization and tracks `origin/custom/korean`.
- `remote.pushDefault` should be `origin`, so an unqualified push cannot target upstream.

Never push to `upstream`. Never push anywhere unless the user explicitly asks for a push in the current request. Updating local branches does not imply permission to publish them.

## Success criteria

An update is complete only when all of these are true:

1. `main` is fast-forwarded to the fetched `upstream/main`.
2. The upstream update is integrated through a temporary integration branch based on `custom/korean`.
3. No unresolved conflict markers or unmerged paths remain.
4. Existing Korean behavior is preserved and every new translatable upstream key has a real Korean translation.
5. Placeholders, plural keys, backend status keys, tool descriptions, and prompt bundles remain structurally consistent across locales.
6. Relevant Python tests, web Node tests, and i18n checks pass.
7. Only after validation, `custom/korean` is fast-forwarded to the validated integration commit.
8. The final report names versions/commits, conflicts resolved, translations added, tests run, branches changed, and whether anything was pushed.

If a requirement cannot be satisfied, keep `custom/korean` unchanged, leave the work on the integration branch, and report the exact blocker.

## 1. Inspect before changing anything

Run read-only checks first:

- `git status --short --branch`
- `git remote -v`
- `git branch -vv`
- `git config --get remote.pushDefault`
- `git rev-parse --verify main`
- `git rev-parse --verify custom/korean`

Stop instead of guessing when:

- a merge, rebase, or cherry-pick is already in progress;
- tracked or untracked user changes are present;
- the expected branches or remotes are missing;
- `upstream` does not identify `HKUDS/DeepTutor`;
- `origin` points at the original repository rather than the user's fork.

Do not stash, discard, overwrite, or auto-commit unrelated work. Explain what must be protected first.

If only the safe push default is missing, set the repository-local value with:

```bash
git config remote.pushDefault origin
```

## 2. Fetch and report the available update

Fetch without touching the working tree:

```bash
git fetch upstream --prune
git fetch origin --prune
```

Compare before integrating:

```bash
git rev-list --left-right --count main...upstream/main
git log --oneline --decorate main..upstream/main
git diff --stat main..upstream/main
```

If there are no upstream commits, report that the project is current and stop without creating a branch or commit.

Note the old and new commit IDs and any release tags. Summarize major upstream areas rather than dumping hundreds of commit lines.

## 3. Fast-forward the clean main branch

Because `main` is the clean upstream mirror, update it only by fast-forward:

```bash
git switch main
git merge --ff-only upstream/main
```

If fast-forward fails, stop. Do not rebase, reset, or merge divergent local commits into `main` automatically.

Do not push `main` unless explicitly requested.

## 4. Create an isolated integration branch

Return to the customization and create a unique branch containing the upstream short SHA, for example:

```bash
git switch custom/korean
git switch -c integrate/upstream-<short-sha>
git merge --no-commit --no-ff main
```

If that branch name exists, inspect it and choose a new unique name. Do not delete or overwrite an existing branch.

The temporary branch is the safety boundary: `custom/korean` must not move until the merge and translations pass validation.

## 5. Resolve conflicts semantically

Inspect each conflict with the base, customized, and upstream versions. Do not resolve all files with blanket `--ours` or `--theirs`.

Use these rules:

- Preserve upstream architectural changes, renamed routes, new APIs, new supported agents, and deleted components that truly have no remaining references.
- Reapply Korean localization through the current i18next/backend localization architecture rather than restoring obsolete components or old route structures.
- Preserve custom Korean locale support, language normalization, backend messages, prompt hints, quiz language behavior, and their tests.
- Keep upstream bug fixes and new functionality unless they directly contradict the Korean feature; adapt the Korean feature to the new structure.
- For a modify/delete conflict, search for references before deciding. Do not resurrect an upstream-deleted component merely because the old Korean branch edited it.
- Inspect any unexpected unrelated customization and report it instead of silently treating it as Korean work.

### Locale JSON merge rule

Treat `web/locales/en/app.json` from current upstream as the authoritative key set and English source text.

Build Korean locale output as follows:

1. Retain existing Korean translations for keys that still exist.
2. Remove Korean-only keys only after confirming upstream removed the feature or renamed the key.
3. Add every new English key to Korean with an actual Korean translation.
4. Preserve interpolation tokens exactly, including forms such as `{{name}}`, `{{count}}`, and plural suffixes.
5. Keep JSON ordering compatible with the upstream English bundle where practical.
6. Never fill missing Korean values by copying English prose merely to satisfy parity tests. Brand names, identifiers, paths, and code literals may remain unchanged when appropriate.

Translate in coherent feature groups so terminology stays consistent. Reuse established Korean terms from the existing bundle before inventing new ones.

### Backend and tool localization

Check more than the web JSON bundles. New upstream features may require updates to:

- backend status dictionaries and parity tests;
- `deeptutor/i18n/metadata_i18n.py` tool names/descriptions;
- `deeptutor/tools/prompting/hints/ko/`;
- Korean agent prompt directories;
- language-aware API and service behavior;
- Korean coverage tests.

When a parity or fallback test reports new names, translate the source metadata rather than weakening or deleting the test.

## 6. Validate before committing

First verify repository integrity:

```bash
git diff --check
git diff --name-only --diff-filter=U
```

Search for conflict markers in changed text files. Confirm locale JSON parses.

Use the supported project environment, not the system Python 3.14:

```bash
.venv/bin/python --version
```

Run at least the Korean/backend regression set:

```bash
.venv/bin/python -m pytest \
  tests/api/test_settings_router.py \
  tests/api/test_quiz_judge_language.py \
  tests/capabilities/test_setup_capability.py \
  tests/capabilities/test_status_i18n_consistency.py \
  tests/core/test_backend_message_locales.py \
  tests/services/test_suggestions_locales.py \
  tests/tools/test_prompt_hints_locales.py \
  tests/tools/test_tool_display_locales.py
```

Run web validation from the package correctly:

```bash
npm --prefix web run test:node
npm --prefix web run i18n:check
```

Also run targeted tests introduced or affected by the upstream commits. Run broader suites when the changed area warrants them.

If dependencies changed and a failure specifically shows stale or missing installed packages, refresh dependencies using the repository's lockfile-compatible command, then rerun. Do not misreport an environment failure as a code failure.

Do not weaken parity, placeholder, fallback, or Korean coverage tests to make the merge pass.

## 7. Commit and promote only after validation

For a conflict-free or resolved merge, stage only the integration work and review the staged diff.

Follow repository commit hygiene:

- Write the commit message to `.git/COMMIT_MSG` with the Write tool.
- Use `git commit -F .git/COMMIT_MSG`.
- Do not use `git commit -m`, an inline message, or a heredoc.
- End the message with `Co-Authored-By: Claude Code <noreply@anthropic.com>`.

Suggested subject:

```text
merge: integrate upstream <version-or-short-sha> with Korean localization
```

After the commit, rerun fast sanity checks if hooks changed files. Then promote without rewriting history:

```bash
git switch custom/korean
git merge --ff-only integrate/upstream-<short-sha>
```

Leave the integration branch in place unless the user asks to remove it. Branch deletion is not part of the update.

If any required test fails, do not promote. Stay on the integration branch and report the failure with the relevant output.

## 8. Push only when explicitly requested

When the user explicitly asks to publish the completed update, push only to the fork:

```bash
git push origin custom/korean
```

Push `main` to `origin` only if the user explicitly asks to sync the fork's main branch too. Never run `git push upstream`.

Before pushing, show that `remote.pushDefault=origin`, the destination branch, and the commits to be published.

## Final report

Keep the report concise but complete:

- old upstream version/commit → new version/commit;
- number and themes of upstream commits;
- integration branch name;
- conflict files and the resolution approach;
- number of new Korean keys/prompts/statuses translated;
- exact test commands and pass/fail counts;
- resulting `main` and `custom/korean` commit IDs;
- whether push was skipped or completed, including the destination;
- any remaining blocker or follow-up.
