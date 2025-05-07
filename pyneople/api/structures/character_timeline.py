from typing import TypedDict
from pyneople.api.structures.character_info import CharacterInfoStructure

class TimelineDateRange(TypedDict):
    start: str
    end: str

class TimelineStructure(TypedDict):
    date: TimelineDateRange
    next: str | None
    rows: list[dict]

class CharacterTimelineStructure(CharacterInfoStructure):
    timeline: TimelineStructure