# Customer acquisition plan: Dejavu lead-feed system → LA special-inspection firms

Date: 2026-09-27. Status: proposal, waiting for your yes.
Everything in "Where things stand" comes from your own files (named inline). Nothing here is invented; unknowns are marked `[unknown]`.

## 1. Where things stand

**Product** (source: Gmail thread "فروش سیستم دژاوو به بقیه", 2026-09-22; Drive doc "Dejavu Marketing: LinkedIn outreach drafts", 2026-09-27)
- LA-area construction lead feed: ConstructConnect projects matched with LADBS + Santa Monica permits, plus decision-maker contacts (owner, architect, GC PM). Delivered as Excel + dashboard, optional email campaigns.
- Voice calling is dropped (TCPA). Do not mention calling in any pitch.
- Live URL contains the customer name (`dejavu-marketing.aiautomation.bar`) and cannot be shown to prospects until the white-label copy exists.

**Pricing** (same Gmail thread, 2026-09-22): setup $1,500 · Leads $750/mo · Leads + Email $1,500/mo · 30-day pilot $500, credited against setup if they continue. Payment via Ali's Italian account; invoice-name and test-transfer items still open.

**Buyers already identified**
- 21 Priority A firms with LinkedIn research and ready-to-send connection notes, DMs and InMail fallbacks (Drive doc 2026-09-27, marked DO NOT SEND YET). 15 have a confirmed person profile.
- 30-firm competitor landscape with phone/email/website for most (Drive doc "CALIFORNIA SPECIAL INSPECTION & MATERIALS TESTING COMPETITOR LANDSCAPE", 2026-09-15). Tiers A/B/C double as a buyer list: tier A small operators are the fit; tier B/C nationals (Terracon, Kleinfelder, WSP) are not.
- A 9/26 email draft set and a roster CSV are referenced in the LinkedIn doc but were **not found in Drive** `[unknown location]`.

**Open blockers from your 2026-09-22 email to Ali** (no reply found in Gmail as of today; only calendar acceptances from him on 9/22–9/24)
1. Domains + Google Workspace + SPF/DKIM/DMARC (`aifirst-solutions.com`, cold-email domain `getaifirstsolutions.com`), 2–3 weeks warm-up.
2. White-label copy of the platform without "dejavu" in the name.
3. Free sample: 10 permitted projects (Glendale / LA County) with contacts, Excel, no client names.
4. Email-sequence feature + role filter in the dashboard (hours estimate pending).

**This cloud environment, tested today**
- Blocked by network policy: `dejavu-marketing.aiautomation.bar`, `data.lacity.org`, `ladbsservices2.lacity.org`, `data.santamonica.gov`, `pwds.oc.gov`, `linkedin.com`, `api.apollo.io`.
- Working: web search, Gmail (read + drafts), Google Drive/Sheets/Docs, Calendar, Notion, Slack, Canva, Composio (gmail, googlesheets, instagram, telegram connected), scheduled Routines that run without you.
- Apollo.io connector exists but is not authenticated in this session; ZoomInfo not connected. Neither is needed for this niche (see §2).

## 2. My read on the five screenshots

The posts are lead magnets ("comment MCP / AGENTS / B2B / LEADS for free access"). What they sell is a bundle of prompts wrapped as "60 agents, 50 skills", plus one real product: Prosp's LinkedIn automation connector (screenshot 1).

What is worth keeping: the loop shape. Find → Write → Send → Read, with a daily cap and a reply router. That is the right shape and we already have most of it in drafts.

What I recommend **against** for this product:
- **LinkedIn automation as the engine.** The total market is small (roughly 50–150 LA/OC special-inspection agencies, from the public approved-agency rosters), so a 2,000-request-a-month machine buys nothing. The buyers are owner-operators who live in email and phone. Automation tools need your logged-in LinkedIn session running 24/7 and put the account at risk, and your LinkedIn access is already fragile from your location. Use LinkedIn by hand, 10 a day, straight from the 2026-09-27 doc.
- **Apollo/ZoomInfo for list building.** Public rosters (LADBS Testing Agency Roster, Orange County 2026 Special Inspector Approved Agencies, Santa Monica registered inspectors, HCAI OPAA, LA County) are the complete universe, are free, and are already the sources your competitor doc used.

