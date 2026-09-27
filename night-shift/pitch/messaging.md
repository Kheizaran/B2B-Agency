# Messaging rules and templates

Sender: Kheizaran Karampoor, AIFirst Solutions, kheizaran.karampoor@gmail.com.
(Brand assumption: the platform is described generically; the customer-named URL is never shown. Change the brand here if you prefer another name.)

## Hard rules (every draft, every reply)
- Never invent a fact about the prospect. Use only what is in `buyers.csv` notes or verified by the list builder.
- No prices. No client names. No project counts or dollar totals from the data.
- No links to the platform until the white-label URL exists.
- Voice agent and email campaigns are mentioned once, as optional add-ons, in one sentence. Never as the headline.
- Plain text. Under 130 words for a first touch, under 60 for a follow-up. One ask per email: reply "sample".
- If the contact name is unknown, open with "Hi there" and address the firm.
- If the email is a generic inbox (info@, support@), open with "Hi [Firm] team".
- Subject lines: never "Re:" on a first touch. Never all caps.
- Do not send. Drafts only, until the owner writes GO SEND in the build session.

## The hook
The platform sees LA City and Santa Monica permits while they are still in plan check, before a general contractor or inspection agency is chosen, and it names the engineer of record on many of them. ConstructConnect lists projects at bid stage and misses most residential additions, ADUs, hillside grading and 2025 wildfire rebuilds. The engineer of record writes the special-inspection program, so that name is the one an inspection firm wants first.

## First touch (day 0)
Subject: LA permits at plan check, with the engineer of record

Hi {first_name},

I came across {firm} and saw you {one_true_fact_from_notes}.

I run AIFirst Solutions. We built a lead feed for LA-area special-inspection firms: LA City and Santa Monica permits pulled while they're still in plan check, matched to the permit's named engineer, architect and contractor, and enriched with their contact details. It's delivered as Excel plus a dashboard, so your team sees a project before the GC has picked an inspection agency. Optional add-ons include email campaign sequences and an AI voice agent for opted-in follow-up.

I'd be glad to send a free sample of 10 recent LA permitted projects with the contacts. Just reply "sample" and I'll put it together.

Kheizaran
AIFirst Solutions

## Follow-up 1 (day 4)
Subject: (same thread)

Hi {first_name}, quick nudge in case this got buried. The sample is 10 recent LA projects still in plan check, with the engineer of record and any contacts we found, in Excel. No strings. Reply "sample" and it's yours.

Kheizaran

## Follow-up 2 (day 9, last)
Subject: (same thread)

Hi {first_name}, last note from me. One thing the feed catches that bid boards don't: 2025 wildfire rebuilds and hillside grading permits, weeks before a GC is on record. If that's useful to {firm}, reply "sample". If not, no reply needed and I'll close this out.

Kheizaran

## Sample hand-off (on reply "sample")
Subject: (reply in thread) Your sample: 10 LA projects at plan check

Hi {first_name}, here's the sample: 10 recent LA permitted projects, all columns, with the engineer of record and the contacts we found. Rows marked REVIEW are ones where a contact detail came from web search and should be confirmed before you call.

If it's useful, the next step is a 30-day pilot on your own service area. Happy to walk you through it on a 15-minute call. What day works?

Kheizaran

## Reply tags (for the morning job)
- sample: they asked for the sample. Build it, draft the hand-off.
- question: they asked something. Draft an answer from this file and the plan; never invent.
- pilot: they asked about a pilot or pricing. Draft a reply that proposes a 15-minute call; do not quote prices (owner decides).
- no: declined. Mark `status=replied_no`, no further touches.
- bounce: delivery failure. Mark `status=bounced`, list builder finds another address.
- ooo: out-of-office. Ignore, keep cadence.
