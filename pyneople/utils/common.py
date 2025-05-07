# pyneople에서 사용되는 함수와 클래스입니다.

import re

class NotFoundCharacterError(Exception):
    """
    404 해당 캐릭터 없음 Error 핸들링을 위한 Class
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

{'options': [{'explain': '최종 데미지 4% 증가', 'explainDetail': '최종 데미지 4% 증가'},
  {'explain': '최종 데미지 4% 증가', 'explainDetail': '최종 데미지 4% 증가'},
  {'engrave': {'color': 'gold', 'value': 3},
   'explain': '최종 데미지 5.5% 증가',
   'explainDetail': '최종 데미지 5.5% 증가'}]}

def format_fusion_option_info(fusion_option_info : dict) -> str:
    """
    융합 옵션 정보를 정리해서 반환하는 함수

    융합석 각인이 가능한 경우만 해당 옵션을 ||로 연결해서 str로 반환한다다
    """
    if fusion_option_info:
        if len(fusion_option_info.get('options', [])) == 3:
            return "||".join([fusion_option.get('explain') for fusion_option in fusion_option_info['options']]) 
    return None

def format_buff_skill_info(buff_skill_info : dict) -> str:
    return buff_skill_info['name']
    