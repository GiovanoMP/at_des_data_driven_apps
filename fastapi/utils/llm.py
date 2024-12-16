from typing import Dict, List
import os
import google.generativeai as genai
from langchain.prompts import PromptTemplate
from langchain.agents import AgentExecutor, Tool, ConversationalAgent
from langchain.memory import ConversationBufferMemory
from langchain.memory.chat_message_histories import StreamlitChatMessageHistory
from dotenv import load_dotenv

# Carrega as variáveis de ambiente
load_dotenv()

# Configura o Gemini
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def generate_match_summary(match_data: Dict) -> str:
    """
    Gera um resumo da partida usando Gemini.
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
        
        # Gera o resumo usando Gemini
        response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        raise Exception(f"Erro ao gerar resumo: {str(e)}")

def generate_narrative(match_data: Dict, style: str = "formal") -> str:
    """
    Gera uma narrativa da partida no estilo especificado usando Gemini.
    """
    try:
        # Template para narrativa baseado no estilo
        style_prompts = {
            "formal": "Crie uma narrativa formal e profissional da partida",
            "humoristico": "Crie uma narrativa bem-humorada e descontraída da partida",
            "tecnico": "Crie uma análise técnica detalhada da partida"
        }
        
        narrative_template = f"""
        {style_prompts.get(style, style_prompts['formal'])} com os seguintes dados:
        {match_data}
        
        A narrativa deve:
        1. Manter consistência com o estilo {style}
        2. Destacar momentos importantes
        3. Mencionar jogadores relevantes
        """
        
        # Gera a narrativa usando Gemini
        response = model.generate_content(narrative_template)
        
        return response.text
    except Exception as e:
        raise Exception(f"Erro ao gerar narrativa: {str(e)}")

def setup_chat_model():
    """
    Configura e retorna uma instância do modelo de chat Gemini.
    """
    try:
        chat = model.start_chat(history=[])
        return chat
    except Exception as e:
        raise Exception(f"Erro ao configurar modelo de chat: {str(e)}")
