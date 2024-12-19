import pandas as pd
import requests
from typing import Dict, Any
import openai
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

# Configura a OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

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

def process_match_data_with_openai(data: Dict[str, Any], query: str) -> str:
    """
    Processa os dados da partida usando a OpenAI para responder consultas específicas.
    """
    try:
        prompt = f"""
        Com base nos seguintes dados da partida:
        {data}
        
        Por favor, responda à seguinte pergunta:
        {query}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um analista de futebol especializado."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Erro ao processar dados com OpenAI: {str(e)}")
