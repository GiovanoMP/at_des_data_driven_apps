import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("\nTestando a API de Análise de Futebol...")
    
    # Teste 1: Endpoint raiz
    print("\n1. Testando endpoint raiz...")
    response = requests.get(f"{BASE_URL}/api/v1")
    if response.status_code == 200:
        print("✓ Endpoint raiz OK!")
    else:
        print("✗ Erro no endpoint raiz:", response.status_code)
    
    # Teste 2: Dados da partida
    print("\n2. Testando endpoint de dados da partida...")
    match_id = 3788741
    response = requests.get(f"{BASE_URL}/api/v1/matches/{match_id}")
    if response.status_code == 200:
        print("✓ Endpoint de dados da partida OK!")
        data = response.json()
        print(f"   Número de eventos na partida: {len(data['events'])}")
    else:
        print("✗ Erro no endpoint de dados da partida:", response.status_code)

if __name__ == "__main__":
    try:
        test_api()
        print("\nTodos os testes concluídos!")
    except Exception as e:
        print(f"\nErro durante os testes: {str(e)}")
        print("Certifique-se de que a API está rodando em http://localhost:8000")
