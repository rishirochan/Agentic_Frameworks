"""Google Calendar tools for LangChain/LangGraph integration."""

import json
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from calendar_auth import get_calendar_service


# Default timezone - adjust as needed
DEFAULT_TIMEZONE = 'America/Los_Angeles'


def _parse_datetime(date_str: str) -> datetime:
    """Parse date/time strings into datetime objects."""
    tz = ZoneInfo(DEFAULT_TIMEZONE)
    now = datetime.now(tz)
    date_str = date_str.lower().strip()
    
    if date_str == 'today':
        return now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif date_str == 'tomorrow':
        return (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        for fmt in ["%Y-%m-%d %H:%M", "%Y-%m-%d", "%m/%d/%Y %H:%M", "%m/%d/%Y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.replace(tzinfo=tz)
            except ValueError:
                continue
        raise ValueError(f"Could not parse date: {date_str}")


def _format_event(event: dict) -> dict:
    """Format a Google Calendar event into a readable dict."""
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    return {
        'id': event.get('id'),
        'summary': event.get('summary', 'No title'),
        'start': start,
        'end': end,
        'description': event.get('description', ''),
        'location': event.get('location', ''),
    }

class SearchEventsInput(BaseModel):
    query: str = Field(description="Date to search: 'today', 'tomorrow', 'YYYY-MM-DD', or range 'YYYY-MM-DD to YYYY-MM-DD'")

class CreateEventInput(BaseModel):
    summary: str = Field(description="Event title/name")
    start_time: str = Field(description="Start time in format 'YYYY-MM-DD HH:MM' (e.g., '2026-01-08 14:00')")
    duration_minutes: int = Field(default=60, description="Duration in minutes (default 60)")
    description: Optional[str] = Field(default=None, description="Event description (optional)")
    location: Optional[str] = Field(default=None, description="Event location (optional)")

class UpdateEventInput(BaseModel):
    event_id: str = Field(description="Event ID from search_calendar_events")
    summary: Optional[str] = Field(default=None, description="New title (optional)")
    start_time: Optional[str] = Field(default=None, description="New start time 'YYYY-MM-DD HH:MM' (optional)")
    end_time: Optional[str] = Field(default=None, description="New end time 'YYYY-MM-DD HH:MM' (optional)")
    description: Optional[str] = Field(default=None, description="New description (optional)")
    location: Optional[str] = Field(default=None, description="New location (optional)")


class DeleteEventInput(BaseModel):
    event_id: str = Field(description="Event ID to delete (get from search_calendar_events)")


def _search_calendar_events(query: str) -> str:
    """Search for events by date or range."""
    try:
        service = get_calendar_service()
        query = query.strip().lower()
        
        if ' to ' in query:
            start_str, end_str = query.split(' to ')
            time_min = _parse_datetime(start_str)
            time_max = _parse_datetime(end_str) + timedelta(days=1)
        else:
            time_min = _parse_datetime(query)
            time_max = time_min + timedelta(days=1)
        
        events_result = service.events().list(
            calendarId='primary',
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        formatted = [_format_event(e) for e in events]
        
        if not formatted:
            return json.dumps({"message": "No events found for this time period.", "events": []})
        return json.dumps({"events": formatted})
    except Exception as e:
        return json.dumps({"error": str(e)})


def _create_calendar_event(
    summary: str, 
    start_time: str, 
    duration_minutes: int = 60,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> str:
    """Create a new calendar event with conflict checking."""
    try:
        service = get_calendar_service()
        tz = ZoneInfo(DEFAULT_TIMEZONE)
        
        start_dt = _parse_datetime(start_time)
        end_dt = start_dt + timedelta(minutes=duration_minutes)
        
        # CONFLICT CHECK
        existing = service.events().list(
            calendarId='primary',
            timeMin=start_dt.isoformat(),
            timeMax=end_dt.isoformat(),
            singleEvents=True
        ).execute().get('items', [])
        
        if existing:
            conflicts = [_format_event(e) for e in existing]
            return json.dumps({
                "warning": "Time slot has existing events!",
                "conflicts": conflicts,
                "action": "Event NOT created. Ask user to confirm or pick different time."
            })
        
        event = {
            'summary': summary,
            'start': {'dateTime': start_dt.isoformat(), 'timeZone': DEFAULT_TIMEZONE},
            'end': {'dateTime': end_dt.isoformat(), 'timeZone': DEFAULT_TIMEZONE},
        }
        if description:
            event['description'] = description
        if location:
            event['location'] = location
        
        created = service.events().insert(calendarId='primary', body=event).execute()
        return json.dumps({
            "success": True,
            "message": f"Event '{summary}' created successfully!",
            "event": _format_event(created)
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def _update_calendar_event(
    event_id: str,
    summary: Optional[str] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    description: Optional[str] = None,
    location: Optional[str] = None
) -> str:
    """Update an existing calendar event."""
    try:
        service = get_calendar_service()
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        if summary:
            event['summary'] = summary
        if description:
            event['description'] = description
        if location:
            event['location'] = location
        if start_time:
            start_dt = _parse_datetime(start_time)
            event['start'] = {'dateTime': start_dt.isoformat(), 'timeZone': DEFAULT_TIMEZONE}
        if end_time:
            end_dt = _parse_datetime(end_time)
            event['end'] = {'dateTime': end_dt.isoformat(), 'timeZone': DEFAULT_TIMEZONE}
        
        updated = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return json.dumps({
            "success": True,
            "message": "Event updated successfully!",
            "event": _format_event(updated)
        })
    except Exception as e:
        return json.dumps({"error": str(e)})


def _delete_calendar_event(event_id: str) -> str:
    """Delete a calendar event by ID."""
    try:
        service = get_calendar_service()
        service.events().delete(calendarId='primary', eventId=event_id.strip()).execute()
        return json.dumps({"success": True, "message": f"Event {event_id} deleted successfully!"})
    except Exception as e:
        return json.dumps({"error": str(e)})
        

def get_calendar_tools() -> list:
    """Returns list of calendar tools for LangChain integration."""
    return [
        StructuredTool.from_function(
            func=_search_calendar_events,
            name="search_calendar_events",
            description="Search for calendar events by date. Use 'today', 'tomorrow', 'YYYY-MM-DD', or 'YYYY-MM-DD to YYYY-MM-DD' for ranges.",
            args_schema=SearchEventsInput
        ),
        StructuredTool.from_function(
            func=_create_calendar_event,
            name="create_calendar_event",
            description="Create a new calendar event. Automatically checks for conflicts. Convert natural language dates to 'YYYY-MM-DD HH:MM' format first.",
            args_schema=CreateEventInput
        ),
        StructuredTool.from_function(
            func=_update_calendar_event,
            name="update_calendar_event",
            description="Update an existing calendar event. Get event_id from search_calendar_events first.",
            args_schema=UpdateEventInput
        ),
        StructuredTool.from_function(
            func=_delete_calendar_event,
            name="delete_calendar_event",
            description="Delete a calendar event by ID. Get event_id from search_calendar_events first.",
            args_schema=DeleteEventInput
        ),
    ]
