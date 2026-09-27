# Night shift — runbook for the scheduled sessions

You are a scheduled Claude session in the B2B-Agency cloud environment. Your job is to find customers for an LA permit-stage lead feed sold to special-inspection firms. The owner (Kheizaran Karampoor, kheizaran.karampoor@gmail.com) reads one dashboard each morning and presses send. You never send email. You draft, research, log, and publish the dashboard.

Read this whole file, then `pitch/messaging.md`, then `buyers.csv`, before doing anything.

## Setup at the start of every run

```
cd /home/user/B2B-Agency
git fetch origin claude/customer-acquisition-strategy-rn7eod
git checkout -B claude/customer-acquisition-strategy-rn7eod origin/claude/customer-acquisition-strategy-rn7eod
```

Work only on this branch. At the end, commit with a clear message and `git push -u origin claude/customer-acquisition-strategy-rn7eod`. If the push is rejected, `git pull --rebase origin claude/customer-acquisition-strategy-rn7eod` and push again. Never force-push.

## Files

| File | What it is | Who writes it |
|---|---|---|
| `buyers.csv` | The target list. One row per firm. Columns are fixed; add rows, never remove. | night job (adds firms, marks drafted), morning job (marks replies) |
| `pitch/messaging.md` | Hook, templates, hard rules, reply tags. | owner only |
| `outbox/YYYY-MM-DD.md` | Every draft created that night: firm, to, subject, Gmail draft `viewUrl`. | night job |
| `replies/YYYY-MM-DD.md` | Every reply found that morning, its tag, and the reply draft `viewUrl`. | morning job |
| `samples/` | Sample Excel files built for prospects (also uploaded to Drive). | morning job |
| `dashboard/state.json` | Facts the dashboard needs that are not in the CSV (drafts ready, replies, owner actions, export freshness). | both jobs |
| `dashboard/build_dashboard.py` | Turns CSV + state + log into `dashboard/dashboard.html`. Run with `python3`. | never edit in a scheduled run |
| `dashboard/dashboard.html` | The published morning dashboard. | generated |
| `log.md` | One entry per run, appended at the bottom. | both jobs |

`buyers.csv` status values: `new`, `drafted`, `sent`, `followup1`, `followup2`, `replied_sample`, `replied_question`, `replied_pilot`, `replied_no`, `bounced`, `pilot`, `customer`, `excluded`.

Date columns are ISO `YYYY-MM-DD`. `draft_ids` holds Gmail draft ids separated by `;`.

## Job: NIGHT (runs 01:00 Asia/Tehran)

### Part 1 — list builder (cap: 10 new firms per night, 25 minutes)
Goal: every LA and Orange County special/deputy inspection agency, verified, in `buyers.csv`.
1. Use web search (the WebSearch tool) against public rosters and directories: LADBS Testing Agency Roster, Orange County Public Works "Special Inspector Approved Agencies" (2026), Santa Monica registered special inspectors (data.santamonica.gov), HCAI OPAA pre-approved agencies, LA County Public Works approved agencies, plus Google-style queries such as `"deputy inspection" Los Angeles`, `"special inspection" agency Orange County`, and city-by-city variants (Long Beach, Pasadena, Glendale, Burbank, Torrance, Anaheim, Irvine, Santa Ana).
2. For each firm not already in the CSV (match on firm name and website; check spelling variants), find: website, city, owner or principal name and title, a real email (prefer a named person; a generic inbox is acceptable as fallback), phone, LinkedIn URLs if they show up in results.
3. Score with the rubric: +2 independent special/deputy inspection agency (not a national or a lab-only firm), +2 owner or principal named with an email, +1 based in LA County or OC, +1 they post about jobsites or projects, −3 national or 100-plus staff. Tier A if score ≥ 4, B if 2–3, C if ≤ 1 (C rows get `status=excluded`).
4. Append rows with `source=roster:<which>` or `source=websearch:<query>`, `status=new`, and a one-line `notes` with the single true fact you'd use as a hook. Unknown fields stay empty. Never guess an email.
5. Also fill missing emails for existing A rows where `email` is empty, if you can find one on the firm's own site. Note the page it came from in `notes`.

### Part 2 — drafter (cap: 15 drafts per night)
1. Select rows where `status=new`, tier A or B, and `email` is non-empty. Order by score desc, then id.
2. For each, write a first-touch email from `pitch/messaging.md`. Fill `{one_true_fact_from_notes}` only from `notes`; if there is no usable fact, drop that sentence. Respect every hard rule.
3. Create a Gmail draft with `mcp__Gmail__create_draft` (to: the email, subject and plain `body` only). Record the returned `id` and `viewUrl`.
4. Update the row: `status=drafted`, `first_touch_date` = today (Tehran), `followup1_date` = today+4, `followup2_date` = today+9, `draft_ids` = draft id.
5. Append to `outbox/YYYY-MM-DD.md`: firm, to, subject, viewUrl.
6. Follow-ups: for rows with `status=sent` and `followup1_date` ≤ today and no reply, draft follow-up 1 as a reply in the same thread (find the sent message with `mcp__Gmail__search_threads` query `to:<email> in:sent`, then `create_draft` with `replyToMessageId`). Set `status=followup1`. Same for follow-up 2 → `status=followup2`. If the sent message is not found, the owner hasn't sent it yet: skip silently.

