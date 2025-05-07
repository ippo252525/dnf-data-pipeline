from typing import TypedDict
from pyneople.api.structures.character_info import CharacterInfoStructure  

class FameRange(TypedDict):
    min: int
    max: int

class CharacterFameStructure(TypedDict):
    fame: FameRange
    rows: list[CharacterInfoStructure]