import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_connection():
    # Carregar variáveis de ambiente
    load_dotenv()
    
    # Obter a chave API
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("[ERRO] GOOGLE_API_KEY não encontrada no arquivo .env")
        return
    
    try:
        # Configurar o Gemini
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Tentar gerar uma resposta simples
        response = model.generate_content("Olá! Por favor, responda com 'Conexão OK' se você estiver funcionando.")
        
        if response and response.text:
            print("[OK] Teste bem-sucedido!")
            print(f"Resposta do Gemini: {response.text.strip()}")
        else:
            print("[ERRO] Não foi possível obter uma resposta do modelo")
            
    except Exception as e:
        print(f"[ERRO] Erro ao conectar com o Gemini: {str(e)}")

if __name__ == "__main__":
    test_gemini_connection()
