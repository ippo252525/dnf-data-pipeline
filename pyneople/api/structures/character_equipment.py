from typing import TypedDict, NotRequired
from pyneople.api.structures.character_info import CharacterInfoStructure

class Status(TypedDict):
    name: str
    value: int | str

class Tune(TypedDict):
    level: int
    setPoint: NotRequired[int]
    upgrade: NotRequired[bool]
    status: NotRequired[list[Status]]

class UpgradeInfo(TypedDict):
    itemId: str
    itemName: str
    itemRarity: str
    setItemId: NotRequired[str]
    setItemName: NotRequired[str]
    setPoint: NotRequired[int]

class Skin(TypedDict):
    itemId: str
    itemName: str
    itemRarity: str

class ExaltedInfo(TypedDict):
    damage: str
    buff: int
    explain: str


class Potency(TypedDict):
    value: int
    damage: str
    buff: int

class Equipment(TypedDict):
    slotId: str
    slotName: str
    itemId: str
    itemName: str
    itemTypeId: str
    itemType: str
    itemTypeDetailId: str
    itemTypeDetail: str
    itemAvailableLevel: int
    itemRarity: str
    setItemId: str | None
    setItemName: str | None
    skin: NotRequired[Skin]
    reinforce: int
    itemGradeName: NotRequired[str]
    enchant: NotRequired[dict]
    amplificationName: str | None
    refine: int
    fusionOption: NotRequired[dict]
    upgradeInfo: NotRequired[UpgradeInfo]
    tune: NotRequired[list[Tune]]
    exaltedInfo: NotRequired[ExaltedInfo]
    potency: NotRequired[Potency]

class SetItemStatus(TypedDict):
    name: str
    value: int | str

class SetPoint(TypedDict):
    current: int
    min: int
    max: int

class SetItemActive(TypedDict):
    explain: str
    explainDetail: str
    status: list[SetItemStatus]
    setPoint: SetPoint

class SlotInfo(TypedDict):
    itemNo: str
    slotId: str
    slotName: str
    itemRarity: str
    fusionStone: NotRequired[bool]

class SetItemInfo(TypedDict):
    setItemId: str
    setItemName: str
    setItemRarityName: str
    active: SetItemActive
    slotInfo: list[SlotInfo]


class CharacterEquipmentStructure(CharacterInfoStructure):
    equipment: list[Equipment]  #TODO 알몸인 캐릭터가 빈 리스트인지 null인지 확인해야함
    setItemInfo: list[SetItemInfo] | None