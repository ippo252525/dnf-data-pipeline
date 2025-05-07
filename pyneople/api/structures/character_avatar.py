from typing import TypedDict, NotRequired, List
from pyneople.api.structures.character_info import CharacterInfoStructure

class CloneDict(TypedDict, total=False):
    itemId: str
    itemName: str


class EmblemDict(TypedDict):
    slotNo: int
    slotColor: str
    itemId: str
    itemName: str
    itemRarity: str


class AvatarItemDict(TypedDict):
    slotId: str
    slotName: str
    itemId: str
    itemName: str
    itemRarity: str
    clone: NotRequired[CloneDict]
    optionAbility: NotRequired[str]
    emblems: NotRequired[List[EmblemDict]]


class CharacterAvatarStructure(CharacterInfoStructure):
    avatar: List[AvatarItemDict]