#!/usr/bin/env python3
"""Build dashboard.html from buyers.csv, state.json and log.md. Stdlib only.

Usage: python3 night-shift/dashboard/build_dashboard.py
"""
import csv, json, html, datetime, pathlib, re

HERE = pathlib.Path(__file__).resolve().parent
ROOT = HERE.parent
CSV = ROOT / "buyers.csv"
STATE = HERE / "state.json"
LOG = ROOT / "log.md"
OUT = HERE / "dashboard.html"

TEHRAN = datetime.timezone(datetime.timedelta(hours=3, minutes=30))
now = datetime.datetime.now(TEHRAN)
today = now.date()

rows = list(csv.DictReader(CSV.open(encoding="utf-8")))
state = json.loads(STATE.read_text(encoding="utf-8")) if STATE.exists() else {}
log_text = LOG.read_text(encoding="utf-8") if LOG.exists() else ""

# ---------- derived facts ----------
def count(pred):
    return sum(1 for r in rows if pred(r))

active = [r for r in rows if r["status"] != "excluded"]
tierA = [r for r in active if r["tier"] == "A"]
tierB = [r for r in active if r["tier"] == "B"]
with_email = [r for r in active if r["email"].strip()]
status_order = ["new", "drafted", "sent", "followup1", "followup2", "replied_sample",
                "replied_question", "replied_pilot", "pilot", "customer", "replied_no", "bounced"]
by_status = {s: count(lambda r, s=s: r["status"] == s) for s in status_order}
touched = sum(by_status[s] for s in status_order if s not in ("new", "drafted"))
replied = sum(by_status[s] for s in ("replied_sample", "replied_question", "replied_pilot", "pilot", "customer", "replied_no"))
samples = by_status["replied_sample"] + by_status["replied_pilot"] + by_status["pilot"] + by_status["customer"]

# LinkedIn messages: parsed from the newest pitch/*-linkedin-messages.md
by_id = {r["id"]: r for r in rows}
li_files = sorted((ROOT / "pitch").glob("*-linkedin-messages.md"))
li_file = li_files[-1] if li_files else None
li_templates, li_people = {}, []
if li_file:
    li_text = li_file.read_text(encoding="utf-8")
    for n in ("1", "2"):
        m = re.search(rf"^## Message {n}\b.*?\n(.*?)(?=^## |^---)", li_text, flags=re.M | re.S)
        li_templates[n] = m.group(1).strip() if m else ""
    for wave_m in re.finditer(r"^## Wave (\d)\b.*?\n(.*?)(?=^## |\Z)", li_text, flags=re.M | re.S):
        wave = wave_m.group(1)
        for block in re.split(r"^### ", wave_m.group(2), flags=re.M)[1:]:
            head, _, body = block.partition("\n")
            pid, _, rest = head.partition(" · ")
            who, _, flag = rest.partition(". ")
            url = next((l.strip() for l in body.splitlines() if l.strip().startswith("http")), "")
            note = " ".join(l[2:].strip() for l in body.splitlines() if l.startswith("> "))
            nm = re.match(r"Hi ([^,]+),", note)
            first = nm.group(1) if nm else "there"
            li_people.append({"id": pid.strip(), "wave": wave, "who": who.strip(), "flag": flag.strip(),
                              "url": url, "note": note, "first": first, "row": by_id.get(pid.strip(), {})})

# Follow-ups due today (owner hasn't sent, or night job will draft)
def due(r, col):
    v = r.get(col, "").strip()
    return v and v <= today.isoformat()
followups_due = [r for r in active if r["status"] == "sent" and due(r, "followup1_date")] + \
                [r for r in active if r["status"] == "followup1" and due(r, "followup2_date")]

drafts_ready = state.get("drafts_ready", [])
replies_waiting = state.get("replies_waiting", [])
owner_actions = state.get("owner_actions", [])

export_date = state.get("export_latest_date")
export_age = None
if export_date:
    try:
        export_age = (today - datetime.date.fromisoformat(export_date)).days
    except ValueError:
        export_age = None

# last 6 log entries
entries = re.split(r"^## ", log_text, flags=re.M)[1:]
log_tail = ["## " + e.strip() for e in entries[-6:]][::-1]

def esc(s):
    return html.escape("" if s is None else str(s))

