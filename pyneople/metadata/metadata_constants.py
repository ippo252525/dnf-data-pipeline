# 서버 ID 가 key NAME 이 value
SERVER_ID_TO_NAME = {
    'anton': '안톤',
    'bakal': '바칼',
    'cain': '카인',
    'casillas': '카시야스',
    'diregie': '디레지에',
    'hilder': '힐더',
    'prey': '프레이',
    'siroco': '시로코'
    }

SERVER_NAME_TO_ID = {v : k for k, v in SERVER_ID_TO_NAME.items()}

SERVER_ID_LIST = list(SERVER_ID_TO_NAME.keys())

EQUIPMENT_SLOT_ID_LIST = [
    'WEAPON',
    'TITLE',
    'JACKET',
    'SHOULDER',
    'PANTS',
    'SHOES',
    'WAIST',
    'AMULET',
    'WRIST',
    'RING',
    'SUPPORT',
    'MAGIC_STON',
    'EARRING'
 ]

AVATAR_SLOT_ID_LIST = [
    'HEADGEAR',
    'HAIR',
    'FACE',
    'JACKET',
    'PANTS',
    'SHOES',
    'BREAST',
    'WAIST',
    'SKIN',
    'AURORA',
    'WEAPON',
    'AURA_SKIN'
]

STATUS_NAME_LIST = [
    'HP',
    'MP',
    '물리 방어율',
    '마법 방어율',
    '힘',
    '지능',
    '체력',
    '정신력',
    '물리 공격',
    '마법 공격',
    '물리 크리티컬',
    '마법 크리티컬',
    '독립 공격',
    '공격 속도',
    '캐스팅 속도',
    '이동 속도',
    '모험가 명성',
    '적중률',
    '회피율',
    'HP 회복량',
    'MP 회복량',
    '경직도',
    '히트리커버리',
    '화속성 강화',
    '화속성 저항',
    '수속성 강화',
    '수속성 저항',
    '명속성 강화',
    '명속성 저항',
    '암속성 강화',
    '암속성 저항',
    '물리 방어',
    '마법 방어',
    '공격력 증가',
    '버프력',
    '공격력 증폭',
    '버프력 증폭',
    '최종 데미지 증가',
    '쿨타임 감소',
    '쿨타임 회복속도',
    '최종 쿨타임 감소율',
    '데미지 증가',
    '크리티컬 데미지 증가',
    '추가 데미지 증가',
    '모든 공격력 증가',
    '물리 공격력 증가',
    '마법 공격력 증가',
    '독립 공격력 증가',
    '힘 증가',
    '지능 증가',
    '지속피해',
    '물리 피해 감소',
    '마법 피해 감소',
    '출혈 피해 전환',
    '중독 피해 전환',
    '화상 피해 전환',
    '감전 피해 전환',
    '출혈 내성',
    '중독 내성',
    '화상 내성',
    '감전 내성',
    '빙결 내성',
    '둔화 내성',
    '기절 내성',
    '저주 내성',
    '암흑 내성',
    '석화 내성',
    '수면 내성',
    '혼란 내성',
    '구속 내성',
    '화속성 피해',
    '수속성 피해',
    '명속성 피해',
    '암속성 피해',
    '출혈 피해',
    '중독 피해',
    '화상 피해',
    '감전 피해'
]

BUFF_NAME_LIST = [
    '모험단 버프',
    '무제한 길드능력치',
    '기간제 길드능력치'    
]

BUFF_STATUS_NAME_LIST = [
    '힘',
    '지능',
    '체력',
    '정신력'
]

