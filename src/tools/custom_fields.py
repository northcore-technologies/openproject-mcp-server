"""Custom field tools (Northcore fork)."""

from typing import Optional

from src.server import mcp, get_client
from src.utils.formatting import format_error


def _current_value(wp: dict, key: str, ftype: str) -> str:
    """Render a work package's current value for a custom field."""
    links = wp.get("_links", {})
    if key in links:
        link = links[key]
        items = link if isinstance(link, list) else [link]
        titles = [str(i.get("title") or i.get("href")) for i in items if i and i.get("href")]
        return ", ".join(titles) if titles else "—"
    value = wp.get(key)
    if isinstance(value, dict):
        value = value.get("raw")
    return "—" if value in (None, "") else str(value)


@mcp.tool
async def list_custom_fields(
    project_id: Optional[int] = None,
    type_id: Optional[int] = None,
    work_package_id: Optional[int] = None,
) -> str:
    """List custom fields available for work packages, with allowed options.

    Give either work_package_id (also shows current values) or project_id + type_id
    (fields available when creating that type in that project).

    Set values with create_work_package / update_work_package via
    custom_fields={"Field name": value}.
    """
    try:
        client = get_client()
        wp = None
        if work_package_id:
            wp = await client.get_work_package(work_package_id)
            href = wp.get("_links", {}).get("schema", {}).get("href")
            schema = await client.get_work_package_schema(schema_href=href)
        elif project_id and type_id:
            schema = await client.get_work_package_schema(project_id=project_id, type_id=type_id)
        else:
            return format_error("Provide work_package_id, or both project_id and type_id")

        fields = client.schema_custom_fields(schema)
        if not fields:
            return "No custom fields are enabled for this project/type."

        text = f"✅ **{len(fields)} custom field(s)**\n\n"
        for key, field in sorted(fields.items(), key=lambda kv: str(kv[1].get("name"))):
            ftype = str(field.get("type", ""))
            line = f"- **{field.get('name')}** (`{key}`, {ftype}"
            if field.get("required"):
                line += ", required"
            if not field.get("writable", True):
                line += ", read-only"
            line += ")"
            if wp is not None:
                line += f": {_current_value(wp, key, ftype)}"
            text += line + "\n"
            if "CustomOption" in ftype:
                options = client.custom_field_options(field)
                if options:
                    labels = ", ".join(str(o.get("title")) for o in options[:30])
                    more = f" (+{len(options) - 30} more)" if len(options) > 30 else ""
                    text += f"  Options: {labels}{more}\n"
        return text

    except Exception as e:
        return format_error(f"Failed to list custom fields: {str(e)}")