# ---------- render ----------
STATUS_LABEL = {
    "new": "New", "drafted": "Draft ready", "sent": "Sent", "followup1": "Follow-up 1",
    "followup2": "Follow-up 2", "replied_sample": "Asked for sample", "replied_question": "Asked a question",
    "replied_pilot": "Pilot talk", "pilot": "Pilot", "customer": "Customer", "replied_no": "Declined",
    "bounced": "Bounced", "excluded": "Excluded",
}
STATUS_KIND = {
    "new": "muted", "drafted": "accent", "sent": "info", "followup1": "info", "followup2": "info",
    "replied_sample": "good", "replied_question": "good", "replied_pilot": "good", "pilot": "good",
    "customer": "good", "replied_no": "bad", "bounced": "bad", "excluded": "muted",
}

def pill(status):
    return f'<span class="pill pill-{STATUS_KIND.get(status,"muted")}">{esc(STATUS_LABEL.get(status,status))}</span>'

def kpi(label, value, sub=""):
    return f'<div class="kpi"><div class="kpi-v">{esc(value)}</div><div class="kpi-l">{esc(label)}</div>{"<div class=kpi-s>"+esc(sub)+"</div>" if sub else ""}</div>'

def copy_block(label, text, key):
    return (f'<div class="msg"><div class="msg-h"><span>{esc(label)}</span>'
            f'<span class="mono small muted">{len(text)} chars</span>'
            f'<button type="button" class="copy" data-copy="{esc(key)}">Copy</button></div>'
            f'<div class="msg-t" id="{esc(key)}">{esc(text)}</div></div>')

def li_timing(p):
    if p["wave"] == "1":
        return '<span class="pill pill-accent">send today</span>'
    r = p["row"]
    if r.get("status") == "drafted":
        return '<span class="pill pill-warn">wait: email not sent yet</span>'
    ft = r.get("first_touch_date", "")
    try:
        after = (datetime.date.fromisoformat(ft) + datetime.timedelta(days=3)).isoformat()
        return f'<span class="pill pill-info">from {esc(after)}</span>'
    except ValueError:
        return '<span class="pill pill-muted">after the email</span>'

def li_person(p):
    k = f'li{esc(p["id"])}'
    m1 = li_templates.get("1", "").replace("{first_name}", p["first"])
    m2 = li_templates.get("2", "").replace("{first_name}", p["first"])
    flag = f'<p class="flag small">{esc(p["flag"])}</p>' if p["flag"] else ""
    link = f'<a href="{esc(p["url"])}" target="_blank" rel="noopener">Open profile</a>' if p["url"] else ""
    check = ' <span class="pill pill-warn">check first</span>' if p["flag"] else ""
    return (f'<details class="li" data-id="{esc(p["id"])}"><summary>'
            f'<label class="done"><input type="checkbox" data-done="{esc(p["id"])}"> sent</label>'
            f'<span class="mono small muted">{esc(p["id"])}</span> <strong>{esc(p["who"])}</strong> {li_timing(p)}{check}</summary>'
            f'<div class="li-body"><p class="small" style="margin:0 0 8px">{link}</p>{flag}'
            f'{copy_block("Connection note (Connect → Add a note)", p["note"], k + "n")}'
            f'{copy_block("Message 1: after they accept", m1, k + "a")}'
            f'{copy_block("Message 2: day 5, no reply (last)", m2, k + "b")}'
            f'</div></details>')

def li_wave(w):
    ps = [p for p in li_people if p["wave"] == w]
    return "".join(li_person(p) for p in ps) if ps else '<p class="muted">None.</p>'

def draft_item(d):
    url = d.get("viewUrl") or ""
    firm = esc(d.get("firm", ""))
    subj = esc(d.get("subject", ""))
    to = esc(d.get("to", ""))
    link = f'<a href="{esc(url)}" target="_blank" rel="noopener">open draft</a>' if url else '<span class="muted">draft id logged</span>'
    return f'<li><strong>{firm}</strong> <span class="muted">→ {to}</span><br><span class="muted">{subj}</span> · {link}</li>'

