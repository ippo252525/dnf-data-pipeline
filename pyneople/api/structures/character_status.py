from typing import TypedDict, NotRequired
from pyneople.api.structures.character_info import CharacterInfoStructure

class BuffStatus(TypedDict):
    name: str
    value: int | float


class Buff(TypedDict):
    name: str
    level: NotRequired[int]  
    status: list[BuffStatus]


class Stat(TypedDict):
    name: str
    value: int | float


class CharacterDetailInfo(CharacterInfoStructure):  
    buff: list[Buff]
    status: list[Stat]