"""Bulk work package updates (Northcore fork)."""

import asyncio
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from src.server import mcp, get_client
from src.utils.formatting import format_error


class BulkUpdateInput(BaseModel):
    """Same fields as update_work_package, applied to every listed work package."""

    work_package_ids: List[int] = Field(..., description="Work package IDs to update", min_length=1, max_length=200)
    status_id: Optional[int] = Field(None, gt=0)
    priority_id: Optional[int] = Field(None, gt=0)
    type_id: Optional[int] = Field(None, gt=0)
    assignee_id: Optional[int] = Field(None, gt=0)
    responsible_id: Optional[int] = Field(None, gt=0)
    category_id: Optional[int] = Field(None, gt=0)
    version_id: Optional[int] = Field(None, gt=0)
    start_date: Optional[str] = Field(None, description="YYYY-MM-DD")
    due_date: Optional[str] = Field(None, description="YYYY-MM-DD")
    percentage_done: Optional[int] = Field(None, ge=0, le=100)
    estimated_hours: Optional[float] = Field(None, ge=0)
    remaining_hours: Optional[float] = Field(None, ge=0)
    custom_fields: Optional[Dict[str, Any]] = Field(None, description="As in update_work_package")


@mcp.tool
async def bulk_update_work_packages(input: BulkUpdateInput) -> str:
    """Apply the same changes to many work packages at once (e.g. move all to a version,
    set status, reassign). Reports success/failure per work package."""
    fields = input.model_dump(exclude_none=True)
    ids = fields.pop("work_package_ids")
    if not fields:
        return format_error("No fields provided to update")
    if "start_date" in fields:
        fields["startDate"] = fields.pop("start_date")
    if "due_date" in fields:
        fields["dueDate"] = fields.pop("due_date")

    client = get_client()
    sem = asyncio.Semaphore(5)

    async def one(wp_id: int):
        async with sem:
            try:
                await client.update_work_package(wp_id, dict(fields))
                return wp_id, None
            except Exception as e:
                return wp_id, str(e).split("\n")[0][:200]

    results = await asyncio.gather(*(one(i) for i in ids))
    ok = [i for i, err in results if err is None]
    failed = [(i, err) for i, err in results if err is not None]
    text = f"✅ Updated {len(ok)}/{len(ids)} work package(s): {', '.join(f'#{i}' for i in ok) or '—'}\n"
    if failed:
        text += "\n❌ Failed:\n" + "\n".join(f"- #{i}: {err}" for i, err in failed)
    return text
