# pyneople에서 사용되는 함수와 클래스입니다.

import re
from pyneople.metadata.metadata_constants import SAME_BUFF_SKILL_NAMES
class NotFoundCharacterError(Exception):
    """
    404 해당 캐릭터 없음 Error 핸들링을 위한 Class
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

class RetryableError(Exception):
    """
    재시도 가능한 Error 핸들링을 위한 Class
    """
    def __init__(self, *args: object) -> None:
        super().__init__(*args)    

def to_snake_case(string : str) -> str:
    """
    모든 문자가 대문자면 소문자로 변환, 나머지는 스네이크 케이스로 반환하는 함수
    """
    return string.lower() if string.isupper() else re.sub(r'(?<!^)(?=[A-Z])', '_', string).lower()

def format_enchant_info(arg_enchant_dict : dict):
    """
    마법부여 정보를 정리해주는 함수
        Args :
            arg_enchant_dict(dict) : 마법부여 정보 dict
    """
    if arg_enchant_dict == {} or arg_enchant_dict == None:
        return None
    output = ""
    if "status" in arg_enchant_dict.keys():
        output = ", ".join([f"{s['name']} {s['value']}" for s in arg_enchant_dict['status']])
    if "reinforceSkill" in arg_enchant_dict.keys():
        output = ", ".join([f"{s['name']} {s['value']}" for r in arg_enchant_dict['reinforceSkill'] for s in r['skills']]) + ", " + output 
    if "explain" in arg_enchant_dict.keys():
        output = arg_enchant_dict['explain'] + ", " + output
    return output

def format_fusion_option_info(fusion_option_info : dict) -> str:
    """
    융합 옵션 정보를 정리해서 반환하는 함수

    융합석 각인이 가능한 경우만 해당 옵션을 ||로 연결해서 str로 반환한다다
    """

    if fusion_option_info:
        if len(fusion_option_info.get('options', [])) == 3:
            fusion_option_info_list = []
            for fusion_option in fusion_option_info['options']:
                if fusion_option.get('explain') or fusion_option.get('buffExplain'):
                    fusion_option_info_list.append(fusion_option.get('explain') or fusion_option.get('buffExplain'))
            return "||".join(fusion_option_info_list) 
    return None

def format_buff_equipment_info(buff_equipment_info : list, buff_name : str, job_name : str) -> int:
    """
    버프강화 장비 정보를 정리해서 반환하는 함수

    2025년 5월 10일 기준으로 버프강화 장비는 짙은 심연의 편린을 제외한 다른 자료가 무의미함
    장비에서 짙은 심연의 편린이 몇개인지 반환한다.
    """
    result = 0
    buff_name = buff_name.replace(" ", "")
    # 남여가 같은 버프 이름을 공유하는 경우는 성별을 표시한다
    if buff_name in SAME_BUFF_SKILL_NAMES:
        buff_name = buff_name + job_name[-3:]

    for equipment in buff_equipment_info:
        if not equipment.get('itemName'):
            continue
        else:
            equipment_name = equipment['itemName']
            if equipment_name.startswith('짙은 심연의 편린'):
                equipment_buff_name = equipment_name.split(":")[-1].replace(" ", "")
                if equipment_buff_name == buff_name:
                    result += 1
    return result    

        
        

def format_buff_skill_info(buff_skill_info : dict) -> str:
    return buff_skill_info['name']
    