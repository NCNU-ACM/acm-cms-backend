from fastapi import APIRouter, HTTPException, Depends
from models import EventCreate, EventResponse
from utils import file_io
from utils.git_backup import commit_change
from utils.build_trigger import trigger_rebuild
from auth import verify_token

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
def get_events(semester: str = None):
    """列出活動，可指定學期，不指定則列出所有學期"""
    if semester:
        entries = file_io.list_entries("events", semester)
    else:
        entries = []
        for sem in file_io.list_semesters("events"):
            entries.extend(file_io.list_entries("events", sem))
    entries.sort(key=lambda x: x.get("date", ""), reverse=True)
    return entries


@router.post("", response_model=EventResponse, dependencies=[Depends(verify_token)])
def create_event(event: EventCreate):
    entry_id = file_io.generate_timestamp_id()
    data = event.model_dump(exclude={"semester"})

    file_io.write_entry("events", entry_id, data, semester=event.semester)
    commit_change(f"新增活動: {event.title}")
    trigger_rebuild()

    data["id"] = entry_id
    data["semester"] = event.semester
    return data


@router.put("/{semester}/{entry_id}", response_model=EventResponse, dependencies=[Depends(verify_token)])
def update_event(semester: str, entry_id: str, event: EventCreate):
    existing = file_io.read_entry("events", entry_id, semester)
    if not existing:
        raise HTTPException(status_code=404, detail="找不到這個活動")

    data = event.model_dump(exclude={"semester"})

    file_io.write_entry("events", entry_id, data, semester=semester)
    commit_change(f"更新活動: {event.title}")
    trigger_rebuild()

    data["id"] = entry_id
    data["semester"] = semester
    return data


@router.delete("/{semester}/{entry_id}", dependencies=[Depends(verify_token)])
def delete_event(semester: str, entry_id: str):
    success = file_io.delete_entry("events", entry_id, semester)
    if not success:
        raise HTTPException(status_code=404, detail="找不到這個活動")

    commit_change(f"刪除活動: {entry_id}")
    trigger_rebuild()

    return {"message": "刪除成功"}