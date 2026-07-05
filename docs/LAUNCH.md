# Divvy — Launch & Marketing Kit

> Owner playbook for sharing Divvy. **Nothing here is automated** — every post and PR is a
> manual, human action. Disclose that it's your own project, lead with value, and never
> coordinate votes, use alt accounts, or buy stars.
>
> Repo: https://github.com/DanMat/Divvy · MIT · Python 3.12+ · uv
> One-liner: *"Backtest your REAL investing history against a different portfolio and compare the dividends & returns you'd have earned."*

**Golden rules for every channel:**
1. Always disclose it's your own project ("I built this / I'm the author").
2. Lead with value, not a pitch. Answer a real question first; link second.
3. Never post the same copy-paste text to multiple subs on the same day (Reddit filters cross-posting spam).
4. No vote manipulation, no coordinated upvotes, no alt accounts, no buying stars — all bannable and off-limits.
5. Reply to every early comment fast — the first 60 minutes drive the whole thread's reach.

---

## 1. Launch strategy — ranked channels, rules, timing

Ranking logic: audience fit × how welcoming the venue is to a genuinely useful free/OSS tool × traffic quality (people who'll actually try it and star it).

### Tier 1 — highest fit, do these first

**#1 — Hacker News "Show HN"**
- *Why:* The single best venue for an OSS dev tool that's actually usable. Sends real developers who star repos.
- *Rules/etiquette:* Title must start with `Show HN:` and describe plainly what it is — no hype, no exclamation marks, no site names. Reader must be able to *try it themselves* (Divvy qualifies: `uv run` quickstart with synthetic data, no signup). Post from your own account, be present in the thread. First comment (from you) adds context that doesn't fit the title. Being transparent it's your project is expected. Don't resubmit repeatedly.
- *Timing (US):* Tue–Thu, ~8–10am Pacific. Timing is minor vs. title clarity and your responsiveness.

**#2 — r/dividends** (the bullseye audience)
- *Why:* Divvy's headline metric (dividend income, lifetime + trailing-12-mo run-rate, DRIP) is exactly this sub's obsession.
- *Rules/etiquette:* Read the sidebar + rules the day you post — check for a self-promotion/"tools" rule, required flair, and any "no blogspam/no referral links" rule. Divvy's strongest asset: no paywall, no affiliate links, no data harvesting (all local). Frame as "I built a free, open-source, privacy-first tool to answer X for myself" and *show a concrete result*. If there's a weekly self-promo thread, prefer it; if unsure, a one-line courtesy DM to mods buys goodwill.
- *Timing (US):* Weekday mornings ~6–9am ET (pre-market). Tue–Thu strongest.

**#3 — r/Python**
- *Why:* Developers who'll appreciate the uv/CLI/Streamlit stack and are quick to star.
- *Rules/etiquette:* Friendly to substantive project shares; low-effort "check out my thing" posts get removed. Lead with what's technically interesting (replaying a real cash-flow calendar, XIRR, DRIP engine, local-first design), not finance marketing. Include the repo link and a CLI snippet. Use the weekly showcase thread if a standalone post isn't allowed.
- *Timing (US):* Weekday mornings ET; showcase thread early in its life.

### Tier 2 — strong fit, more etiquette-sensitive

**#4 — r/financialindependence / r/Fire / r/Bogleheads-adjacent**
- *Why:* FIRE people care about "how much to invest monthly to reach $X/month in dividends" — Divvy's projection tool speaks directly to this.
- *Rules/etiquette:* r/financialindependence is strict and funnels most content into its Daily Discussion thread. Safest: help inside the Daily thread when someone asks, or post a value-first "how I modeled my dividend runway" story with the repo as a footnote. Confirm the rules first. Never drop a bare repo link.

**#5 — r/algotrading**
- *Why:* Appreciates the backtesting engine, XIRR, and data-adapter architecture.
- *Rules/etiquette:* Has rules against low-effort self-promo; the post should teach something. Angle: "how I built a real-cash-flow (money-weighted) backtester and why time-weighted returns mislead dividend investors."

**#6 — r/opensource**
- *Why:* Explicitly welcomes "I made this OSS thing" posts.
- *Rules/etiquette:* Among the most self-promo-friendly; still wants genuine OSS (license, CONTRIBUTING, open issues — Divvy has all). Emphasize MIT, privacy-first/local, and "contributions welcome (broker adapters, importers)."

### Tier 3 — amplification / long-tail

- **#7 — X/Twitter:** launch thread; tag fintech/FIRE/#Python/#buildinpublic. Weekday 9am–12pm or ~5–6pm ET.
- **#8 — LinkedIn:** one polished post; put the link in the first comment.
- **#9 — r/investing:** huge but promo-averse; only as a value-first methodology post or within an allowed thread, after the dividend-specific subs.
- **#10 — Discords/forums:** Bogleheads.org (strict — answer threads, don't advertise), FIRE Discords, the Streamlit community.

**Sequencing (over ~2 weeks, never same-day duplicate):**
Day 1 (Tue): Show HN + X thread + LinkedIn. Day 3 (Thu): r/dividends. Day 6 (Tue): r/Python. Day 8 (Thu): r/opensource. Then r/algotrading / FIRE / r/investing across the following week, each tailored. Submit awesome-lists (Section 3) in parallel.

---

## 2. Ready-to-paste drafts

### 2a. Show HN

**Title (pick one — plain, no hype):**
- `Show HN: Divvy – Backtest your real investing history against a different portfolio`
- `Show HN: Divvy – Replay your actual contributions into any portfolio and compare dividends`

**Body:**

> I built Divvy to answer a question every backtester I tried answered badly: "What if I'd put *my actual money* — the same dates and dollar amounts I really invested — into a different set of holdings?"
>
> Tools like Portfolio Visualizer simulate a synthetic "$500/month." Divvy instead replays your real contribution calendar (from a Fidelity ledger export, a generic `date,amount` CSV, or a 1099 dividend importer) into any hypothetical basket of ETFs/stocks, with dividend reinvestment (DRIP). It reports dividend income as a first-class metric — lifetime and trailing-12-month run-rate — plus total return and money-weighted XIRR, so you're comparing apples to apples against what you actually did.
>
> It has a CLI, an interactive local Streamlit "Portfolio Experiment Lab" (add/remove tickers, drag weight sliders, compare live with charts), and a forward-projection tool ("how much must I invest monthly to reach $X/month in dividends?") with a Monte Carlo range.
>
> Privacy-first: all financial data stays on your machine — nothing is uploaded or committed. Python 3.12+, uses uv, MIT.
>
> You can try it in ~30 seconds with zero data using the synthetic quickstart:
>
> ```
> uv run divvy compare --synthetic-monthly 500 --synthetic-start 2019-01-01 \
>   --bucket examples/buckets/dividend_etf_core.yaml \
>   --bucket examples/buckets/high_yield_tilt.yaml
> ```
>
> Repo: https://github.com/DanMat/Divvy
>
> Big caveat, stated up front and in the README: this is a backtest, not investment advice — past performance says nothing about the future.
>
> I'd love feedback on the return methodology (money-weighted vs. time-weighted for cash-flow-heavy accounts), and on which broker/importer adapters to build next.

---

### 2b. Reddit — r/dividends

**Title:**
`I built a free, open-source tool that replays your REAL contribution history into a different portfolio, so you can see the dividends you'd have earned`

**Body:**

> Full disclosure: this is my own project and it's free + open source (MIT), no signup, no ads, nothing uploaded — everything runs locally. Mods, happy to move this to a weekly thread if that's the norm here.
>
> Like a lot of you, I kept wondering "what if I'd been buying SCHD/DGRO/VYM this whole time instead of what I actually bought?" Every backtester I found made me pretend I'd invested a clean "$X/month," which isn't how anyone's contributions actually look — real life is lumpy dates and amounts.
>
> So I built **Divvy**. You feed it your actual contribution calendar (a Fidelity ledger export, a plain `date,amount` CSV, or a 1099 dividend import) and it replays those exact dollars, on those exact dates, into whatever basket of tickers you want — with DRIP. Then it shows you, side by side:
> - **Dividend income** — lifetime and trailing-12-month run-rate (first-class metric, not an afterthought)
> - **Total return**
> - **Money-weighted XIRR** (so lumpy contributions are handled honestly)
> - **Risk** — max drawdown and volatility, plus an SPY benchmark row
>
> There's a CLI and an interactive local "Portfolio Experiment Lab" where you add/remove tickers, drag weight sliders, and watch the numbers update live. There's also a projection tool: "how much do I need to invest per month to hit $X/month in dividends?" (with a Monte Carlo range, not a single fake-precise number).
>
> You can try it with zero data first (synthetic mode) to kick the tires.
>
> Repo: https://github.com/DanMat/Divvy
>
> Obligatory and sincere: **this is a backtester, not investment advice.** Past performance tells you nothing about the future.
>
> Would genuinely love feedback: what dividend metrics do you most want compared, and which brokers should I add import adapters for next?

---

### 2c. Reddit — r/opensource

**Title:**
`Divvy – MIT-licensed, privacy-first Python tool to backtest your real investing history against a different portfolio (CLI + Streamlit)`

**Body:**

> I made **Divvy**, an open-source (MIT, Python 3.12+, uv) tool for a niche I couldn't find good software for: replaying your *actual* investment contributions — real dates and dollar amounts from your broker export — into a hypothetical portfolio, so you can compare the dividends and total return you'd have earned.
>
> Why it might interest this sub:
> - **Privacy-first / local-only:** all financial data stays on your machine. Nothing uploaded, nothing committed (sensitive dirs gitignored). No accounts, no telemetry.
> - **Real cash-flow modeling:** genuine contribution calendar + money-weighted XIRR + DRIP, instead of the usual synthetic "$X/month."
> - **Two interfaces:** a CLI and an interactive local Streamlit "Experiment Lab."
> - **Pluggable data adapters:** Fidelity ledger, generic `date,amount` CSV, 1099 importer — exactly where I'd love contributions (more broker adapters). There's a documented adapter template.
>
> Repo (quickstart, CONTRIBUTING, and a clear "backtest, not investment advice" disclaimer): https://github.com/DanMat/Divvy
>
> Feedback on architecture and good-first-issue ideas very welcome.

---

### 2d. X / Twitter — launch thread

**1 (hook + link):**
> I built Divvy: an open-source tool that replays your REAL investing history — the actual dates and dollars you contributed — into a *different* portfolio, so you can see the dividends & returns you'd have earned.
>
> Free, local, MIT. 🧵
> github.com/DanMat/Divvy

**2 (the wedge):**
> Every backtester makes you pretend you invested a tidy "$500/month."
>
> Nobody's contributions look like that.
>
> Divvy uses your genuine, lumpy contribution calendar (Fidelity export, a date,amount CSV, or a 1099 import) and DRIPs it into any basket you choose.

**3 (the metric that matters):**
> It treats DIVIDEND INCOME as a first-class metric:
> • lifetime dividends
> • trailing-12-month run-rate
> • total return
> • money-weighted XIRR (honest math for lumpy cash flows)
> • max drawdown + an SPY benchmark

**4 (the fun part):**
> There's a CLI + an interactive local "Portfolio Experiment Lab" (Streamlit): add/remove tickers, drag weight sliders, watch dividends & returns update live.
>
> Plus a projection tool with a Monte Carlo range: "how much/month to reach $X/month in dividends?"
>
> [attach demo GIF]

**5 (trust + CTA):**
> Privacy-first: your financial data never leaves your machine. Nothing uploaded, nothing committed.
>
> And yes — this is a backtest, not investment advice. Past ≠ future.
>
> Try the zero-data quickstart, and a ⭐ helps a ton:
> github.com/DanMat/Divvy

*(Hashtags to sprinkle, not spam: #Python #dividends #FIRE #investing #opensource #buildinpublic)*

---

### 2e. LinkedIn

> I just open-sourced a side project: **Divvy**.
>
> It answers a question I could never get a straight answer to: *"What if I'd invested my actual money — the same dates, the same amounts — into a different portfolio?"*
>
> Most backtesters simulate a clean "$X/month." Real contributions are lumpy. Divvy replays your genuine contribution calendar (from a broker export or a simple CSV) into any basket of ETFs/stocks, reinvests dividends, and reports the numbers dividend and FIRE investors actually care about: lifetime dividend income, trailing-12-month run-rate, total return, and money-weighted XIRR.
>
> It's got a CLI, an interactive local "Portfolio Experiment Lab," and a projection tool for "how much must I invest monthly to reach $X/month in dividends?"
>
> Free, MIT-licensed, Python, and privacy-first — all your financial data stays on your own machine.
>
> One honest caveat, front and center: it's a backtester, not investment advice. Past performance is not predictive.
>
> Repo + quickstart in the comments. Feedback and contributions welcome. 👇
>
> *(put the GitHub link in the first comment — LinkedIn suppresses reach on posts with outbound links in the body)*

---

## 3. "Awesome" lists & directories (owner opens the PRs)

For each: fork → add one section-appropriate line → open a PR ("Adds Divvy, an MIT-licensed tool for X"). Follow each list's CONTRIBUTING format (many require a specific bullet style and a passing `awesome-lint`). Verify each list still exists and read its rules first.

1. **wilsonfreitas/awesome-quant** — section **"Trading & Backtesting"**.
   `[Divvy](https://github.com/DanMat/Divvy) - Replay your real contribution history (broker export / CSV / 1099) into a hypothetical portfolio and compare dividends, total return, and money-weighted XIRR with DRIP. Local-first, MIT.`
2. **vinta/awesome-python** — closest data/finance grouping.
   `* [Divvy](https://github.com/DanMat/Divvy) - Backtest your real investing history against a different portfolio and compare dividends and returns.`
3. **awesome-fintech / awesome-investing / awesome-dividend lists** (search GitHub topics) — Tools/Backtesting heading.
   `[Divvy](https://github.com/DanMat/Divvy) - Open-source, privacy-first backtester that replays your actual contributions into any ETF/stock basket, with dividend income (lifetime + TTM run-rate), total return, and XIRR.`
4. **MarcSkovMadsen/awesome-streamlit** + the Streamlit community "Show the community".
   `[Divvy Portfolio Experiment Lab](https://github.com/DanMat/Divvy) - Interactive local app to compare portfolios by dividends and returns using your real contribution history.`
5. **agarrharr/awesome-cli-apps** — finance/utility section.
   `[Divvy](https://github.com/DanMat/Divvy) - Backtest your real investing history against a different portfolio from the command line.`

---

## 4. Pre-launch checklist

**Already done:**
- ✅ Clear one-liner + "why it's different" paragraph (real-ledger replay vs. synthetic)
- ✅ Badges (CI, MIT, Python 3.12+, uv); hero screenshot (`docs/experiment-lab.png`)
- ✅ Zero-data quickstart; metrics legend; data-source + privacy sections
- ✅ Prominent "backtest, not advice" disclaimer; CONTRIBUTING + MIT + example data
- ✅ Repo topics set; Issues + Discussions enabled
- ✅ PyPI-ready (`divvy-backtest`) with a release-triggered publish workflow
- ✅ Broker-adapter template for contributors

**Gaps to fill (ranked by impact):**
1. **Animated demo GIF** — a 10–20s clip of dragging weight sliders and watching numbers update live is the single highest-converting asset for a visual tool. Record with synthetic data so nothing personal shows. Put it at the top of the README and attach to the X thread.
2. **Social-preview image** — GitHub Settings → Social preview (1280×640). Without it, HN/Reddit/X/LinkedIn shares show a bland default.
3. **"Good first issues"** — label 3–6 (e.g. "add Schwab adapter," "add Vanguard CSV adapter," "add a dividend metric"). Gives r/Python & r/opensource something to point at.
4. **Pinned "How it works"** — a short architecture note (cash-flow replay + XIRR + DRIP). Devs on HN will ask; answer preemptively.
5. **Cut a v0.1.0 release** the day you launch (and configure the PyPI trusted publisher so the publish workflow runs) — a concrete "launched today" hook that also puts it on PyPI.

---

## 5. Ethical tips to maximize stars/forks (no manipulation)

1. **Ship the demo GIF first** — highest ROI for a visual, interactive tool.
2. **Be the operator, not the advertiser** — answer real questions genuinely; mention Divvy as "I built a thing for this," disclosed.
3. **Front-load the "try it in 30 seconds" path** — the zero-data quickstart is your conversion engine; make sure it works from a clean clone.
4. **Answer every comment in the first hour** — early engagement drives HN/Reddit ranking and shows the project is alive.
5. **Publish good first issues** and say "contributions welcome — broker adapters." Each merged adapter is a new evangelist.
6. **Tailor every post to its venue** — r/dividends cares about run-rate; r/Python about the XIRR/DRIP engine and uv; r/opensource about MIT + privacy.
7. **Lead with the honest disclaimer** — in finance, transparency ("past ≠ future") builds trust and pre-empts the top critical comment.
8. **Turn feedback into visible momentum** — open an issue for each request; when you ship it, reply in the original thread: "you asked, it's live."
9. **Cross-link your own channels, not fake ones** — put HN/Reddit links in your X thread and vice versa; never coordinate votes or use alts.
10. **Give it a "launched" moment** — tag v0.1.0 the day you post; maintain a visible changelog.

---

*Owner action required for all posting/PRs. Nothing in this repo posts or submits anything on your behalf.*
