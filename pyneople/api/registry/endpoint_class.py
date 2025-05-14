from abc import ABC, abstractmethod

from pyneople.api.registry.endpoint_registry import register_endpoint

from pyneople.api.preprocessors.character_info_preprocessor import preprocess_character_info
from pyneople.api.preprocessors.character_fame_preprocessor import preprocess_character_fame
from pyneople.api.preprocessors.character_timeline_preprocessor import preprocess_character_timeline
from pyneople.api.preprocessors.character_status_preprocessor import preprocess_character_status
from pyneople.api.preprocessors.character_equipment_preprocessor import preprocess_character_equipment
from pyneople.api.preprocessors.character_avatar_preprocessor import preprocess_character_avatar
from pyneople.api.preprocessors.character_creature_preprocessor import preprocess_character_creature
from pyneople.api.preprocessors.character_flag_preprocessor import preprocess_character_flag
from pyneople.api.preprocessors.character_buff_equipment_preprocessor import preprocess_character_buff_equipment
from pyneople.api.preprocessors.character_buff_avatar_preprocessor import preprocess_character_buff_avatar
from pyneople.api.preprocessors.character_buff_creature_preprocessor import preprocess_character_buff_creature

from pyneople.api.data_path_map import (
    CHARACTER_INFO_DATA_PATH_MAP,
    CHARACTER_TIMELINE_DATA_PATH_MAP,
    CHARACTER_STATUS_DATA_PATH_MAP,
    CHARACTER_EQUIPMENT_DATA_PATH_MAP,
    CHARACTER_AVATAR_DATA_PATH_MAP,
    CHARACTER_CREATURE_DATA_PATH_MAP,
    CHARACTER_FLAG_DATA_PATH_MAP,
    CHARACTER_BUFF_EQUIPMENT_DATA_PATH_MAP,
    CHARACTER_BUFF_AVATAR_DATA_PATH_MAP,
    CHARACTER_BUFF_CREATURE_DATA_PATH_MAP,
    CHARACTER_FAME_DATA_PATH_MAP
)


from pyneople.api.seeders.character_base_seeder import CharacterBaseSeeder
from pyneople.api.seeders.character_fame_seeder import CharacterFameSeeder
from pyneople.api.seeders.character_timeline_seeder import CharacterTimelineSeeder

from pyneople.api.next_builders.build_next_character_fmae_api_request import build_next_character_fame_api_request
from pyneople.api.next_builders.build_next_character_timeline_api_request import build_next_character_timeline_api_request

class BaseEndpoint(ABC):
    """모든 엔드포인트 클래스가 상속받는 기본 베이스 클래스."""
    staging_table_name: str
    accepts_sql: bool = True
    seeder: type = CharacterBaseSeeder
    has_next: bool = False
    has_character_info_data = True
    data_path_map: dict = None
    
    @staticmethod
    @abstractmethod
    def preprocess(data, columns):
        pass
    
    @staticmethod
    def build_next_api_request(data : dict, api_request : dict):
        """기본 next api request 생성 메서드. (필요한 엔드포인트에서만 오버라이드)"""
        return None

# 캐릭터 기본 정보 조회
@register_endpoint('character_info')
class CharacterInfo(BaseEndpoint):
    staging_table_name = 'staging_character_info'
    has_character_info_data = False
    data_path_map = CHARACTER_INFO_DATA_PATH_MAP

    @staticmethod
    def preprocess(data, columns):
        return preprocess_character_info(data, columns)

# 캐릭터 타임라인 정보 조회    
@register_endpoint('character_timeline')
class CharacterTimeline(BaseEndpoint):
    staging_table_name = 'staging_character_timeline'
    seeder = CharacterTimelineSeeder
    data_path_map = CHARACTER_TIMELINE_DATA_PATH_MAP

    @staticmethod
    def preprocess(data, columns):
        return preprocess_character_timeline(data, columns)

    @staticmethod
    def build_next_api_request(data: dict, api_request: dict):
        return build_next_character_timeline_api_request(data, api_request)

# 캐릭터 능력치 정보 조회
@register_endpoint('character_status')
class CharacterStatus(BaseEndpoint):
    staging_table_name = 'staging_character_status'
    data_path_map = CHARACTER_STATUS_DATA_PATH_MAP

    @staticmethod
    def preprocess(data, columns):
        return preprocess_character_status(data, columns)

# 캐릭터 장착 장비 조회
@register_endpoint('character_equipment')
class CharacterEquipment(BaseEndpoint):
    staging_table_name = 'staging_character_equipment'
    data_path_map = CHARACTER_EQUIPMENT_DATA_PATH_MAP

    @staticmethod
    def preprocess(data, columns):
        return preprocess_character_equipment(data, columns)

# 캐릭터 장착 아바타 조회
@register_endpoint('character_avatar')
class CharacterAvatar(BaseEndpoint):
    staging_table_name = 'staging_character_avatar'
    data_path_map = CHARACTER_AVATAR_DATA_PATH_MAP
    
    @staticmethod
    def preprocess(data, columns):
        return preprocess_character_avatar(data, columns)

# 캐릭터 장착 크리쳐 조회
@register_endpoint('character_creature')
class CharacterCreature(BaseEndpoint):
    staging_table_name = 'staging_character_creature'
    data_path_map = CHARACTER_CREATURE_DATA_PATH_MAP

    @staticmethod
    def preprocess(data, columns):
        return preprocess_character_creature(data, columns)

# 캐릭터 장착 휘장 조회
@register_endpoint('character_flag')
class CharacterFlag(BaseEndpoint):
    staging_table_name = 'staging_character_flag'
    data_path_map = CHARACTER_FLAG_DATA_PATH_MAP

    @staticmethod
    def preprocess(data, columns):
        return preprocess_character_flag(data, columns)

# 캐릭터 버프 스킬 강화 장착 장비 조회
@register_endpoint('character_buff_equipment')
class CharacterBuffEquipment(BaseEndpoint):
    staging_table_name = 'staging_character_buff_equipment'
    data_path_map = CHARACTER_BUFF_EQUIPMENT_DATA_PATH_MAP

    @staticmethod
    def preprocess(data, columns):
        return preprocess_character_buff_equipment(data, columns)

# # 캐릭터 버프 스킬 강화 장착 아바타 조회
# @register_endpoint('character_buff_avatar')
# class CharacterBuffAvatar(BaseEndpoint):
#     staging_table_name = 'staging_character_buff_avatar'
#     data_path_map = CHARACTER_BUFF_AVATAR_DATA_PATH_MAP

#     @staticmethod
#     def preprocess(data, columns):
#         return preprocess_character_buff_avatar(data, columns)

# # 캐릭터 버프 스킬 강화 장착 크리쳐 조회
# @register_endpoint('character_buff_creature')
# class CharacterBuffCreature(BaseEndpoint):
#     staging_table_name = 'staging_character_buff_creature'
#     data_path_map = CHARACTER_BUFF_CREATURE_DATA_PATH_MAP

#     @staticmethod
#     def preprocess(data, columns):
#         return preprocess_character_buff_creature(data, columns)

# 캐릭터 명성 검색
@register_endpoint('character_fame')
class CharacterFame(BaseEndpoint):
    staging_table_name = 'staging_character_fame'
    accepts_sql = False
    seeder = CharacterFameSeeder
    has_next = True
    has_character_info_data = False
    data_path_map = CHARACTER_FAME_DATA_PATH_MAP

    @staticmethod
    def preprocess(data, columns):
        return preprocess_character_fame(data, columns)

    @staticmethod
    def build_next_api_request(data: dict, api_request : dict):
        return build_next_character_fame_api_request(data, api_request)