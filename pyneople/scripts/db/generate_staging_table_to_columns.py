# 각 스테이징 테이블에서 사용 할 컬럼들의 정보를 담는 dict 생성 후 저장
# 여기서 선언하지 않은 엔드포인트는 가능 한 모든 값을 사용함함

import os 
import json
import pyneople.api.registry.endpoint_class
from pyneople.api.registry.endpoint_registry import EndpointRegistry
from itertools import product
from pyneople.metadata.metadata_constants import AVATAR_SLOT_ID_LIST, EQUIPMENT_SLOT_ID_LIST

staging_table_to_columns = {}

base_equipments = [slot_id.lower() for slot_id in EQUIPMENT_SLOT_ID_LIST if slot_id not in ['WEAPON', 'TITLE']]
# 무기와 칭호를 제외한 나머지 장비 slotId
base_equipments = [slot_id for slot_id in base_equipments]

# 무기와 칭호를 제외한 나머지 장비에서 가져올 값
base_equipment_data = [
   'slot_name', 
   'item_id', 
   'item_name', 
   'item_available_level', 
   'item_rarity', 
   'set_item_name', 
   'reinforce', 
   'item_grade_name', 
   'enchant', 
   'amplification_name', 
   'fusion_option', 
   'upgrade_info_item_name', 
   'upgrade_info_item_rarity', 
   'upgrade_info_set_item_name', 
   'tune_level'
   ]

base_equipment_columns = [f"{i}_{j}" for i, j in product(base_equipments, base_equipment_data)]

from pyneople.metadata.metadata_constants import AVATAR_SLOT_ID_LIST
base_avatars = [slot_id.lower() for slot_id in AVATAR_SLOT_ID_LIST if slot_id not in ['AURA_SKIN']]
base_avatar_data = [
    'item_name', 
    'item_rarity', 
    'option_ability', 
    'emblems_0_item_name', 
    'emblems_1_item_name']
base_avatar_columns = [f"{i}_{j}" for i, j in product(base_avatars, base_avatar_data)]

endpoint_class = EndpointRegistry.get_class('character_info')
staging_table_to_columns[f'{endpoint_class.staging_table_name}'] = [
    'server_id',
    'character_id',
    'character_name',
    'level',
    'job_name',
    'job_grow_name',
    'fame',
    'adventure_name',
    'guild_id',
    'guild_name',
    'fetched_at'
    ]

endpoint_class = EndpointRegistry.get_class('character_status')
staging_table_to_columns[f'{endpoint_class.staging_table_name}'] = [
    'server_id',
    'character_id',
    'buff_adventure_level',
    'status_physical_defense_rate_value',
    'status_magical_defense_rate_value',
    'status_strength_value',
    'status_intelligence_value',
    'status_vitality_value',
    'status_spirit_value',
    'status_final_cooldown_reduction_rate_value',
    'fetched_at'
    ]

endpoint_class = EndpointRegistry.get_class('character_equipment')
staging_table_to_columns[f'{endpoint_class.staging_table_name}'] = [
    'server_id',
    'character_id',
    'weapon_item_id',
    'weapon_item_name',
    'weapon_item_type_detail',
    'weapon_item_available_level',
    'weapon_item_rarity',
    'weapon_reinforce',
    'weapon_item_grade_name',
    'weapon_enchant',
    'weapon_amplification_name',
    'weapon_refine',
    'weapon_engrave_name',
    'weapon_tune_level',
    'title_item_id',
    'title_item_name',
    'title_enchant'] + base_equipment_columns + [
       'magic_ston_potency_value',
       'earring_potency_value',
       'set_item_info',
       'fetched_at'
    ]

endpoint_class = EndpointRegistry.get_class('character_avatar')
staging_table_to_columns[f'{endpoint_class.staging_table_name}'] = [
    'server_id',
    'character_id'
    ] + base_avatar_columns + [
        'jacket_emblems_2_item_name',
        'pants_emblems_2_item_name',
        'aura_skin_item_name',
        'fetched_at'
    ]

endpoint_class = EndpointRegistry.get_class('character_flag')
staging_table_to_columns[f'{endpoint_class.staging_table_name}'] = [
    'server_id', 
    'character_id', 
    'item_rarity', 
    'reinforce', 
    'gems_0_item_rarity', 
    'gems_1_item_rarity', 
    'gems_2_item_rarity', 
    'gems_3_item_rarity', 
    'fetched_at'
    ]

endpoint_class = EndpointRegistry.get_class('character_creature')
staging_table_to_columns[f'{endpoint_class.staging_table_name}'] = [
    'server_id',
    'character_id',
    'item_name',
    'clone_item_name',
    'artifact_red_item_name',
    'artifact_red_item_available_level',
    'artifact_red_item_rarity',
    'artifact_blue_item_name',
    'artifact_blue_item_available_level',
    'artifact_blue_item_rarity',
    'artifact_green_item_name',
    'artifact_green_item_available_level',
    'artifact_green_item_rarity',
    'fetched_at'
    ]

endpoint_class = EndpointRegistry.get_class('character_buff_equipment')
staging_table_to_columns[f'{endpoint_class.staging_table_name}'] = [
    'server_id',
    'character_id',
    'buff_skill_info_name',
    'buff_skill_info_option_level',
    'equipment',
    'fetched_at'
    ]


def main():
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(BASE_DIR, f'../../db/schema/staging_table_to_columns.json')
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(staging_table_to_columns, f, ensure_ascii=False, indent=2) 

if __name__ == '__main__':
    main()        