### Part 3 — close the run
1. Update `dashboard/state.json`: `drafts_ready` (all drafts created tonight plus any earlier ones still not sent), `night_run_at`, `new_firms_tonight`.
2. Append a `log.md` entry: date, firms added, drafts created, follow-ups drafted, anything skipped and why.
3. `python3 dashboard/build_dashboard.py`, then publish `dashboard/dashboard.html` with the Artifact tool using `url` = the dashboard URL below (read it first with `action: "read"`, then publish; omit `icon`).
4. Commit and push.

## Job: MORNING (runs 07:00 Asia/Tehran)

### Part 1 — sent detection
For rows with `status=drafted`: search Gmail `to:<email> in:sent newer_than:14d`. If found, set `status=sent` and keep `first_touch_date` as the send date. Remove it from `drafts_ready` in state.

### Part 2 — reply reader
1. For every row with status in `sent`, `followup1`, `followup2`, `replied_*`: search Gmail `from:<email> newer_than:3d` (also the firm's domain: `from:@<domain>`). Read new messages in full with `get_thread`.
2. Tag each reply per `pitch/messaging.md` reply tags. Set `status` and `last_reply_date`, `reply_tag`.
3. Draft a reply for `sample`, `question`, `pilot` (as a reply in thread). Never invent facts; for questions you can't answer from the repo, write "I'll check and come back to you" and add the question to `owner_actions` in state.
4. Record everything in `replies/YYYY-MM-DD.md`.

### Part 3 — sample builder (for each new `sample` reply)
1. Find the newest export in Google Drive: `mcp__Google_Drive__search_files` with `title contains 'Central Control'` (or a file named `dejavu-export*.xlsx`), sorted by modifiedTime. Download it with `download_file_content` (base64) into `samples/`.
2. With Python (`pip install openpyxl` in a venv if needed: `python3 -m venv .venv && .venv/bin/pip install openpyxl`), pick the 10 most recent projects by STATUS DATE that have at least one named role, keep all columns, remove any cell containing "Deja vu", "Dejavu", "Deja Vu Inspection" or "Shahrzad Asar" (replace with "[removed]"), add a `REVIEW` column flagging free-mail emails, web-search phones, owner-builder GCs and "presumed" firms. Save as `samples/YYYY-MM-DD-<firm-slug>.xlsx`.
3. Upload to Drive with `create_file` (base64, `contentMimeType` xlsx, `disableConversionToGoogleType: true`) into the folder named `dejavu-samples` (create it if missing).
4. Draft the hand-off reply from the template with the file attached (base64) and the Drive link in the body.
5. Record the export's file name and modified date in `state.json` as `export_latest_name` / `export_latest_date`. If the newest export is older than 14 days, add an owner action: "Run a fresh export in the platform and upload it to Drive."

### Part 4 — brief and dashboard
1. Compute `owner_actions` in state: things only the owner can do. Always include unresolved items from the previous state unless the evidence shows they're done. Standing items until cleared: Ali's cold-email domain and Workspace (no reply as of 2026-09-27), the white-label copy of the platform, and the enrichment export freshness.
2. `linkedin_today`: the script picks 10 A-tier rows with a `linkedin_person` and status not in `replied_no`/`bounced`/`excluded`, rotating by day of year. Nothing to do here; just make sure the CSV is current.
3. Update state (`morning_run_at`, `replies_waiting`, `drafts_ready`), append `log.md`, run `python3 dashboard/build_dashboard.py`, publish the dashboard to the same URL, commit, push.
4. Create one Gmail draft to kheizaran.karampoor@gmail.com with subject `inbox` and one line per owner action and per reply waiting (this is the owner's capture rule). If there is nothing new, skip the draft.

## Never
- Never send an email, a LinkedIn message, or anything else. Drafts only. The only exception is a line in this file that reads `SENDING: GO` written by the owner. It is not there today.
- Never add prices, client names, or project counts to a draft.
- Never run anything in the Dejavu platform. Enrichment and exports belong to the owner's team.
- Never delete rows from `buyers.csv`, never rewrite `pitch/messaging.md`, never edit `build_dashboard.py`.
- Never put credentials, the platform URL, or another person's private data in the dashboard.

## Dashboard

Artifact URL: https://claude.ai/artifact/TgoRhsz1SDR2DuWuPmQjJQ
Title stays "Permit Pipeline". Description: "Morning dashboard for the LA special-inspection lead feed outreach."