def reply_item(d):
    url = d.get("viewUrl") or ""
    link = f'<a href="{esc(url)}" target="_blank" rel="noopener">open thread</a>' if url else ""
    return f'<li><strong>{esc(d.get("firm",""))}</strong> {pill(d.get("status","replied_question"))} <span class="muted">{esc(d.get("summary",""))}</span> {link}</li>'

def table_rows():
    out = []
    for r in sorted(active, key=lambda r: (status_order.index(r["status"]) if r["status"] in status_order else 99, -int(r["score"] or 0), int(r["id"]))):
        contact = r["contact_name"] or "—"
        email = r["email"] or "—"
        li = f'<a href="{esc(r["linkedin_person"])}" target="_blank" rel="noopener">in</a>' if r["linkedin_person"].strip() else ""
        out.append(
            f'<tr data-tier="{esc(r["tier"])}" data-status="{esc(r["status"])}">'
            f'<td class="mono">{esc(r["id"])}</td>'
            f'<td><div class="firm">{esc(r["firm"])}</div><div class="muted small">{esc(r["city"])}</div></td>'
            f'<td><span class="tier tier-{esc(r["tier"])}">{esc(r["tier"])}</span> <span class="mono small">{esc(r["score"])}</span></td>'
            f'<td>{esc(contact)}<div class="muted small">{esc(r["title"])}</div></td>'
            f'<td class="small">{esc(email)} {li}</td>'
            f'<td>{pill(r["status"])}</td>'
            f'<td class="mono small">{esc(r["first_touch_date"] or "")}</td>'
            f'<td class="small notes">{esc(r["notes"])}</td>'
            f'</tr>')
    return "\n".join(out)


def render_log():
    if not log_tail:
        return '<p class="muted">No runs yet.</p>'
    parts = []
    for e in log_tail:
        lines = e.split("\n")
        head = esc(lines[0].lstrip("# ").strip())
        items = "".join("<li>" + esc(l.lstrip("- ").strip()) + "</li>" for l in lines[1:] if l.strip())
        parts.append("<div><h3>" + head + "</h3><ul>" + items + "</ul></div>")
    return "".join(parts)

export_line = ""
if export_date:
    age_txt = f"{export_age} days old" if export_age is not None else ""
    kind = "bad" if (export_age or 0) > 14 else ("warn" if (export_age or 0) > 7 else "good")
    export_line = f'<span class="pill pill-{kind}">Enriched export: {esc(export_date)} · {age_txt}</span> <span class="muted small">{esc(state.get("export_note",""))}</span>'

night = state.get("night_run_at") or "not yet"
morning = state.get("morning_run_at") or "not yet"
sending = state.get("sending_mode", "drafts only")

