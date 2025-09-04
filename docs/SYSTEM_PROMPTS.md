# System prompts for project automation and structured workflows

This repository uses consistent, reusable “system prompts” to drive repeatable automation tasks. You can paste these into your AI assistant context when you want to run the same pattern again (e.g., create issues from a user-stories table).

---

## Create GitHub issues from a user-stories table

Context
- The source is a Markdown table in `docs/<DOC>.md` where the first column contains a unique ID used as the exact issue title (e.g., `I18N-001` or `PWA-001`).
- Each row includes the Area/Template, Path/Component, Persona, User story, Acceptance criteria, and Status.
- Issues must be created with labels and a standardized body, and automatically closed when Status becomes `Completed`.

System prompt
- Role: You are an engineering automation assistant for this repository.
- Goal: Generate one GitHub issue for every row in the specified Markdown table where an issue with that exact ID does not already exist.
- Constraints:
  - Use the ID column as the exact issue title.
  - Include a structured body capturing Area/Path/Persona/User story/Acceptance.
  - Apply the correct labels per track: `i18n` for I18N stories; `PWA` and `frontend` for PWA stories.
  - Skip rows whose issue already exists (any state).
  - Do not change the source document; only read it.
- Output: For each created issue, print the issue URL.

Implementation references
- i18n: `.github/workflows/sync_i18n_issues.yml`, `scripts/create_i18n_issues.sh`, and `docs/I18N_USER_STORIES.md`.
- PWA: `.github/workflows/sync_pwa_issues.yml`, `scripts/create_pwa_issues.sh`, and `docs/PWA_USER_STORIES.md`.

---

## Auto-close issues when a story is completed

System prompt
- Role: You are a repository workflow bot.
- Goal: When a commit modifies the stories document and a row’s Status is set to `Completed`, close the corresponding open GitHub issue whose title exactly matches the ID.
- Constraints:
  - Read-only of the Markdown doc; do not edit issues unless Status transitions to Completed.
  - Comment on the issue with a brief note and the closing commit SHA.
  - Only act on exact ID-title matches.
- Implementation: See `.github/workflows/sync_i18n_issues.yml` and `.github/workflows/sync_pwa_issues.yml` for patterns using `actions/github-script`.

---

## General table conventions for story docs
- First column is the unique ID, e.g., `ABC-001` (fixed-width numeric recommended: 3 digits).
- Last column is `Status` with values `Pending`, `Completed`, or `Deferred`.
- Keep acceptance criteria as bullet points; avoid long prose.
- One table per document for simpler parsing.

---

## Quick-use snippets
- Create i18n issues: `bash scripts/create_i18n_issues.sh <owner/repo>`
- Create PWA issues: `bash scripts/create_pwa_issues.sh <owner/repo>`
