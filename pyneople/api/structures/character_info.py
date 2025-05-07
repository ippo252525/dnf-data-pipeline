from typing import TypedDict, NotRequired

class CharacterInfoStructure(TypedDict):
    serverId: str
    characterId: str
    characterName: str
    level: int
    jobId: str
    jobGrowId: str
    jobName: str
    jobGrowName: str
    fame: int | None
    adventureName: NotRequired[str]
    guildId: NotRequired[str]
    guildName: NotRequired[str]