## 3. Recommendation: a "night shift" that runs here, in this cloud environment

One strong option, not three. Four scheduled jobs, built as Routines in this environment, each writing to one Google Sheet ("Buyers") that is the single source of truth.

| # | Job | Runs | What it does | Sends anything? |
|---|-----|------|--------------|-----------------|
| 1 | List builder | nightly | Web-search the public rosters, find every LA/OC special-inspection agency, verify site + owner + email, dedupe against the 21 + 30 already known, append to the sheet with a fit score (A/B/C). Target 80–150 verified firms in 2 weeks. | No |
| 2 | Drafter | nightly | For each new verified A/B firm, write first-touch email + 2 follow-ups (day 4, day 9), following the rules already in the 9/27 doc: data feed, contacts, Excel/dashboard, optional email campaigns; no calling, no prices, no client names, no invented facts. Saves them as **Gmail drafts** and logs draft IDs in the sheet. | No |
| 3 | Reply reader + morning brief | 07:30 Tehran, daily | Scans the inbox for replies from any address in the sheet, tags them (sample / question / no / bounce), updates the sheet, and writes a short brief: drafts ready to send today, replies to answer, the 10 LinkedIn targets for today. Delivered as a Gmail draft with subject "inbox" per your capture rule, or a Slack/Telegram message if you prefer. | No |
| 4 | Sample builder | on demand, when a reply says "sample" | Builds the 10-project Excel for that firm's service area. **Blocked today** because this environment cannot reach LA open data (see §4). | No |

Who presses send: you, from the drafts, 10–20 a day from Gmail, until the cold domain exists. That is the honest "while I sleep" boundary under your own rule (I never send). The night shift does 90% of the work; the send is one click per email in the morning.

After `getaifirstsolutions.com` is warmed (2–3 weeks after purchase): move sending to a dedicated tool (Instantly or Smartlead, or Composio's Gmail on the new Workspace account) with a one-time written authorization from you, a daily cap (start 20/day), and a kill switch (a "PAUSE" cell in the sheet). Only then do follow-ups go out unattended.

## 4. What only you or Ali can clear, in order

1. **Ali: domains + Workspace + DNS.** No reply in email as of 2026-09-27. If this is not moving by ~Oct 1, plan B is to keep everything on Gmail at low volume; the night shift still works, just slower.
2. **Ali: white-label copy of the platform.** Until it exists, we send no links. Interim collateral I can make: a one-page PDF (what the feed contains, sample columns, pilot terms) and the sample Excel.
3. **You: environment network allow-list.** In the cloud environment menu in this session's title bar → Edit → Network access, add: `data.lacity.org`, `data.santamonica.gov`, `ladbsservices2.lacity.org`, `pwds.oc.gov`. With that, job 4 can pull permits directly from LA open data and build samples here, without waiting on the Master Record. Optionally add `dejavu-marketing.aiautomation.bar` if you want me to review the dashboard and write the one-pager from what it actually does; I do not need your login until then.
4. **You: sending authority** (question 1 below).

## 5. Week-1 targets

Targets, not predictions.
- All 21 Priority A firms touched once by email and once on LinkedIn (from existing drafts).
- Buyers sheet at 60+ verified firms.
- 3+ "sample" replies; one 30-day pilot conversation started.

## 6. Two questions before I build

1. **Sending authority.** Once the cold domain is warmed, do you authorize the night shift to send first-touch and follow-ups itself (daily cap, kill switch, log of every send), or must every send stay a manual click? The answer decides whether I build job 2 as drafts-only or drafts-then-send.
2. **Ali's status.** Has he bought the domains or started the white-label copy since 9/22? If yes, when; if no, I build plan B (Gmail, low volume) now and switch later.

If you say yes, the first build is: the Buyers sheet seeded from the two Drive docs (51 firms), job 1 and job 3 scheduled tonight, job 2 producing its first 21 drafts for you to review tomorrow morning.
