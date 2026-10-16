"""Attachment tools (Northcore fork)."""

import base64
import mimetypes
from typing import Optional

from src.server import mcp, get_client
from src.utils.formatting import format_error, format_success

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
TEXT_TYPES = ("text/", "application/json", "application/xml", "application/javascript",
              "application/x-yaml", "application/csv")


def _size(n: Optional[int]) -> str:
    if n is None:
        return "?"
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return f"{n:.0f} {unit}" if unit == "B" else f"{n:.1f} {unit}"
        n /= 1024
    return str(n)


@mcp.tool
async def list_attachments(work_package_id: int) -> str:
    """List files attached to a work package (id, name, size, author, date)."""
    try:
        client = get_client()
        result = await client.get_work_package_attachments(work_package_id)
        items = result.get("_embedded", {}).get("elements", [])
        if not items:
            return f"No attachments on work package #{work_package_id}."
        text = f"✅ **{len(items)} attachment(s) on #{work_package_id}**\n\n"
        for a in items:
            author = a.get("_links", {}).get("author", {}).get("title", "Unknown")
            desc = (a.get("description") or {}).get("raw") if isinstance(a.get("description"), dict) else None
            text += (
                f"- **{a.get('fileName')}** (ID: {a.get('id')}, {_size(a.get('fileSize'))}, "
                f"{a.get('contentType', '?')})\n  By {author}, {a.get('createdAt', '')[:10]}\n"
            )
            if desc:
                text += f"  {desc}\n"
        return text
    except Exception as e:
        return format_error(f"Failed to list attachments: {str(e)}")


@mcp.tool
async def upload_attachment(
    work_package_id: int,
    file_name: str,
    content: str,
    encoding: str = "text",
    description: Optional[str] = None,
    content_type: Optional[str] = None,
) -> str:
    """Attach a file to a work package.

    Args:
        work_package_id: Target work package
        file_name: File name incl. extension (e.g. "signal-list.csv")
        content: File content – plain text, or base64 when encoding="base64"
        encoding: "text" (UTF-8) or "base64" for binary files
        description: Optional attachment description
        content_type: Optional MIME type (guessed from file name if omitted)
    """
    try:
        if encoding == "base64":
            data = base64.b64decode(content, validate=True)
        elif encoding == "text":
            data = content.encode("utf-8")
        else:
            return format_error("encoding must be 'text' or 'base64'")
        if len(data) > MAX_UPLOAD_BYTES:
            return format_error(f"File too large ({_size(len(data))}); max {_size(MAX_UPLOAD_BYTES)}")

        ctype = content_type or mimetypes.guess_type(file_name)[0] or "application/octet-stream"
        client = get_client()
        result = await client.upload_work_package_attachment(
            work_package_id, file_name, data, ctype, description
        )
        return format_success(
            f"Attached **{result.get('fileName', file_name)}** to #{work_package_id} "
            f"(ID: {result.get('id')}, {_size(result.get('fileSize', len(data)))})"
        )
    except Exception as e:
        return format_error(f"Failed to upload attachment: {str(e)}")


@mcp.tool
async def download_attachment(attachment_id: int, max_bytes: int = 200_000) -> str:
    """Read an attachment's content.

    Text files are returned as text; binary files as base64. Files larger than
    max_bytes are not returned (raise max_bytes if needed, up to 5 MB).
    """
    try:
        max_bytes = min(max(max_bytes, 1), 5 * 1024 * 1024)
        client = get_client()
        meta, ctype, body = await client.download_attachment(attachment_id)
        name = meta.get("fileName", f"attachment-{attachment_id}")
        if len(body) > max_bytes:
            return format_error(
                f"{name} is {_size(len(body))}, above max_bytes ({_size(max_bytes)})."
            )
        header = f"**{name}** ({_size(len(body))}, {ctype or 'unknown type'})\n\n"
        if ctype.startswith(TEXT_TYPES) or name.lower().endswith(
            (".txt", ".csv", ".md", ".json", ".xml", ".yaml", ".yml", ".log", ".ini", ".cfg", ".scd", ".icd", ".cid")
        ):
            try:
                return header + body.decode("utf-8-sig")
            except UnicodeDecodeError:
                return header + body.decode("latin-1")
        return header + "base64:\n" + base64.b64encode(body).decode()
    except Exception as e:
        return format_error(f"Failed to download attachment: {str(e)}")


@mcp.tool
async def delete_attachment(attachment_id: int) -> str:
    """Permanently delete an attachment."""
    try:
        client = get_client()
        await client.delete_attachment(attachment_id)
        return format_success(f"Attachment {attachment_id} deleted")
    except Exception as e:
        return format_error(f"Failed to delete attachment: {str(e)}")
