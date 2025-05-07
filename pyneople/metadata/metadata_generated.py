import pickle
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
METADATA_FILE = os.path.join(BASE_DIR, 'metadata_generated.pkl')

with open(METADATA_FILE, 'rb') as f:
    GENERATED_METADATA = pickle.load(f)

TABLE_COLUMNS_MAP = GENERATED_METADATA['table_columns_map']
PARAMS_FOR_SEED_CHARACTER_FAME = GENERATED_METADATA['params_for_seed_character_fame']