CHARACTER_STATUS_TRANSLATION_MAP = {
    '모험단 버프' : 'adventure',
    '무제한 길드능력치' : 'permanent_guild_stats',
    '기간제 길드능력치' : 'temporary_guild_stats',
    'HP': 'hp',
    'MP': 'mp',
    '물리 방어율': 'physical_defense_rate',
    '마법 방어율': 'magical_defense_rate',
    '힘': 'strength',
    '지능': 'intelligence',
    '체력': 'vitality',
    '정신력': 'spirit',
    '물리 공격': 'physical_attack',
    '마법 공격': 'magical_attack',
    '물리 크리티컬': 'physical_critical_chance',
    '마법 크리티컬': 'magical_critical_chance',
    '독립 공격': 'independent_attack',
    '공격 속도': 'attack_speed',
    '캐스팅 속도': 'casting_speed',
    '이동 속도': 'movement_speed',
    '모험가 명성': 'fame',
    '적중률': 'hit_rate',
    '회피율': 'evasion_rate',
    'HP 회복량': 'hp_recovery',
    'MP 회복량': 'mp_recovery',
    '경직도': 'stiffness',
    '히트리커버리': 'hit_recovery',
    '화속성 강화': 'fire_element_enhancement',
    '화속성 저항': 'fire_element_resistance',
    '수속성 강화': 'water_element_enhancement',
    '수속성 저항': 'water_element_resistance',
    '명속성 강화': 'light_element_enhancement',
    '명속성 저항': 'light_element_resistance',
    '암속성 강화': 'dark_element_enhancement',
    '암속성 저항': 'dark_element_resistance',
    '물리 방어': 'physical_defense',
    '마법 방어': 'magical_defense',
    '공격력 증가': 'attack_power_increase',
    '버프력': 'buff_power',
    '공격력 증폭': 'attack_power_amplification',
    '버프력 증폭': 'buff_power_amplification',
    '최종 데미지 증가': 'final_damage_increase',
    '쿨타임 감소': 'cooldown_reduction',
    '쿨타임 회복속도': 'cooldown_recovery_rate',
    '최종 쿨타임 감소율': 'final_cooldown_reduction_rate',
    '데미지 증가': 'damage_increase',
    '크리티컬 데미지 증가': 'critical_damage_increase',
    '추가 데미지 증가': 'additional_damage_increase',
    '모든 공격력 증가': 'all_attack_power_increase',
    '물리 공격력 증가': 'physical_attack_power_increase',
    '마법 공격력 증가': 'magical_attack_power_increase',
    '독립 공격력 증가': 'independent_attack_power_increase',
    '힘 증가': 'strength_increase',
    '지능 증가': 'intelligence_increase',
    '지속피해': 'damage_over_time',
    '물리 피해 감소': 'physical_damage_reduction',
    '마법 피해 감소': 'magical_damage_reduction',
    '출혈 피해 전환': 'bleed_damage_conversion',
    '중독 피해 전환': 'poison_damage_conversion',
    '화상 피해 전환': 'burn_damage_conversion',
    '감전 피해 전환': 'electrocution_damage_conversion',
    '출혈 내성': 'bleed_resistance',
    '중독 내성': 'poison_resistance',
    '화상 내성': 'burn_resistance',
    '감전 내성': 'electrocution_resistance',
    '빙결 내성': 'freeze_resistance',
    '둔화 내성': 'slow_resistance',
    '기절 내성': 'stun_resistance',
    '저주 내성': 'curse_resistance',
    '암흑 내성': 'darkness_resistance',
    '석화 내성': 'petrification_resistance',
    '수면 내성': 'sleep_resistance',
    '혼란 내성': 'confusion_resistance',
    '구속 내성': 'restraint_resistance',
    '화속성 피해': 'fire_element_damage',
    '수속성 피해': 'water_element_damage',
    '명속성 피해': 'light_element_damage',
    '암속성 피해': 'dark_element_damage',
    '출혈 피해': 'bleed_damage',
    '중독 피해': 'poison_damage',
    '화상 피해': 'burn_damage',
    '감전 피해': 'electrocution_damage'
}

# 노전직 캐릭터가 있을 수 있는 직업의 ID
NO_JOG_GROW_JOB_IDS = [
    '41f1cdc2ff58bb5fdc287be0db2a8df3',
    'a7a059ebe9e6054c0644b40ef316d6e9',
    'afdf3b989339de478e85b614d274d1ef',
    '3909d0b188e9c95311399f776e331da5',
    'f6a4ad30555b99b499c07835f87ce522',
    '944b9aab492c15a8474f96947ceeb9e4',
    'ddc49e9ad1ff72a00b53c6cff5b1e920',
    'ca0f0e0e9e1d55b5f9955b03d9dd213c',
    'a5ccbaf5538981c6ef99b236c0a60b73',
    '1645c45aabb008c98406b3a16447040d',
    '0ee8fa5dc525c1a1f23fc6911e921e4a',
    '3deb7be5f01953ac8b1ecaa1e25e0420',
    '0c1b401bb09241570d364420b3ba3fd7',
    '986c2b3d72ee0e4a0b7fcfbe786d4e02'
    ]

