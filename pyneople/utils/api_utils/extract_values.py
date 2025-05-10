import logging

logger = logging.getLogger(__name__)

def _get_nested_value(data, path):
    """
    list를 포함한 중첩 dict에서 path를 기반으로 탐색 후 해당 데이터를 반환하는 함수

    path는 tuple이며 원소로 str, int, tuple(str, Any)를 가질 수 있다.
    str은 dict의 key, int는 list의 index, tuple은 list내부의 dict의 key와 value를 매칭해서 탐색한다.
    path의 첫번째 값은 str을 가정한다.
    """
    current = data
    # print(current)
    first_key = path[0]
    current = current.get(first_key)  

    for step in path[1:]:
        #print(current)
        if current is None:
            # print(current)
            # print(path)
            # print(step)
            # print("커런트 없음")
            # raise Exception
            return current

        if isinstance(step, tuple):
            key, value = step
            if not isinstance(current, list):
                logger.info(f"Expected list at {step}, got {type(current)}")
                # return None
                raise TypeError(f"Expected list at {step}, got {type(current)}")
            for item in current:
                if isinstance(item, dict) and item.get(key) == value:
                    current = item
                    break
            else:
                # raise ValueError(f"No matching item for {step}")
                # logger.info(f"No matching item for {step}")
                # print('리스트 다 돌았는데 없음')
                return None
        elif isinstance(step, int):

            if isinstance(current, list):
                if 0 <= step < len(current):
                    current = current[step]                
                else:
                    logger.debug('Out of index')
                    return None
        else:
            if not isinstance(current, dict):
                # logger.info(f"Expected dict at {step}, got {type(current)}")
                raise TypeError(f"Expected dict at {step}, got {type(current)}")
            current = current.get(step)  
    return current

def extract_values(data, columns, data_map):
    """특정 데이터의 path를 기록한 path_map을 이용해 원하는 데이터만 가져오는 함수"""
    return {name: _get_nested_value(data, data_map[name]) for name in columns if data_map.get(name)}