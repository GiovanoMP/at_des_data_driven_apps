import json
import os
from typing import Dict, List, Any
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_json_file(filename: str) -> List[Dict[str, Any]]:
    try:
        current_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        file_path = os.path.join(current_dir, 'tests', 'statsbomb_samples', filename)
        logger.info(f"Loading file: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            logger.info(f"Successfully loaded {filename}")
            return data
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Invalid JSON in file: {filename}")
        return []
    except Exception as e:
        logger.error(f"Error loading {filename}: {str(e)}")
        return []

# Carregar dados de exemplo
matches_data = load_json_file('matches.json')
competitions_data = load_json_file('competitions.json')
lineup_england_data = load_json_file('lineup_England.json')
lineup_colombia_data = load_json_file('lineup_Colombia.json')
events_data = load_json_file('events.json')

# Verificar se os dados foram carregados
logger.info(f"Loaded {len(matches_data)} matches")
logger.info(f"Loaded {len(competitions_data)} competitions")
logger.info(f"Loaded {len(lineup_england_data)} England players")
logger.info(f"Loaded {len(lineup_colombia_data)} Colombia players")
logger.info(f"Loaded {len(events_data)} events")
