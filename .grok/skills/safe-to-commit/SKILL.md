---
name: safe-to-commit
description: >
  Keep personal information, credentials, and local private data out of git commits
  and GitHub. Use before writing docs, editing README/LICENSE, preparing commits,
  or when the user mentions secrets, passwords, API keys, tokens, PII, privacy,
  or pushing to GitHub. Also use for /safe-to-commit.
---

# Safe To Commit

Before creating or modifying files that may be committed, or before suggesting a
commit/push, verify the change set does not expose private data.

## Never commit

- API keys, tokens, passwords, private keys, `.env` files, or connection strings
- Real values in setup examples (use placeholders like `YOUR_API_TOKEN_HERE`)
- Personal names, emails, ages, health details, addresses, or other PII
- Local workout exports or other downloaded user data
- Files under `~/.config/` (for example `~/.config/concept2/api_key`)

## This repo: keep local only

| Item | Local path | In repo |
|------|------------|---------|
| Concept2 API token | `~/.config/concept2/api_key` | Never |
| Workout CSV/JSON exports | `~/concept2_detailed_workouts/` | Never |
| Test fixtures | `tests/fixtures/` | OK (synthetic sample data only) |

## Before every commit or push

1. Run `git diff --cached` and `git diff` on changed files.
2. Scan for secret-like patterns:
   - `api_key`, `token`, `password`, `secret`, `Bearer `
   - email addresses, real names, phone numbers
   - absolute home-directory paths that reveal a username if sensitive
3. Confirm `.gitignore` covers generated/local data and secret filenames.
4. If anything sensitive is already tracked, stop and tell the user to remove it
   from git history before pushing.

## When editing docs or code

- README/setup instructions: placeholders only, never real tokens.
- LICENSE/copyright: use project or contributor names, not personal legal names
  unless the user explicitly wants them public.
- Tests: fake tokens like `secret-token` in temp dirs are fine; never read the
  real `~/.config/concept2/api_key` into repo files.
- If the user asks to document their identity, confirm they want it public on
  GitHub first.

## If a secret was committed

Tell the user immediately:

1. Rotate/revoke the exposed credential.
2. Remove the file from the index: `git rm --cached <file>`
3. Add or update `.gitignore`.
4. If already pushed, rewrite history or use GitHub secret scanning guidance;
   rotation is still required because history may be cached.

## Quick staged-file check

```bash
git diff --cached --name-only
git diff --cached | rg -i 'api[_-]?key|password|secret|token|bearer |@.*\.(com|org|net)|BEGIN (RSA |OPENSSH )?PRIVATE KEY'
```

If matches look real (not placeholders or test fakes), do not commit until fixed.