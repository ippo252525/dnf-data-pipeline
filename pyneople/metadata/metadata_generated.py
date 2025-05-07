import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METADATA_FILE = os.path.join(BASE_DIR, 'metadata_generated.json')

with open(METADATA_FILE, 'r', encoding='utf-8') as f:
    GENERATED_METADATA = json.load(f)

TABLE_COLUMNS_MAP = GENERATED_METADATA['table_columns_map']
PARAMS_FOR_SEED_CHARACTER_FAME = GENERATED_METADATA['params_for_seed_character_fame']