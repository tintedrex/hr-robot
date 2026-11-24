# Branch rules — hr-robot

## Branches

| Branch | Purpose |
| --- | --- |
| `main` | Stable integration; protected |
| `feature/<short-name>` | New work (e.g. `feature/balance-outer`) |
| `fix/<short-name>` | Bug fixes |
| `docs/<short-name>` | Documentation-only changes |

Do not commit directly to `main`.

## Pull requests

1. Branch from latest `main`.
2. Open a PR into `main` with a short summary and test notes.
3. CI workflow **ROS 2 Humble build** must pass.
4. At least one approving review when a second teammate is available (solo: self-check against SRS IDs you touch).
5. Squash-merge preferred for a clean history.

## GitHub protection settings (apply after remote exists)

In GitHub → **Settings → Branches → Add rule** for `main`:

- Require a pull request before merging
- Require status checks to pass: `humble-build`
- Require conversation resolution before merging
- Do not allow force pushes
- Do not allow deletions

CLI equivalent (GitHub CLI):

```bash
gh api repos/{owner}/hr-robot/branches/main/protection \
  --method PUT \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["humble-build"]
  },
  "enforce_admins": true,
  "required_pull_request_reviews": {
    "required_approving_review_count": 1
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false
}
EOF
```

If you are solo and reviews block you, set `required_approving_review_count` to `0` temporarily but keep status checks on.

## Commit message style

- Imperative, short: `Add balance outer loop stub`
- Reference SRS IDs when relevant: `Implement SW-BAL-002 publish rate`
