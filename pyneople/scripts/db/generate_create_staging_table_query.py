"""
스테이징 테이블 생성 쿼리를 저장하는 스크립트
스테이징 테이블 이름을 key로 각 스테이징 테이블에 사용 할 column list를 value로 가지는 db/schema/staging_table_to_columns.josn 파일이 있다면 해당 컬럼을 이용함
없다면 사용 가능한 모든 값을 column으로 이용함
"""

import json
import os
import pyneople.api.registry.endpoint_class
from pyneople.api.registry.endpoint_registry import EndpointRegistry
from pyneople.utils.db_utils.query_builder import build_create_table_query
from pyneople.utils.db_utils.psql_connection import psql_connection
if __name__ == "__main__":
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(BASE_DIR, f'../../db/endpoint_to_column_dtype_map.json'), 'r', encoding='utf-8') as f:
        endpoint_to_column_dtype_dict = json.load(f)
    endpoints = EndpointRegistry.get_registered_endpoints()    
    
    # 미리 사용 할 컬럼을 작성했다면 해당 정보를 받아온다다
    try:
        with open(os.path.join(BASE_DIR, f'../../db/schema/staging_table_to_columns.json'), 'r', encoding='utf-8') as f:
            staging_table_to_columns = json.load(f)
    except:
        staging_table_to_columns = None

    with psql_connection() as conn:
        for endpoint in endpoints:
            if endpoint in ['character_fame', 'character_timeline']:
                continue
            column_dtype_dict = endpoint_to_column_dtype_dict[endpoint]
            endpoint_class = EndpointRegistry.get_class(endpoint)
            staging_table_name = endpoint_class.staging_table_name
            sql_path = os.path.join(BASE_DIR, f'../../db/schema/staging_tables/{staging_table_name}.sql')
            
            if staging_table_to_columns.get(staging_table_name):
                columns = staging_table_to_columns[staging_table_name]    
            else:
                columns = endpoint_class.data_path_map.keys()

            columns = {column : column_dtype_dict[column] for column in columns}
            query = build_create_table_query(staging_table_name, columns)
            query_str = query.as_string(conn)
            
            with open(sql_path, "w", encoding="utf-8") as f:
                f.write(query_str)  
        