page = f"""<title>Permit Pipeline</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@500;600;700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root{{
  --bg:#F2F4F6; --surface:#FFFFFF; --surface-2:#E9EDF0; --text:#172026; --muted:#5B6B76; --line:#D6DDE3;
  --accent:#1F5FA8; --accent-ink:#FFFFFF; --good:#2E7D4F; --warn:#B8770F; --bad:#B3261E; --info:#4B5D6B;
  --good-bg:#E3F1E8; --warn-bg:#FBEFD9; --bad-bg:#F9E3E1; --info-bg:#E6EBEF; --accent-bg:#E0EAF6;
  --radius:6px;
}}
@media (prefers-color-scheme: dark){{ :root:not([data-theme="light"]){{
  --bg:#0F1519; --surface:#17202A; --surface-2:#1F2A35; --text:#E6EBEF; --muted:#93A1AB; --line:#2A3640;
  --accent:#6FA8E8; --accent-ink:#0F1519; --good:#7BC494; --warn:#E3B04B; --bad:#EF8A80; --info:#A7B6C2;
  --good-bg:#1B3325; --warn-bg:#3A2E12; --bad-bg:#3E1C19; --info-bg:#22303A; --accent-bg:#1C2F45;
  color-scheme: dark; }} }}
:root[data-theme="dark"]{{
  --bg:#0F1519; --surface:#17202A; --surface-2:#1F2A35; --text:#E6EBEF; --muted:#93A1AB; --line:#2A3640;
  --accent:#6FA8E8; --accent-ink:#0F1519; --good:#7BC494; --warn:#E3B04B; --bad:#EF8A80; --info:#A7B6C2;
  --good-bg:#1B3325; --warn-bg:#3A2E12; --bad-bg:#3E1C19; --info-bg:#22303A; --accent-bg:#1C2F45;
  color-scheme: dark; }}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 "IBM Plex Sans",system-ui,sans-serif;padding-block:0 40px;padding-inline:16px}}
a{{color:var(--accent)}}
a:focus-visible,button:focus-visible{{outline:2px solid var(--accent);outline-offset:2px}}
.wrap{{max-width:1180px;margin:0 auto}}
header{{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--line);padding:14px 0 10px;margin-bottom:18px;display:flex;flex-wrap:wrap;gap:8px 20px;align-items:baseline}}
h1{{font:700 26px/1.1 "IBM Plex Sans Condensed",sans-serif;margin:0;letter-spacing:.01em;text-wrap:balance}}
h2{{font:600 17px/1.2 "IBM Plex Sans Condensed",sans-serif;margin:0 0 10px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted)}}
.stamp{{font:500 13px "IBM Plex Mono",monospace;color:var(--muted)}}
.grid{{display:grid;gap:16px}}
.grid-2{{grid-template-columns:repeat(auto-fit,minmax(300px,1fr))}}
.card{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:16px}}
.card.alert{{border-left:5px solid var(--bad)}}
.card.act{{border-left:5px solid var(--accent)}}
ul{{margin:0;padding-left:18px}} li{{margin:6px 0;overflow-wrap:anywhere}}
.kpis{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px;margin:18px 0}}
.kpi{{background:var(--surface);border:1px solid var(--line);border-radius:var(--radius);padding:12px 14px}}
.kpi-v{{font:600 28px/1 "IBM Plex Mono",monospace;font-variant-numeric:tabular-nums}}
.kpi-l{{font-size:12px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin-top:6px}}
.kpi-s{{font-size:12px;color:var(--muted)}}
.pill{{display:inline-block;padding:2px 8px;border-radius:999px;font-size:12px;font-weight:500;white-space:nowrap;border:1px solid transparent}}
.pill-good{{background:var(--good-bg);color:var(--good)}} .pill-warn{{background:var(--warn-bg);color:var(--warn)}}
.pill-bad{{background:var(--bad-bg);color:var(--bad)}} .pill-info{{background:var(--info-bg);color:var(--info)}}
.pill-accent{{background:var(--accent-bg);color:var(--accent)}} .pill-muted{{background:var(--surface-2);color:var(--muted)}}
.tier{{display:inline-block;width:22px;height:22px;line-height:22px;text-align:center;border-radius:4px;font:600 12px "IBM Plex Mono",monospace}}
.tier-A{{background:var(--accent);color:var(--accent-ink)}} .tier-B{{background:var(--surface-2);color:var(--text)}} .tier-C{{background:var(--surface-2);color:var(--muted)}}
.muted{{color:var(--muted)}} .small{{font-size:12.5px}} .mono{{font-family:"IBM Plex Mono",monospace;font-variant-numeric:tabular-nums}}
.filters{{display:flex;flex-wrap:wrap;gap:6px;margin:0 0 10px}}
.filters button{{background:var(--surface-2);color:var(--text);border:1px solid var(--line);border-radius:999px;padding:4px 12px;font:500 13px "IBM Plex Sans",sans-serif;cursor:pointer}}
.filters button[aria-pressed="true"]{{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}}
.tablewrap{{overflow-x:auto;border:1px solid var(--line);border-radius:var(--radius);background:var(--surface)}}
table{{border-collapse:collapse;width:100%;min-width:900px;font-size:13.5px}}
th{{text-align:left;font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);padding:10px 10px;border-bottom:1px solid var(--line);background:var(--surface-2);position:sticky;top:0}}
td{{padding:9px 10px;border-bottom:1px solid var(--line);vertical-align:top}}
tr[hidden]{{display:none}}
.firm{{font-weight:500}} .notes{{max-width:340px;color:var(--muted)}}
.log{{font-size:13px}} .log h3{{font:600 14px "IBM Plex Sans Condensed",sans-serif;margin:12px 0 4px}}
.log ul{{color:var(--muted)}}
footer{{margin-top:24px;color:var(--muted);font-size:12.5px}}
.wave{{font:600 14px "IBM Plex Sans Condensed",sans-serif;margin:0 0 8px}}
details.li{{border:1px solid var(--line);border-radius:var(--radius);margin:0 0 8px;background:var(--surface)}}
details.li summary{{cursor:pointer;padding:10px 12px;display:flex;flex-wrap:wrap;gap:6px 8px;align-items:center;list-style:none}}
details.li summary::-webkit-details-marker{{display:none}}
details.li[open] summary{{border-bottom:1px solid var(--line)}}
details.li.is-done summary strong{{text-decoration:line-through;color:var(--muted)}}
.done{{font-size:12px;color:var(--muted);display:inline-flex;gap:4px;align-items:center}}
.li-body{{padding:10px 12px}}
.flag{{background:var(--warn-bg);color:var(--warn);padding:6px 10px;border-radius:4px;margin:0 0 10px}}
.msg{{margin:0 0 10px}}
.msg-h{{display:flex;gap:8px;align-items:center;font-size:12px;text-transform:uppercase;letter-spacing:.05em;color:var(--muted);margin-bottom:4px}}
.msg-h span:first-child{{flex:1}}
.msg-t{{white-space:pre-wrap;background:var(--surface-2);border-radius:4px;padding:8px 10px;font-size:13.5px}}
.copy{{background:var(--accent);color:var(--accent-ink);border:0;border-radius:4px;padding:3px 10px;font:500 12px "IBM Plex Sans",sans-serif;cursor:pointer;text-transform:none;letter-spacing:0}}
@media (prefers-reduced-motion: no-preference){{ .filters button{{transition:background .15s}} }}
</style>

<div class="wrap">
<header>
  <h1>Permit Pipeline</h1>
  <span class="stamp">{esc(now.strftime('%a %d %b %Y · %H:%M'))} Tehran</span>
  <span class="stamp">night run: {esc(night)} · morning run: {esc(morning)}</span>
  <span class="pill pill-{'warn' if sending=='drafts only' else 'good'}">sending: {esc(sending)}</span>
</header>

<section class="grid grid-2">
  <div class="card alert">
    <h2>Only you can do these</h2>
    {"<ul>" + "".join(f"<li>{esc(a)}</li>" for a in owner_actions) + "</ul>" if owner_actions else '<p class="muted">Nothing waiting on you.</p>'}
    <p style="margin:10px 0 0">{export_line}</p>
  </div>
  <div class="card act">
    <h2>Drafts ready to send · {len(drafts_ready)}</h2>
    {"<ul>" + "".join(draft_item(d) for d in drafts_ready) + "</ul>" if drafts_ready else '<p class="muted">No drafts waiting. The night job creates them at 01:00 Tehran.</p>'}
    {("<p class=small style='margin:10px 0 0'>Follow-ups due today: " + ", ".join(esc(r['firm']) for r in followups_due) + "</p>") if followups_due else ""}
  </div>
  <div class="card act">
    <h2>Replies waiting · {len(replies_waiting)}</h2>
    {"<ul>" + "".join(reply_item(d) for d in replies_waiting) + "</ul>" if replies_waiting else '<p class="muted">No new replies. The morning job checks Gmail at 07:00 Tehran.</p>'}
  </div>
</section>

<section class="card act" style="margin-top:16px" id="linkedin">
  <h2>LinkedIn messages · {len(li_people)} people</h2>
  <p class="small muted" style="margin:0 0 10px">Send by hand from your LinkedIn. Tap a name, open the profile, then Connect → Add a note → paste. When they accept, send Message 1; if no reply in 5 days, send Message 2. The "sent" tick is saved only in this browser, so tell Claude who you sent to. Source: {esc(li_file.name if li_file else "none")}</p>
  <div class="grid grid-2">
    <div><h3 class="wave">Wave 1 · first touch, send today</h3>{li_wave("1")}</div>
    <div><h3 class="wave">Wave 2 · 3+ days after their email is sent</h3>{li_wave("2")}</div>
  </div>
</section>

<div class="kpis">
  {kpi("Firms in play", len(active), f"{len(tierA)} A · {len(tierB)} B")}
  {kpi("With an email", len(with_email), f"{len(active)-len(with_email)} still to find")}
  {kpi("Drafted", by_status['drafted'])}
  {kpi("Touched", touched, "sent or later")}
  {kpi("Replied", replied)}
  {kpi("Sample asks", samples)}
  {kpi("Pilots", by_status['pilot'] + by_status['customer'])}
</div>

<section class="card">
  <h2>Pipeline · {len(active)} firms</h2>
  <div class="filters" id="filters">
    <button type="button" data-f="all" aria-pressed="true">All</button>
    <button type="button" data-f="tier:A" aria-pressed="false">Tier A</button>
    <button type="button" data-f="tier:B" aria-pressed="false">Tier B</button>
    <button type="button" data-f="status:new" aria-pressed="false">New</button>
    <button type="button" data-f="status:drafted" aria-pressed="false">Draft ready</button>
    <button type="button" data-f="status:sent" aria-pressed="false">Sent</button>
    <button type="button" data-f="replied" aria-pressed="false">Replied</button>
  </div>
  <div class="tablewrap">
  <table id="pipe">
    <thead><tr><th>#</th><th>Firm</th><th>Tier</th><th>Contact</th><th>Email</th><th>Status</th><th>First touch</th><th>Notes</th></tr></thead>
    <tbody>
{table_rows()}
    </tbody>
  </table>
  </div>
</section>

<section class="card log" style="margin-top:16px">
  <h2>Run log · latest first</h2>
  {render_log()}
</section>

<footer>Data: night-shift/buyers.csv on branch claude/customer-acquisition-strategy-rn7eod. Generated {esc(now.isoformat(timespec='minutes'))}. Drafts live in Gmail; nothing is sent by the night shift.</footer>
</div>

<script>
(function(){{
  var btns=document.querySelectorAll('#filters button');
  var rows=document.querySelectorAll('#pipe tbody tr');
  var replied=['replied_sample','replied_question','replied_pilot','pilot','customer','replied_no'];
  var saved=null; try{{saved=localStorage.getItem('pp-filter')}}catch(e){{}}
  function apply(f){{
    btns.forEach(function(b){{b.setAttribute('aria-pressed', b.dataset.f===f ? 'true':'false')}});
    rows.forEach(function(r){{
      var show=true;
      if(f==='all') show=true;
      else if(f.indexOf('tier:')===0) show=r.dataset.tier===f.slice(5);
      else if(f.indexOf('status:')===0) show=r.dataset.status===f.slice(7);
      else if(f==='replied') show=replied.indexOf(r.dataset.status)>=0;
      r.hidden=!show;
    }});
    try{{localStorage.setItem('pp-filter',f)}}catch(e){{}}
  }}
  btns.forEach(function(b){{b.addEventListener('click',function(){{apply(b.dataset.f)}})}});
  apply(saved||'all');

  document.querySelectorAll('button.copy').forEach(function(b){{
    b.addEventListener('click',function(e){{
      e.preventDefault();
      var el=document.getElementById(b.dataset.copy); if(!el) return;
      var t=el.textContent;
      function ok(){{b.textContent='Copied'; setTimeout(function(){{b.textContent='Copy'}},1500)}}
      function fallback(){{var r=document.createRange(); r.selectNodeContents(el); var s=window.getSelection(); s.removeAllRanges(); s.addRange(r); try{{document.execCommand('copy'); ok()}}catch(x){{b.textContent='Select + copy'}}}}
      try{{navigator.clipboard.writeText(t).then(ok,fallback)}}catch(x){{fallback()}}
    }});
  }});
  var done={{}}; try{{done=JSON.parse(localStorage.getItem('pp-li-done')||'{{}}')}}catch(e){{done={{}}}}
  document.querySelectorAll('input[data-done]').forEach(function(c){{
    var id=c.dataset.done, d=c.closest('details');
    c.checked=!!done[id]; d.classList.toggle('is-done',c.checked);
    c.addEventListener('click',function(e){{e.stopPropagation()}});
    c.addEventListener('change',function(){{
      done[id]=c.checked; d.classList.toggle('is-done',c.checked);
      try{{localStorage.setItem('pp-li-done',JSON.stringify(done))}}catch(e){{}}
    }});
  }});
}})();
</script>
"""
OUT.write_text(page, encoding="utf-8")
print(f"wrote {OUT} ({len(page)//1024} KB): {len(active)} active firms, {len(drafts_ready)} drafts ready, {len(replies_waiting)} replies waiting")
