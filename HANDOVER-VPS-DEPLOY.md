# Handover: replace GitHub Pages hosting with VPS deploy via Actions

Brief for the next Claude session working in this repo (`Fox-Menus`). Read this top-to-bottom before touching anything.

## Context

The Fox-Menus repo currently hosts the menus on **GitHub Pages** at `https://menus.foxatwalton.com/`. The WordPress site at `foxatwalton.co.uk` (currently staged at `staging.foxatwalton.co.uk`) wants to pull menu HTMLs/PDFs into its own pages — Sunday Lunch in particular needs the dish data wrapped inside its rich SEO page.

The decision: **drop GitHub Pages** entirely. Push the built `menus/` folder straight to the WordPress server's `wp-content/uploads/menus/` via SSH on every push to `main`. The WP site then serves the files natively from `foxatwalton.co.uk/wp-content/uploads/menus/...`.

### Why drop Pages?

1. **SEO**: a second public domain (`menus.foxatwalton.com`) competes with `foxatwalton.co.uk` for menu-related searches. Customers can land on a bare menu page with no booking CTA. The medium-paranoia fix (robots.txt + meta noindex + canonical) leaves a small residual risk for PDFs because GitHub Pages doesn't allow custom `X-Robots-Tag` headers.
2. **Performance**: WP serving local files is faster than fetching from a remote CDN on every page load.
3. **Privacy option**: with this setup, this repo could go private later if owners want, without affecting menu delivery to the public site.
4. **One domain to manage**: the rest of the site is on `foxatwalton.co.uk` and that's what owners think of as "the website."

The Sunday Lunch wrapper (where the menu data gets injected into a rich WP page) lives **in the WordPress project**, not here. That's a separate work item already documented in that project.

## Architecture

```
You/chef edit menus/Foo-Menu-A4.html
        │
        ▼ git push
GitHub Actions (.github/workflows/generate-pdfs.yml)
   1. Detects changed HTML files
   2. Runs Playwright to generate matching PDFs
   3. Commits PDFs back to the repo (existing behaviour)
   4. ★ NEW: rsync the entire menus/ folder to the VPS
        │
        ▼ SSH
VPS (77.68.97.183) at /root/foxatwalton-staging/wp-content/uploads/menus/
        │
        ▼ Docker bind-mount
WordPress container serves at https://staging.foxatwalton.co.uk/wp-content/uploads/menus/*
```

## Required changes in this repo

### 1. Add the deploy step to `.github/workflows/generate-pdfs.yml`

Append after the existing "Commit and push PDFs" step. Use `appleboy/scp-action` so SSH host-key handling and key parsing are handled for you.

```yaml
      - name: Deploy menus to WordPress VPS
        uses: appleboy/scp-action@v0.1.7
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ${{ secrets.VPS_USER }}
          key: ${{ secrets.VPS_SSH_KEY }}
          port: 22
          source: "menus/*.html,menus/*.pdf"
          target: "/root/foxatwalton-staging/wp-content/uploads/"
          strip_components: 0
          overwrite: true
```

Notes:
- `source` is comma-separated globs (NOT bash brace expansion — appleboy/scp-action parses this string itself).
- `target` is the parent directory; `strip_components: 0` keeps the `menus/` prefix so files land in `/root/foxatwalton-staging/wp-content/uploads/menus/`.
- `overwrite: true` so re-deploying with the same filename replaces the existing file.

### 2. Make this step run after the auto-commit, on the same workflow run

The existing workflow auto-commits PDFs in the `Commit and push PDFs` step. If the deploy step runs in the same job, the new PDFs from this run are already on disk — they get copied across. ✅ No second workflow trigger needed.

If you want this to also run on `workflow_dispatch` even when no HTML changed, that already works because the step is unconditional.

### 3. Disable GitHub Pages for this repo

After the first successful deploy that proves the WP side is serving the files:

1. **Repo Settings → Pages → Source: "None"** (or "Disabled")
2. Delete the `CNAME` file from the repo root
3. Coordinate with the user to **delete the DNS CNAME record** for `menus.foxatwalton.com` at whatever DNS provider hosts `foxatwalton.com`
4. Submit a removal request in Google Search Console if `menus.foxatwalton.com` was ever indexed

