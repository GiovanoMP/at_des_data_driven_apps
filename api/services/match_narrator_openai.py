from typing import Dict, List, Any, Optional
import logging
import openai
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class MatchNarratorOpenAI:
    def __init__(self):
        # Carregar variáveis de ambiente
        load_dotenv()
        
        # Configurar a OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY")

        # Templates para diferentes estilos de narração
        self.templates = {
            'formal': """
            Atue como um narrador esportivo profissional e formal. 
            Crie uma narração detalhada e objetiva da partida com base no seguinte resumo:
            {match_summary}
            
            Mantenha um tom profissional e foque nos aspectos técnicos e táticos do jogo.
            """,
            'humorous': """
            Atue como um narrador esportivo bem-humorado e descontraído.
            Crie uma narração divertida e criativa da partida com base no seguinte resumo:
            {match_summary}
            
            Use metáforas engraçadas, trocadilhos e mantenha um tom leve e divertido.
            """,
            'technical': """
            Atue como um analista técnico de futebol.
            Faça uma análise profunda e técnica da partida com base no seguinte resumo:
            {match_summary}
            
            Foque em aspectos táticos, formações, estatísticas e decisões técnicas importantes.
            """
        }

    def _format_match_summary(self, match_data: Dict[str, Any]) -> str:
        """
        Formata o resumo da partida em um texto estruturado para o LLM.
        """
        match_info = match_data['match_info']
        key_events = match_data['key_events']
        
        summary = f"""
        Partida: {match_info['home_team']} vs {match_info['away_team']}
        Placar: {match_info['score']}
        Data: {match_info['date']}
        Local: {match_info['stadium']}
        
        Gols:
        """
        
        for goal in key_events['goals']:
            assist = f" (Assistência: {goal['assist']})" if goal['assist'] else ""
            summary += f"\n- {goal['minute']}': {goal['scorer']} ({goal['team']}){assist}"
        
        summary += "\n\nCartões:"
        for card in key_events['cards']:
            summary += f"\n- {card['minute']}': {card['player']} ({card['team']}) - {card['card_type']}"
        
        summary += "\n\nSubstituições:"
        for sub in key_events['substitutions']:
            summary += f"\n- {sub['minute']}': {sub['team']} - Saiu: {sub['player_out']}, Entrou: {sub['player_in']}"
        
        return summary

    def generate_narrative(self, match_data: Dict[str, Any], style: str = 'formal') -> str:
        """
        Gera uma narrativa da partida no estilo especificado usando a OpenAI.
        """
        try:
            if style not in self.templates:
                style = 'formal'
                
            formatted_summary = self._format_match_summary(match_data)
            prompt = self.templates[style].format(match_summary=formatted_summary)
            
            # Gerar resposta usando a OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um narrador esportivo especializado em futebol."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Erro ao gerar narrativa: {str(e)}")
            return "Não foi possível gerar a narrativa da partida."

    def generate_player_analysis(self, player_data: Dict[str, Any]) -> str:
        """
        Gera uma análise detalhada do desempenho de um jogador usando a OpenAI.
        """
        try:
            stats = player_data['statistics']
            info = player_data['info']
            
            prompt = f"""
            Atue como um analista técnico especializado em análise individual de jogadores.
            Faça uma análise detalhada do desempenho do jogador {info['player_name']} ({info['team']}) 
            com base nas seguintes estatísticas:
            
            - Passes: {stats['passes']['total']} (Completos: {stats['passes']['successful']})
            - Finalizações: {stats['shots']['total']} (Gols: {stats['shots']['goals']})
            - Desarmes: {stats['tackles']}
            - Interceptações: {stats['interceptions']}
            - Minutos jogados: {stats['minutes_played']}
            
            Considere:
            1. Eficiência nos passes e finalizações
            2. Contribuição defensiva
            3. Pontos fortes e áreas para melhoria
            4. Impacto geral na partida
            """
            
            # Gerar resposta usando a OpenAI
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um analista técnico de futebol especializado em análise individual."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Erro ao gerar análise do jogador: {str(e)}")
            return "Não foi possível gerar a análise do jogador."
