# Security Policy

## Divvy's security model

Divvy is a **local-first** tool. Your financial data (broker exports, contribution CSVs,
cached price data, generated reports) stays on your machine — it is never uploaded, and the
repo's `.gitignore` keeps it out of version control. The only outbound network calls are to
fetch public market price/dividend history from Yahoo Finance (via `yfinance`). Divvy has no
server, no accounts, no telemetry, and asks for no credentials.

The optional Finviz Elite lookups read your API key from a local `.env` (gitignored); it is
never printed or transmitted anywhere except to Finviz.

## Supported versions

Divvy is pre-1.0. Security fixes are applied to the latest release on `main`.

| Version | Supported |
| ------- | --------- |
| latest (`main`) | ✅ |
| older tags | ❌ |

## Reporting a vulnerability

Please **do not** open a public issue for security problems.

- Preferred: use GitHub's **private vulnerability reporting** — go to the repo's **Security**
  tab → **Report a vulnerability**.
- Alternatively, email the maintainer at **dannymatthew@gmail.com**.

Include steps to reproduce and the affected version/commit. You'll get an acknowledgement as
soon as possible, and a fix or mitigation will be coordinated before any public disclosure.

## Scope notes

Divvy is an analysis tool, not investment advice, and it makes no guarantees about the
accuracy of third-party market data. Data-accuracy issues are regular bugs — please file
those as normal GitHub issues.
