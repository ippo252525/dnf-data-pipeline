from typing import TypedDict, NotRequired
from pyneople.api.structures.character_info import CharacterInfoStructure


class Clone(TypedDict, total=False):
    itemId: str
    itemName: str


class Artifact(TypedDict):
    slotColor: str
    itemId: str
    itemName: str
    itemAvailableLevel: int
    itemRarity: str


class Creature(TypedDict):
    itemId: str
    itemName: str
    itemRarity: str
    clone: NotRequired[Clone]
    artifact: NotRequired[list[Artifact]]


class CharacterCreatureStructure(CharacterInfoStructure):
    creature: Creature