import pytest
from fastapi.testclient import TestClient
from api.main import app
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dados de exemplo para testes
SAMPLE_MATCH_ID = 3788741  # ID de uma partida real do dataset aberto do StatsBomb
SAMPLE_PLAYER_ID = 5503  # ID de um jogador real do dataset aberto do StatsBomb

@pytest.fixture
def test_client():
    """
    Fixture que fornece um cliente de teste para a API.
    """
    return TestClient(app)

def test_root(test_client):
    """
    Testa o endpoint raiz da API.
    """
    response = test_client.get("/api/v1")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["message"] == "Welcome to the Football Analysis API"

def test_get_match(test_client):
    """
    Testa o endpoint de obtenção de dados brutos de uma partida.
    """
    response = test_client.get(f"/api/v1/matches/{SAMPLE_MATCH_ID}")
    assert response.status_code == 200
    data = response.json()
    assert "match_info" in data
    assert "events" in data
    assert "lineups" in data

def test_get_match_summary(test_client):
    """
    Testa o endpoint de resumo da partida.
    """
    response = test_client.get(f"/api/v1/matches/{SAMPLE_MATCH_ID}/summary")
    assert response.status_code == 200
    data = response.json()
    assert "match_info" in data
    assert "key_events" in data
    
    # Verificar estrutura dos eventos chave
    key_events = data["key_events"]
    assert "goals" in key_events
    assert "cards" in key_events
    assert "substitutions" in key_events

def test_get_match_narrative(test_client):
    """
    Testa o endpoint de geração de narrativa da partida.
    """
    # Testar cada estilo de narração
    styles = ["formal", "humorous", "technical"]
    
    for style in styles:
        response = test_client.get(
            f"/api/v1/matches/{SAMPLE_MATCH_ID}/narrative",
            params={"style": style}
        )
        assert response.status_code == 200
        data = response.json()
        assert "narrative" in data
        assert len(data["narrative"]) > 0
        logger.info(f"Narrativa gerada com estilo {style}")

def test_get_player_profile(test_client):
    """
    Testa o endpoint de perfil do jogador.
    """
    # Testar sem análise detalhada
    response = test_client.get(
        f"/api/v1/matches/{SAMPLE_MATCH_ID}/player/{SAMPLE_PLAYER_ID}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "info" in data
    assert "statistics" in data
    
    # Testar com análise detalhada
    response = test_client.get(
        f"/api/v1/matches/{SAMPLE_MATCH_ID}/player/{SAMPLE_PLAYER_ID}",
        params={"include_analysis": True}
    )
    assert response.status_code == 200
    data = response.json()
    assert "info" in data
    assert "statistics" in data
    assert "analysis" in data

def test_invalid_match_id(test_client):
    """
    Testa o comportamento da API com um ID de partida inválido.
    """
    invalid_id = 99999999
    response = test_client.get(f"/api/v1/matches/{invalid_id}")
    assert response.status_code == 404

def test_invalid_player_id(test_client):
    """
    Testa o comportamento da API com um ID de jogador inválido.
    """
    invalid_id = 99999999
    response = test_client.get(f"/api/v1/matches/{SAMPLE_MATCH_ID}/player/{invalid_id}")
    assert response.status_code == 404

def test_invalid_narrative_style(test_client):
    """
    Testa o comportamento da API com um estilo de narração inválido.
    """
    response = test_client.get(
        f"/api/v1/matches/{SAMPLE_MATCH_ID}/narrative",
        params={"style": "invalid_style"}
    )
    assert response.status_code == 422  # Erro de validação