Don't do steps 1–3 until the new path is verified working — otherwise customers who already have menu links lose access during the transition.

## GitHub secrets to add

In Repo Settings → Secrets and variables → Actions, add:

| Secret name | Value |
|---|---|
| `VPS_HOST` | `77.68.97.183` |
| `VPS_USER` | `root` |
| `VPS_SSH_KEY` | The full ed25519 private key, including `-----BEGIN OPENSSH PRIVATE KEY-----` / `-----END OPENSSH PRIVATE KEY-----` lines. Provided separately by the operator. |

This is a **dedicated** key for this repo — not the same as `ground_control_deploy`. If this repo is ever compromised, rotating the key on the VPS only affects menu deploys.

## VPS state — already prepared

The user has run these one-time steps before handing this to you, so you can assume:

- The deploy key's public half is already in `/root/.ssh/authorized_keys` on the VPS as the entry tagged `fox-menus-deploy-YYYYMMDD`.
- The target directory `/root/foxatwalton-staging/wp-content/uploads/menus/` already exists with `chmod 755`.
- Docker bind-mount: `/root/foxatwalton-staging/wp-content/uploads/` is mounted into the WP container at `/var/www/html/wp-content/uploads/`, so anything you scp into the host path is immediately served by Apache at `https://staging.foxatwalton.co.uk/wp-content/uploads/menus/*` without container restart.

## Testing the deploy

After merging the workflow change:

1. Manually trigger the workflow once: Actions → "Generate PDFs from HTML Menus" → Run workflow → main
2. Watch the step `Deploy menus to WordPress VPS` complete green
3. From your machine:
   ```
   curl -sI https://staging.foxatwalton.co.uk/wp-content/uploads/menus/Sunday-Menu-B4.pdf | head -1
   ```
   Expect `HTTP/2 200`. Repeat for at least the .html version too.
4. Open the PDF in a browser to confirm it's the latest. Compare file size to the one in this repo.

If 200s come back, the deploy is wired.

## Edge cases to watch

- **PDFs not yet committed** — the workflow's "Commit and push PDFs" step has `git diff --cached --quiet` short-circuit. If nothing changed, no commit happens, but the scp step still runs and re-uploads the existing files. Safe but technically wasteful. Don't optimise this — predictable is better than clever for CI.
- **Deleted menus** — `appleboy/scp-action` doesn't have a `--delete` equivalent. If a menu is removed from this repo, the corresponding files **stay** on the VPS. If this matters, add a small `appleboy/ssh-action` step that runs `find ... -delete` before the scp, OR switch to a real `rsync --delete` via a bash step using `ssh-action`. Not implemented by default; add only if it becomes a real problem.
- **Race condition with auto-commit** — the "Commit and push PDFs" step pushes to `main`, which would normally re-trigger the workflow. Look at the existing workflow: `paths: [menus/*.html]` filters that out (PDFs are not HTMLs). ✅ No infinite loop.
- **Permissions inside the container** — files land as `root:root` on the host. WP runs as `www-data` inside the container. Apache reads world-readable files fine, so this works. If you ever switch to NGINX or change file permissions, re-verify Apache can read them.

## What this does NOT do

- Does not modify any HTML/PDF content
- Does not change the converter scripts
- Does not affect the local dev workflow (Python scripts still work the same)
- Does not handle WordPress-side wiring — that's the foxatwalton.co.uk theme's job

## After this is merged and verified

Tell the operator. The next step (in the WordPress project, not here) is to:

1. Update `page-menus.php` "Download PDF" buttons to point at `/wp-content/uploads/menus/*.pdf`
2. Update "View Menu" buttons (except Sunday Lunch) to point at `/wp-content/uploads/menus/*.html`
3. Wrap the Sunday Lunch dish data inside the rich WP page using a `fox_local_menu()` helper that reads `wp-content/uploads/menus/Sunday-Menu-B4.html` from disk (no network call needed)
4. After WP wiring is verified, disable GitHub Pages and delete the CNAME file and DNS record (this repo)

Stop here once the deploy step is green and files are serving from the WP server. Don't drift into the WordPress wiring — that belongs in the other project.
