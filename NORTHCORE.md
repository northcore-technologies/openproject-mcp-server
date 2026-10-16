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
| Projects | `custom_fields` on `create_project`/`update_project` for project attributes (e.g. Client, AO); `get_project` shows them; new tool `list_project_attributes` with options |
| Work packages | New tool `get_work_package` (full detail incl. custom fields, backlogs, budget, costs) — missing upstream despite README |
| Backlogs | `story_points`, `sprint_id` on create/update/bulk; new tool `list_sprints` (falls back to versions on older OpenProject). Backlog position is read-only in the API |
| Costs | `budget_id` on create/update/bulk; new tool `list_budgets`; spent time and labor/unit/overall costs shown read-only (cost entries can't be written via API v3) |
| Watchers | New tools `list_watchers`, `add_watcher`, `remove_watcher` |
| Categories | `category_id` on create/update; new tool `list_categories`. Creating categories isn't possible via API v3 (Project settings → Work packages → Categories) |
| Search | `search_work_packages(full_text=True)` searches subject, description and comments |
| Templates | New tools `list_template_projects`, `copy_project` (waits for OpenProject's copy job, choose what to copy) |
| Versions | New tools `update_version`, `delete_version` |
| Notifications | New tools `list_notifications`, `mark_notifications_read` (for the API token's user) |
| Bulk | New tool `bulk_update_work_packages` (same fields as update, per-item result) |

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
