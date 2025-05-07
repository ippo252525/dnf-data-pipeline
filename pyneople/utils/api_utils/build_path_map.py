def build_data_path_map(data, current_path=(), identifier_key=None):
    """
    마킹된 데이터를 바탕으로 마킹 값을 key, 마킹 값에 도달하기 위한 path을 value로 가지는 dict를 반환하는 함수
    """
    result = {}

    if isinstance(data, dict):
        for key, value in data.items():
            path = current_path + (key,)
            if isinstance(value, (dict, list)):
                result.update(build_data_path_map(value, path, identifier_key))
            elif isinstance(value, str) and value.startswith("__") and value.endswith("__"):
                result[value.strip("__")] = path

    elif isinstance(data, list):
        for index, item in enumerate(data):
            if isinstance(item, dict) and identifier_key in item:
                path = current_path + ((identifier_key, item[identifier_key]),)
            else:
                path = current_path + (index,)
            result.update(build_data_path_map(item, path, identifier_key))

    return result
