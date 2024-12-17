import os
import sys
from dotenv import load_dotenv

# Adiciona o diretório raiz ao PYTHONPATH
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Carrega as variáveis de ambiente
load_dotenv()

from api.services.match_analysis import MatchAnalyzer

def test_match_analysis():
    """
    Testa a análise tática de uma partida usando LLM.
    """
    # ID da partida da Copa do Mundo Feminina 2019
    MATCH_ID = 69301  # USA vs Thailand
    
    print("\n=== Testando Análise de Partida ===")
    
    # Instanciar o analisador
    analyzer = MatchAnalyzer()
    
    # Primeiro, testar o resumo da partida
    print("\nObtendo resumo da partida...")
    match_summary = analyzer.summarize_match(MATCH_ID)
    
    if match_summary:
        print("\nResumo dos Eventos:")
        print(f"Total de Gols: {len(match_summary['goals'])}")
        print(f"Total de Cartões: {len(match_summary['cards'])}")
        
        print("\nGols:")
        for goal in match_summary['goals']:
            print(f"⚽ Minuto {goal['minute']}: {goal['scorer']} ({goal['team']})")
        
        print("\nCartões:")
        for card in match_summary['cards']:
            print(f"🟨 Minuto {card['minute']}: {card['player']} ({card['team']}) - {card['card_type']}")
    else:
        print("❌ Erro ao obter resumo da partida")
        return

    # Agora, testar a análise com LLM
    print("\nGerando análise tática...")
    match_analysis = analyzer.analyze_with_llm(MATCH_ID)
    
    if match_analysis:
        print("\nAnálise Tática:")
        print("-" * 50)
        print(match_analysis['tactical_analysis'])
    else:
        print("❌ Erro ao gerar análise tática")

if __name__ == "__main__":
    print("Iniciando testes de análise...")
    test_match_analysis()
