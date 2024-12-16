from statsbombpy import sb
import pandas as pd
import json
import os

def explore_statsbomb_structure():
    """
    Script para explorar e salvar a estrutura real dos dados da StatsBomb
    """
    try:
        # Cria diretório para os resultados se não existir
        os.makedirs('tests/statsbomb_samples', exist_ok=True)
        
        # Lista competições disponíveis
        competitions = sb.competitions()
        competitions.to_json('tests/statsbomb_samples/competitions.json', orient='records')
        print("✓ Dados das competições salvos")
        
        # Pega partidas de exemplo
        matches = sb.matches(competition_id=43, season_id=3)
        matches.to_json('tests/statsbomb_samples/matches.json', orient='records')
        print("✓ Dados das partidas salvos")
        
        # Pega uma partida específica para exemplo
        sample_match_id = matches.iloc[0]['match_id']
        
        # Explora eventos da partida
        events = sb.events(match_id=sample_match_id)
        events.to_json('tests/statsbomb_samples/events.json', orient='records')
        print("✓ Dados dos eventos salvos")
        
        # Explora escalações
        lineups = sb.lineups(match_id=sample_match_id)
        
        # Salva dados de cada time
        for team, players in lineups.items():
            players.to_json(f'tests/statsbomb_samples/lineup_{team}.json', orient='records')
        print("✓ Dados das escalações salvos")
        
        print("\nTodos os dados foram salvos em tests/statsbomb_samples/")
        print("Agora podemos analisar a estrutura exata dos dados para criar nossos modelos.")
            
    except Exception as e:
        print(f"Erro ao explorar dados: {str(e)}")

if __name__ == "__main__":
    explore_statsbomb_structure()
