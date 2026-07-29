# ValuedHR Launch — Status Handoff (July 27, 2026)

Context file for future Claude chats. Read this first.

## What happened
Revamped ValuedHR around one lead offer to generate first revenue. Lead offer: **Employee Relations**, entry product: **HR Fire Drill** — $495 flat, 60-min session + written action plan in 48 hrs + 1 week email support, credited toward retainer.

## Live & done
- **valuedhr.com/hr-fire-drill.html** — live, deployed via deploy.sh (GitHub → Hostinger auto-pull).
- **Stripe (live mode):** product `prod_Uxo8DJyO7fViMl`, price `price_1TxsWcJACpKdKLGnW5oO10GC`, payment link `plink_1TxsWlJACpKdKLGnA2YVWAQ9` → https://buy.stripe.com/bJe00kaSGb3Pf8GbzaeQM01. After payment redirects to https://app.reclaim.ai/m/hr-consulting/hr-fire-drill.
- **deploy.sh fixed** — now stages hr-fire-drill.html and detects new files.
- **Refund promise softened** on the page (refund only when Michelle declines the engagement) — edit made in this folder.

## Pending (do next)
1. **Run deploy** to push the refund-promise edit live: `cd "/Users/michellemendez/Documents/Claude/Projects/ValuedHR Website" && bash deploy.sh`
2. **Send warm outreach** — 8 personalized drafts in `warm-outreach-drafts.md` (this folder). Priority: Elaine Marshall, William Frost (call: 707-318-9565), Randy Milbert, Angela Peleschka. Alexandra Crispino = lawyer + works under Angela at Seen → referral-partnership pitch, send after/with Angela's.
3. **Post Facebook + LinkedIn announcements** (Facebook copy in chat history; LinkedIn post in `outreach-kit.md`).
4. **Create Fire Drill intake form** (page promises one — Google Form OK).
5. **Homepage edits** to index.html per `revamp-and-launch-plan.md` (Fire Drill CTA in hero, trim waitlist offers, remove unverifiable stats "3× faster"/"90% retention", add About Michelle block, add Fire Drill to contact form dropdown).
6. Test the live Stripe button with a real card, then refund from dashboard.

## Known issues
- **Zoho Mail connector:** reads work; create_draft consistently fails (500) — likely missing compose scope. Don't retry blindly; drafts are copy-paste from warm-outreach-drafts.md.
- **Zoho CRM connector:** no record/lead creation tools available.
- **valuedhr-content skill is outdated** (describes freelance/offshore positioning; site is people-first HR). Follow the live site's positioning.
- Laila Martinez's email in "Clients contact list.xlsx" has a trailing space.

## Key contacts (from client list + inbox)
Clients: Elaine Marshall (elainemarshall1111@gmail.com), William Frost (awakeheart@yahoo.com — mengettingreal.com), Randy Milbert (randy.milbert@pushpin.us), Angela Peleschka (apeleschka@seen.com), Laila Martinez (martinezlaila06@yahoo.com). Lead/partner: Alexandra Crispino (alexzandramae2017@gmail.com). Collaborators: Julie Matovich, A. Wright (EnsembleIQ). Team: Laila Sarcia (laila@valuedhr.com). Do NOT solicit the MonetizeNow/Mark Patrick team (Michelle's decision).

## Files in this folder
`hr-fire-drill.html` (live page) · `warm-outreach-drafts.md` · `outreach-kit.md` (cold email sequence, LinkedIn scripts, CAN-SPAM footer) · `revamp-and-launch-plan.md` · `deploy.sh`
