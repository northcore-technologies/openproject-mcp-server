"""In-app notification tools (Northcore fork). Acts as the API token's user."""

from typing import Optional

from src.server import mcp, get_client
from src.utils.formatting import format_error, format_success


@mcp.tool
async def list_notifications(unread_only: bool = True, page_size: int = 25) -> str:
    """List OpenProject in-app notifications for the API user (mentions, assignments, watched changes)."""
    try:
        page_size = min(max(page_size, 1), 100)
        result = await get_client().get_notifications(unread_only, page_size)
        items = result.get("_embedded", {}).get("elements", [])
        total = result.get("total", len(items))
        if not items:
            return "No unread notifications." if unread_only else "No notifications."
        text = f"✅ **{total} {'unread ' if unread_only else ''}notification(s)** (showing {len(items)})\n\n"
        for n in items:
            links = n.get("_links", {})
            resource = links.get("resource", {})
            wp_id = (resource.get("href") or "").rstrip("/").split("/")[-1]
            text += (
                f"- [{n.get('id')}] **{n.get('reason', '?')}** on #{wp_id} {resource.get('title', '')}\n"
                f"  {links.get('project', {}).get('title', '')} · by {links.get('actor', {}).get('title', 'system')}"
                f" · {str(n.get('createdAt', ''))[:16].replace('T', ' ')}"
                f"{'' if n.get('readIAN') is False else ' · read'}\n"
            )
        return text
    except Exception as e:
        return format_error(f"Failed to list notifications: {str(e)}")


@mcp.tool
async def mark_notifications_read(notification_id: Optional[int] = None, all_notifications: bool = False) -> str:
    """Mark one notification (notification_id) or all notifications (all_notifications=True) as read."""
    try:
        client = get_client()
        if all_notifications:
            await client.mark_all_notifications_read()
            return format_success("All notifications marked as read")
        if notification_id:
            await client.mark_notification_read(notification_id)
            return format_success(f"Notification {notification_id} marked as read")
        return format_error("Give notification_id or all_notifications=True")
    except Exception as e:
        return format_error(f"Failed to mark notifications read: {str(e)}")
