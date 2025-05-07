from typing import TypedDict, NotRequired, List
from pyneople.api.structures.character_info import CharacterInfoStructure

class ReinforceStatus(TypedDict):
    name: str
    value: float


class Gem(TypedDict):
    slotNo: int
    itemId: str
    itemName: str
    itemRarity: str


class Flag(TypedDict):
    itemId: str
    itemName: str
    itemRarity: str
    reinforce: int
    reinforceStatus: NotRequired[List[ReinforceStatus]]
    gems: NotRequired[List[Gem]]


class CharacterFlagStructure(CharacterInfoStructure):
    flag: Flag