import json
import pandas as pd

def analyze_structure():
    """
    Analisa a estrutura dos dados da StatsBomb
    """
    # Analisar eventos
    with open('tests/statsbomb_samples/events.json', 'r', encoding='utf-8') as f:
        events = pd.read_json(f)
        print("\n=== Estrutura dos Eventos ===")
        print("Colunas disponíveis:")
        print(events.columns.tolist())
        
        # Analisar eventos de gol
        goals = events[events['shot'].notna() & events['shot'].apply(lambda x: x.get('outcome', {}).get('name') == 'Goal')]
        if not goals.empty:
            print("\nEstrutura de um evento de gol:")
            print(json.dumps(goals.iloc[0].to_dict(), indent=2))

    # Analisar partidas
    with open('tests/statsbomb_samples/matches.json', 'r', encoding='utf-8') as f:
        matches = pd.read_json(f)
        print("\n=== Estrutura das Partidas ===")
        print("Colunas disponíveis:")
        print(matches.columns.tolist())
        if not matches.empty:
            print("\nEstrutura de uma partida:")
            print(json.dumps(matches.iloc[0].to_dict(), indent=2))

if __name__ == "__main__":
    analyze_structure()
