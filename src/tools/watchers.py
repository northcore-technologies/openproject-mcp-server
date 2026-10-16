"""Watcher and category tools (Northcore fork)."""

from src.server import mcp, get_client
from src.utils.formatting import format_error, format_success


@mcp.tool
async def list_watchers(work_package_id: int) -> str:
    """List users watching a work package."""
    try:
        result = await get_client().get_watchers(work_package_id)
        users = result.get("_embedded", {}).get("elements", [])
        if not users:
            return f"No watchers on #{work_package_id}."
        lines = [f"- **{u.get('name')}** (ID: {u.get('id')})" for u in users]
        return f"✅ **{len(users)} watcher(s) on #{work_package_id}**\n\n" + "\n".join(lines)
    except Exception as e:
        return format_error(f"Failed to list watchers: {str(e)}")


@mcp.tool
async def add_watcher(work_package_id: int, user_id: int) -> str:
    """Add a user as watcher of a work package (they get notified of changes)."""
    try:
        await get_client().add_watcher(work_package_id, user_id)
        return format_success(f"User {user_id} now watches #{work_package_id}")
    except Exception as e:
        return format_error(f"Failed to add watcher: {str(e)}")


@mcp.tool
async def remove_watcher(work_package_id: int, user_id: int) -> str:
    """Remove a watcher from a work package."""
    try:
        await get_client().remove_watcher(work_package_id, user_id)
        return format_success(f"User {user_id} no longer watches #{work_package_id}")
    except Exception as e:
        return format_error(f"Failed to remove watcher: {str(e)}")


@mcp.tool
async def list_categories(project_id: int) -> str:
    """List work package categories of a project (use the ID as category_id)."""
    try:
        result = await get_client().get_categories(project_id)
        cats = result.get("_embedded", {}).get("elements", [])
        if not cats:
            return f"No categories in project #{project_id}."
        lines = []
        for c in cats:
            default = c.get("_links", {}).get("defaultAssignee", {}).get("title")
            lines.append(
                f"- **{c.get('name')}** (ID: {c.get('id')})"
                + (f" – default assignee: {default}" if default else "")
            )
        return f"✅ **{len(cats)} categor{'y' if len(cats) == 1 else 'ies'} in project #{project_id}**\n\n" + "\n".join(lines)
    except Exception as e:
        return format_error(f"Failed to list categories: {str(e)}")