# 남여 직업군의 버프 스킬 이름이 같은 버프 스킬
SAME_BUFF_SKILL_NAMES = [
    '데스바이리볼버',
    '로보틱스',
    '오버차지',
    '강권',
    '반드시잡는다!'
    '미라클비전'
]

# 유일 장비를 착용 할 수 있는 부위
HAS_EXALTED_INFO_SLOT_IDS = ['EARRING', 'MAGIC_STON']

# 퇴마사의 모든 전직 이름
EXORCIST_JOB_GROW_NAMES = ['퇴마사', '용투사', '태을선인', '眞 퇴마사']

# 타임라인 데이터 코드마다 올 수 있는 dict의 key
TIMELINE_CODE_TO_KEYS_MAP = {
    102: {'afterName', 'beforeName'},
    103: {'jobGrowId', 'jobGrowName', 'jobId', 'jobName'},
    104: {'level'},
    105: {'afterName', 'beforeName'},
    201: {'guide', 'hard', 'matching', 'modeName', 'phaseName', 'raidName', 'raidPartyName', 'single', 'squad'},
    206: {'mode', 'point'},
    207: {'guide', 'raidPartyName'},
    209: {'regionName'},
    210: {'hard', 'modeName', 'raidName', 'raidPartyName'},
    401: {'after', 'before', 'itemId', 'itemName', 'itemRarity', 'result', 'safe', 'ticket'},
    402: {'after', 'before', 'itemId', 'itemName', 'itemRarity', 'result', 'safe', 'ticket'},
    403: {'after', 'itemId', 'itemName', 'itemRarity', 'result'},
    404: {'after', 'before', 'itemId', 'itemName', 'itemRarity', 'result', 'safe'},
    405: {'amplification', 'itemId', 'itemName', 'itemRarity', 'refine', 'reinforce'},
    406: {'amplification', 'itemId', 'itemName', 'itemRarity', 'refine', 'reinforce'},
    407: {'itemId', 'itemName', 'itemRarity'},
    501: {'booster', 'itemId', 'itemName'},
    502: {'itemId', 'itemName', 'itemRarity'},
    504: {'channelName', 'channelNo', 'itemId', 'itemName', 'itemRarity', 'mistGear', 'reinforce'},
    505: {'channelName', 'channelNo', 'dungeonName', 'itemId', 'itemName', 'itemRarity', 'mistGear'},
    506: {'itemId', 'itemName', 'itemRarity'},
    507: {'itemId', 'itemName', 'itemRarity'},
    508: {'itemId', 'itemName', 'itemRarity', 'npcName'},
    510: {'itemId', 'itemName', 'itemRarity', 'mistGear', 'refinedMistGear'},
    511: {'itemId', 'itemName', 'itemRarity', 'pureMistGear'},
    512: {'itemId', 'itemName', 'itemRarity', 'upgradeName'},
    513: {'dungeonName', 'itemId', 'itemName', 'itemRarity', 'mistGear'},
    514: {'itemId', 'itemName', 'itemRarity'},
    516: {'adventureSafeMoveType', 'itemId', 'itemName', 'itemRarity', 'mistGear'},
    517: {'itemId', 'itemName', 'itemRarity', 'resultItems'},
    518: {'itemId', 'itemName', 'itemObtainInfo', 'itemRarity'},
    519: {'itemId', 'itemName', 'itemRarity', 'mistGear'},
    520: {'itemId', 'itemName', 'itemRarity'},
    601: {'itemId', 'itemName', 'itemObtainInfo', 'itemRarity'},
    602: {'itemId', 'itemName', 'itemObtainInfo', 'itemRarity'}
}
