import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_match_endpoint():
    """Testa o endpoint de partida"""
    match_id = 3788741
    response = requests.get(f"{BASE_URL}/matches/{match_id}")
    print("\nTeste do endpoint de partida:")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Dados recebidos com sucesso!")
        print(f"Informações da partida: {json.dumps(data.get('match_info', {}), indent=2)}")
        
        # Mostrar jogadores disponíveis
        if 'lineups' in data:
            print("\nJogadores disponíveis:")
            for team, lineup in data['lineups'].items():
                print(f"\n{team}:")
                for player in lineup:
                    print(f"ID: {player.get('player_id', 'N/A')} - Nome: {player.get('player_name', 'N/A')}")
    else:
        print(f"Erro: {response.text}")

def test_match_analysis():
    """Testa o endpoint de análise de partida"""
    match_id = 3788741
    response = requests.get(f"{BASE_URL}/matches/{match_id}/analysis")
    print("\nTeste do endpoint de análise:")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Análise recebida com sucesso!")
        print(f"Análise tática: {data.get('tactical_analysis', '')[:200]}...")  # Primeiros 200 caracteres
    else:
        print(f"Erro: {response.text}")

def test_match_narrative_analysis():
    """Testa o endpoint de análise narrativa"""
    match_id = 3788741  # Turquia vs Itália
    
    # Testar diferentes estilos
    styles = ['formal', 'humoristico', 'tecnico']
    
    for style in styles:
        response = requests.get(f"{BASE_URL}/matches/{match_id}/analysis?style={style}")
        print(f"\nTeste do endpoint de análise ({style}):")
        print(f"Status: {response.status_code}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data is not None
        assert 'match_id' in data
        assert 'events_summary' in data
        assert 'style' in data
        assert data['style'] == style
        assert 'narrative' in data
        assert isinstance(data['narrative'], str)
        assert len(data['narrative']) > 0
    
    # Testar estilo inválido
    response = requests.get(f"{BASE_URL}/matches/{match_id}/analysis?style=invalido")
    assert response.status_code == 400

def test_player_profile():
    """Testa o endpoint de perfil de jogador"""
    match_id = 3788741
    player_id = 11086  # Burak Yilmaz
    response = requests.get(f"{BASE_URL}/matches/{match_id}/player/{player_id}?include_analysis=true")
    print("\nTeste do endpoint de perfil de jogador:")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print("Perfil recebido com sucesso!")
        print(f"Informações do jogador: {json.dumps(data.get('info', {}), indent=2)}")
        if 'analysis' in data:
            print(f"Análise do jogador: {data['analysis'][:200]}...")  # Primeiros 200 caracteres
    else:
        print(f"Erro: {response.text}")

def test_match_summary():
    """Testa o endpoint de sumarização de partida"""
    match_id = 3788741  # Turquia vs Itália
    response = requests.get(f"{BASE_URL}/matches/{match_id}/summary")
    
    print("\nTeste do endpoint de sumarização:")
    print(f"Status: {response.status_code}")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data is not None
    assert 'match_id' in data
    assert 'goals' in data
    assert 'cards' in data
    
    # Verificar estrutura dos gols
    if data['goals']:
        goal = data['goals'][0]
        assert 'minute' in goal
        assert 'team' in goal
        assert 'scorer' in goal
    
    # Verificar estrutura dos cartões
    if data['cards']:
        card = data['cards'][0]
        assert 'minute' in card
        assert 'team' in card
        assert 'player' in card
        assert 'card_type' in card

if __name__ == "__main__":
    print("Iniciando testes dos endpoints...")
    test_match_endpoint()
    test_match_analysis()
    test_match_narrative_analysis()
    test_player_profile()
    test_match_summary()
