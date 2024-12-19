import requests
import pytest
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000/api/v1"
TEST_MATCH_ID = 3788741  # Turquia vs Itália
TEST_PLAYER_ID = 11086.0  # Burak Yilmaz

def test_match_data_endpoint():
    """Testa o endpoint de dados brutos da partida"""
    logger.info("\n=== Testando endpoint de dados brutos ===")
    
    response = requests.get(f"{BASE_URL}/matches/{TEST_MATCH_ID}")
    assert response.status_code == 200
    
    data = response.json()
    assert data is not None
    assert 'events' in data
    
    logger.info(f"Número total de eventos: {len(data['events'])}")
    return data

def test_player_profile_endpoint():
    """Testa o endpoint de perfil do jogador"""
    logger.info("\n=== Testando endpoint de perfil do jogador ===")
    
    # Teste básico
    response = requests.get(f"{BASE_URL}/matches/{TEST_MATCH_ID}/player/{TEST_PLAYER_ID}")
    assert response.status_code == 200
    
    data = response.json()
    assert data is not None
    assert 'info' in data
    assert 'statistics' in data
    
    # Verificar informações do jogador
    info = data['info']
    assert info['player_name'] == 'Burak Yılmaz'
    assert info['team'] == 'Turkey'
    
    # Verificar estatísticas
    stats = data['statistics']
    assert 'passes' in stats
    assert 'shots' in stats
    assert 'tackles' in stats
    
    logger.info(f"Estatísticas do jogador {info['player_name']}:")
    logger.info(f"Passes: {stats['passes']}")
    logger.info(f"Finalizações: {stats['shots']}")
    
    # Teste com análise LLM
    response = requests.get(
        f"{BASE_URL}/matches/{TEST_MATCH_ID}/player/{TEST_PLAYER_ID}?include_analysis=true"
    )
    assert response.status_code == 200
    data = response.json()
    assert 'analysis' in data
    
    logger.info("Análise LLM gerada com sucesso")
    return data

def test_match_summary_endpoint():
    """Testa o endpoint de sumarização da partida"""
    logger.info("\n=== Testando endpoint de sumarização ===")
    
    response = requests.get(f"{BASE_URL}/matches/{TEST_MATCH_ID}/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert data is not None
    assert 'match_id' in data
    assert 'goals' in data
    assert 'cards' in data
    
    logger.info(f"Gols marcados: {len(data['goals'])}")
    logger.info(f"Cartões mostrados: {len(data['cards'])}")
    
    # Verificar estrutura dos gols
    if data['goals']:
        goal = data['goals'][0]
        assert all(k in goal for k in ['minute', 'team', 'scorer'])
    
    # Verificar estrutura dos cartões
    if data['cards']:
        card = data['cards'][0]
        assert all(k in card for k in ['minute', 'team', 'player', 'card_type'])
    
    return data

def test_match_analysis_endpoint():
    """Testa o endpoint de análise narrativa"""
    logger.info("\n=== Testando endpoint de análise narrativa ===")
    
    styles = ['formal', 'humoristico', 'tecnico']
    results = {}
    
    for style in styles:
        logger.info(f"\nTestando estilo: {style}")
        response = requests.get(f"{BASE_URL}/matches/{TEST_MATCH_ID}/analysis?style={style}")
        assert response.status_code == 200
        
        data = response.json()
        assert data is not None
        assert 'analysis' in data
        
        analysis = data['analysis']
        assert all(k in analysis for k in ['match_id', 'events_summary', 'style', 'narrative'])
        assert analysis['style'] == style
        assert isinstance(analysis['narrative'], str)
        assert len(analysis['narrative']) > 100  # Garantir que a narrativa tem conteúdo substancial
        
        logger.info(f"Tamanho da narrativa: {len(analysis['narrative'])} caracteres")
        results[style] = analysis
    
    # Testar erro com estilo inválido
    response = requests.get(f"{BASE_URL}/matches/{TEST_MATCH_ID}/analysis?style=invalido")
    assert response.status_code == 400
    
    return results

def run_all_tests():
    """Executa todos os testes em sequência"""
    logger.info("Iniciando testes de integração da API...")
    
    try:
        match_data = test_match_data_endpoint()
        logger.info("✅ Teste de dados da partida passou")
        
        player_profile = test_player_profile_endpoint()
        logger.info("✅ Teste de perfil do jogador passou")
        
        match_summary = test_match_summary_endpoint()
        logger.info("✅ Teste de sumarização passou")
        
        analysis_results = test_match_analysis_endpoint()
        logger.info("✅ Teste de análise narrativa passou")
        
        logger.info("\n🎉 Todos os testes passaram com sucesso!")
        
    except Exception as e:
        logger.error(f"\n❌ Erro durante os testes: {str(e)}")
        raise

if __name__ == "__main__":
    run_all_tests()
