from typing import Dict, List
import os
import openai
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configura a OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

def generate_match_summary(match_data: Dict) -> str:
    """
    Gera um resumo da partida usando OpenAI.
    """
    try:
        # Template para o resumo
        summary_template = """
        Gere um resumo da partida de futebol com os seguintes dados:
        {match_data}
        
        O resumo deve incluir:
        1. Resultado final
        2. Principais acontecimentos
        3. Destaques individuais
        
        Por favor, forneça um resumo conciso e informativo.
        """
        
        # Prepara o prompt
        prompt = summary_template.format(match_data=str(match_data))
        
        # Gera o resumo usando OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um analista esportivo especializado em futebol."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Erro ao gerar resumo: {str(e)}")

def generate_narrative(match_data: Dict, style: str = "formal") -> str:
    """
    Gera uma narrativa da partida no estilo especificado usando OpenAI.
    """
    try:
        # Template para narrativa baseado no estilo
        style_prompts = {
            "formal": """
            Atue como um narrador esportivo profissional e formal.
            Gere uma narrativa objetiva e detalhada da partida.
            """,
            "humoristico": """
            Atue como um narrador esportivo bem-humorado.
            Gere uma narrativa divertida e criativa da partida.
            """,
            "tecnico": """
            Atue como um analista técnico de futebol.
            Gere uma análise tática detalhada da partida.
            """
        }
        
        # Prepara o prompt
        prompt = f"""
        {style_prompts.get(style, style_prompts['formal'])}
        
        Dados da partida:
        {str(match_data)}
        """
        
        # Gera a narrativa usando OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Você é um narrador esportivo especializado em futebol."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Erro ao gerar narrativa: {str(e)}")

def setup_chat_model():
    """
    Configura e retorna uma instância do modelo de chat OpenAI.
    """
    try:
        return {
            "model": "gpt-3.5-turbo",
            "api_key": os.getenv('OPENAI_API_KEY')
        }
    except Exception as e:
        raise Exception(f"Erro ao configurar modelo de chat: {str(e)}")
