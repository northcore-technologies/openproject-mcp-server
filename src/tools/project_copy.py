"""Project template and copy tools (Northcore fork)."""

import json
from typing import Optional

from src.server import mcp, get_client
from src.utils.formatting import format_error, format_success


@mcp.tool
async def list_template_projects() -> str:
    """List projects marked as templates in OpenProject (usable with copy_project)."""
    try:
        filters = json.dumps([{"templated": {"operator": "=", "values": ["t"]}}])
        result = await get_client().get_projects(filters)
        projects = result.get("_embedded", {}).get("elements", [])
        if not projects:
            return (
                "No template projects. Mark one under Project settings → Information → "
                "'Set as template', or copy any project by ID."
            )
        lines = [f"- **{p.get('name')}** (ID: {p.get('id')}, `{p.get('identifier')}`)" for p in projects]
        return f"✅ **{len(projects)} template project(s)**\n\n" + "\n".join(lines)
    except Exception as e:
        return format_error(f"Failed to list template projects: {str(e)}")


@mcp.tool
async def copy_project(
    source_project_id: int,
    name: str,
    identifier: Optional[str] = None,
    parent_id: Optional[int] = None,
    copy_work_packages: bool = True,
    copy_members: bool = True,
    copy_versions: bool = True,
    copy_categories: bool = True,
    copy_wiki: bool = True,
    copy_attachments: bool = True,
    send_notifications: bool = False,
) -> str:
    """Create a new project by copying an existing (template) project.

    Args:
        source_project_id: Project to copy (see list_template_projects)
        name: Name of the new project
        identifier: Optional URL identifier (lowercase, dashes); generated if omitted
        parent_id: Optional parent project ID
        copy_*: What to copy from the source
        send_notifications: Notify members about copied work packages (default False)
    """
    try:
        options = {
            "copyWorkPackages": copy_work_packages,
            "copyMembers": copy_members,
            "copyVersions": copy_versions,
            "copyCategories": copy_categories,
            "copyWiki": copy_wiki,
            "copyWikiPageAttachments": copy_wiki and copy_attachments,
            "copyWorkPackageAttachments": copy_work_packages and copy_attachments,
            "copyQueries": True,
            "copyBoards": True,
            "copyOverview": True,
        }
        job = await get_client().copy_project(
            source_project_id, name, identifier, parent_id, options, send_notifications
        )
        status = job.get("status")
        if job.get("_type") == "Project":
            return format_success(f"Project **{job.get('name')}** (ID: {job.get('id')}) created from #{source_project_id}")
        if status == "success":
            payload = job.get("payload") or {}
            target = payload.get("redirect") or payload.get("_links", {}).get("project", {}).get("href", "")
            return format_success(f"Project **{name}** created from #{source_project_id}. {target}".strip())
        if status in ("in_queue", "in_process"):
            return format_success(
                f"Copy of #{source_project_id} → **{name}** is still running ({status}). "
                "Check list_projects in a minute."
            )
        return format_error(f"Copy failed ({status}): {job.get('message') or job}")
    except Exception as e:
        return format_error(f"Failed to copy project: {str(e)}")
