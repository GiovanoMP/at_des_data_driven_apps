from statsbombpy import sb
import pandas as pd
import json

def debug_match_events():
    match_id = 3788741  # Turkey vs Italy
    player_id = 7037    # Lorenzo Insigne

    print("Obtendo eventos da partida...")
    events = sb.events(match_id=match_id)
    
    if events is None or events.empty:
        print("Nenhum evento encontrado!")
        return

    print("\nPrimeiros eventos da partida:")
    print(events.head())
    
    print("\nColunas disponíveis:")
    print(events.columns.tolist())
    
    print("\nProcurando eventos do Insigne...")
    # Tentar diferentes maneiras de encontrar eventos do jogador
    player_events = events[events['player'].notna()]
    
    print("\nExemplo de um evento com informações do jogador:")
    sample_event = player_events.iloc[0]
    print(json.dumps(sample_event.to_dict(), indent=2))
    
    # Tentar encontrar eventos específicos do Insigne
    insigne_events = player_events[player_events['player'].apply(lambda x: isinstance(x, dict) and str(x.get('id')) == str(player_id))]
    
    print(f"\nNúmero de eventos encontrados para Insigne: {len(insigne_events)}")
    if not insigne_events.empty:
        print("\nPrimeiro evento do Insigne:")
        print(json.dumps(insigne_events.iloc[0].to_dict(), indent=2))

if __name__ == "__main__":
    debug_match_events()
