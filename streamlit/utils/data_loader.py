import pandas as pd
import requests
from typing import Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

# Configura o Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def load_match_data(match_id: str) -> Dict[str, Any]:
    """
    Carrega os dados de uma partida específica.
    Será implementado para integrar com a API FastAPI.
    """
    try:
        # Aqui será implementada a chamada à API FastAPI
        api_url = f"http://localhost:8000/api/v1/matches/{match_id}/summary"
        response = requests.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Erro ao buscar dados: {response.status_code}")
    except Exception as e:
        raise Exception(f"Erro ao carregar dados da partida: {str(e)}")

def process_match_data_with_gemini(data: Dict[str, Any], query: str) -> str:
    """
    Processa os dados da partida usando o Gemini para responder consultas específicas.
    """
    try:
        prompt = f"""
        Com base nos seguintes dados da partida:
        {data}
        
        Por favor, responda à seguinte pergunta:
        {query}
        """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        raise Exception(f"Erro ao processar dados com Gemini: {str(e)}")
