"""
Mural Pay MCP Server — a 7Block Labs build for Mural Pay.

A production-shaped Model Context Protocol server over Mural Pay's API (https://developers.muralpay.com/docs/overview). Any MCP client
(Claude, ChatGPT, Cursor, agent frameworks) can use Mural Pay's data directly, metered to the caller's
own key — a first-party, agent-native surface instead of community wrappers Mural Pay can't control.

Auth: Bearer JWT API key (Authorization: Bearer <key>); payout execute also needs transfer-api-key header. Set MURALPAY_API_KEY in the environment to call authed endpoints.
Run (stdio):  python -m mural_pay_mcp.server
Run (remote): TRANSPORT=http PORT=8000 python -m mural_pay_mcp.server
"""
from __future__ import annotations
import os
import httpx
from mcp.server.mcpserver import MCPServer
from mcp.types import ToolAnnotations

API = os.environ.get("MURAL_PAY_API_BASE", "https://api.muralpay.com")   # override base per deployment if needed
UA = "mural-pay-mcp/1.0 (+https://github.com/7BlockLabs/mcp-mural-pay-demo)"
AUTH_STYLE = "bearer"   # bearer | header | raw | saltedge | none
AUTH_HEADER = ""
READ_ONLY = ToolAnnotations(readOnlyHint=True, openWorldHint=True)

mcp = MCPServer("Mural Pay", instructions="Mural Pay data over MCP. Set MURALPAY_API_KEY for authed calls.")

def _auth_headers() -> dict:
    h = {"User-Agent": UA, "Accept": "application/json"}
    key = os.environ.get("MURALPAY_API_KEY")
    if AUTH_STYLE == "none":
        return h
    if AUTH_STYLE == "saltedge":              # App-id + Secret headers (Test/Pending apps)
        if os.environ.get("SALTEDGE_APP_ID"): h["App-id"] = os.environ["SALTEDGE_APP_ID"]
        if os.environ.get("SALTEDGE_SECRET"): h["Secret"] = os.environ["SALTEDGE_SECRET"]
        return h
    if key and AUTH_STYLE == "bearer":
        h["Authorization"] = f"Bearer {key}"
    elif key and AUTH_STYLE == "raw":          # raw token in Authorization (e.g. Cube JWT, no 'Bearer')
        h["Authorization"] = key
    elif key and AUTH_STYLE == "header":
        h[AUTH_HEADER] = key
    return h

async def _call(method: str, path: str, params: dict | None = None, body: dict | None = None) -> dict:
    async with httpx.AsyncClient(timeout=30, headers=_auth_headers()) as c:
        r = await c.request(method, f"{API}{path}", params=params or {}, json=body)
        r.raise_for_status()
        try: return r.json()
        except Exception: return {"raw": r.text[:2000]}

@mcp.tool(title="List Accounts", description="List accounts available as payout sources", annotations=READ_ONLY)
async def list_accounts() -> dict:
    return await _call("GET", "/api/accounts", params={})

@mcp.tool(title="Get Payout Fees", description="Estimate fees for a token-to-fiat payout", annotations=READ_ONLY)
async def get_payout_fees() -> dict:
    return await _call("POST", "/api/payouts/fees/token-to-fiat", params={})

@mcp.tool(title="Search Payout Requests", description="Search/list payout requests by status", annotations=READ_ONLY)
async def search_payout_requests() -> dict:
    return await _call("POST", "/api/payouts/search", params={})

@mcp.tool(title="Get Payout Request", description="Get a payout request and its status", annotations=READ_ONLY)
async def get_payout_request() -> dict:
    return await _call("GET", "/api/payouts/payout/{id}", params={})

@mcp.tool(title="Search Account Transactions", description="Search transaction history for an account", annotations=READ_ONLY)
async def search_account_transactions() -> dict:
    return await _call("POST", "/api/transactions/search/account/{accountId}", params={})


def main() -> None:
    if os.environ.get("TRANSPORT") == "http":
        import uvicorn
        uvicorn.run(mcp.streamable_http_app(), host="0.0.0.0", port=int(os.environ.get("PORT", "8000")))
    else:
        mcp.run()

if __name__ == "__main__":
    main()
