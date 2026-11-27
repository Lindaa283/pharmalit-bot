# PharmaLit Bot

A Discord bot for the **AI Pharma PhD Hub** community. Type `/lit <target>` and get a short, cited literature summary built from recent PubMed abstracts and two different LLMs.

## Features
- `/lit <target>`: searches PubMed for a drug target, drug or topic (e.g. `/lit KRAS G12C`), summarises the abstracts with DeepSeek and GLM separately, then merges both into one summary with PMID citations and PubMed links.
- `/ping`: health check.
- Per-user daily quota (default 3 `/lit` calls per day).
- One-shot server setup script (categories, channels, rules and welcome messages).
- Minimal Discord intents: the bot does not read message content.

## Architecture
```
/lit <target>
   │
   ▼
PubMed E-utilities (ESearch → EFetch)   → titles, abstracts, PMIDs
   │
   ▼
LiteLLM gateway (OpenAI-compatible)     → deepseek-chat, glm-4-flash (independent summaries)
   │
   ▼
Merge step                              → one summary with PMID citations + PubMed links
   │
   ▼
Discord reply
```

## Setup
Requirements: Python 3.10+, a Discord application with a bot token, and an OpenAI-compatible gateway (e.g. [LiteLLM](https://github.com/BerriAI/litellm)) with DeepSeek and GLM models configured.

```bash
git clone https://github.com/<your-username>/pharmalit-bot.git
cd pharmalit-bot
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your own values
python main.py
```

`.env` variables (never commit this file):
| Variable | Description |
|---|---|
| `DISCORD_BOT_TOKEN` | Bot token from the Discord Developer Portal |
| `LLM_GATEWAY_BASE_URL` | Gateway base URL, e.g. `http://127.0.0.1:4000/v1` |
| `LLM_GATEWAY_KEY` | Gateway API key |
| `NCBI_API_KEY` | Optional, for higher PubMed rate limits |

Please follow [NCBI's E-utilities usage guidelines](https://www.ncbi.nlm.nih.gov/books/NBK25497/) and respect rate limits.

## Disclaimer
PharmaLit Bot is a research and learning tool. **It is not medical advice.** LLM summaries can be incomplete or wrong. Always read the cited papers before relying on anything the bot says. Do not submit confidential or patient data.

## Roadmap
- [ ] Daily AI-pharma and frontier-tech feeds posted automatically
- [ ] Choose number of papers and date range in `/lit`
- [ ] Show where models disagree
- [ ] Export full reports
- [ ] Integration with a standalone web literature assistant

## Join the community
Pharma/biotech students, bio-AI PhD applicants and beginner coders welcome: **https://discord.gg/krNMwJzs8**

## License
MIT. See `LICENSE`.

## Free resource
- [Bio-AI PhD Application Toolkit (PDF)](docs/Bio-AI_PhD_Application_Toolkit.pdf): a free guide to applying for funded bio-AI / computational biology PhDs.
