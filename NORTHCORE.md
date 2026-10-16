# Northcore fork

Fork of [AndyEverything/openproject-mcp-server](https://github.com/AndyEverything/openproject-mcp-server).
Deployed from the `northcore` branch on darpa (10.10.2.67), published at `https://mcp.ncore.se/openproject`.

## Changes vs upstream

| Area | Change |
|---|---|
| HTTP transport | Endpoint path configurable via `MCP_HTTP_PATH` (default `/mcp`) |
| Python | `.python-version` = 3.13; `aiohttp` bumped to 3.14.x (wheels for 3.13 and 3.14, no compiler needed) |
| Work packages | `responsible_id` (Accountable) on create/update |
| Work packages | `estimated_hours` (Work), `remaining_hours`, `duration_days`, `schedule_manually` on create/update; shown in responses |
| Custom fields | `custom_fields` on create/update, keyed by field name or `customFieldN`. List fields take option label or id, user/version fields take ids, `null` clears |
| Custom fields | New tool `list_custom_fields` (by work package, or project + type) with options and current values |
| Attachments | New tools `list_attachments`, `upload_attachment` (text or base64, max 20 MB), `download_attachment` (text, or base64 for binary), `delete_attachment` |

## Deploy (darpa)

```bash
cd ~/openproject-mcp-server
git pull && uv sync && sudo systemctl restart openproject-mcp
```

After a restart, Claude chats need a new chat (or toggle the connector) to pick up new or changed tools.

## Configuration (`.env`)

```ini
OPENPROJECT_URL=https://project.ncore.se
OPENPROJECT_API_KEY=<token of a dedicated OpenProject user>
MCP_HTTP_HOST=0.0.0.0
MCP_HTTP_PORT=8010
MCP_HTTP_PATH=/openproject
```

Access is restricted in pfSense HAProxy to Anthropic's outbound range (`160.79.104.0/21`); everyone else gets 403 on `/openproject`.
