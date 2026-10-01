# Mural Pay MCP Server

A production-shaped [Model Context Protocol](https://modelcontextprotocol.io) server for **Mural Pay**,
built by **[7Block Labs](https://7blocklabs.com)**. It makes Mural Pay's API usable directly by AI agents
(Claude, ChatGPT, Cursor) — metered to the caller's own key — instead of leaving it to community wrappers.

Built for the Mural Pay team as a working example of the official MCP server we'd ship & launch for you
(OAuth + per-plan metering + listings in the Claude and ChatGPT directories).

```bash
python -m venv .venv && source .venv/bin/activate && pip install -e .
export MURALPAY_API_KEY=...        # your Mural Pay API key
python -m mural_pay_mcp.server                       # stdio
TRANSPORT=http PORT=8000 python -m mural_pay_mcp.server   # remote
```
Claude Code: `claude mcp add --transport http mural-pay http://localhost:8000/mcp`

API: `https://api.muralpay.com` · docs: https://developers.muralpay.com/docs/overview · auth: Bearer JWT API key (Authorization: Bearer <key>); payout execute also needs transfer-api-key header

## Tools
| Tool | What it does |
|---|---|
| `list_accounts` | List accounts available as payout sources |
| `get_payout_fees` | Estimate fees for a token-to-fiat payout |
| `search_payout_requests` | Search/list payout requests by status |
| `get_payout_request` | Get a payout request and its status |
| `search_account_transactions` | Search transaction history for an account |

Want this hardened (OAuth, metering) and listed in Claude + ChatGPT? **[7Block Labs](https://7blocklabs.com)**
builds and launches MCP servers for data & API companies. MIT licensed.
