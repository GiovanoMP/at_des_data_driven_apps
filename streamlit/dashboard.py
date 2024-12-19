import streamlit as st
import requests
import plotly.graph_objects as go
from typing import Dict, List
import os
from dotenv import load_dotenv
from openai import OpenAI
import json

# Configuração
load_dotenv()
st.set_page_config(
    page_title="⚽ Análise de Futebol",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# APIs e Configurações
API_BASE_URL = "http://localhost:8000/api/v1"
MATCH_ID = 3788741  # Turquia vs Itália
PLAYER_ID = 11086.0  # Burak Yilmaz

# Cliente OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Estado do chat
if 'messages' not in st.session_state:
    st.session_state.messages = []

def get_match_data() -> Dict:
    """Função genérica para chamadas à API"""
    try:
        response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro na API: {str(e)}")
        return {}

def get_match_summary() -> Dict:
    """Obtém resumo da partida via API"""
    try:
        response = requests.get(f"{API_BASE_URL}/matches/{MATCH_ID}/summary")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Erro ao obter resumo: {str(e)}")
        return {}

def get_player_profile(include_analysis: bool = True) -> Dict:
    """Obtém perfil do jogador via API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/matches/{MATCH_ID}/player/{PLAYER_ID}",
            params={"include_analysis": include_analysis}
        )
        response.raise_for_status()
        data = response.json()
        
        # Adiciona análise se solicitado
        if include_analysis:
            analysis_response = requests.get(
                f"{API_BASE_URL}/matches/{MATCH_ID}/player/{PLAYER_ID}/analysis"
            )
            if analysis_response.ok:
                data['analysis'] = analysis_response.json().get('analysis', '')
        
        return data
    except Exception as e:
        st.error(f"Erro ao obter perfil: {str(e)}")
        return {}

def get_match_analysis(style: str) -> str:
    """Obtém análise da partida via API"""
    try:
        response = requests.get(
            f"{API_BASE_URL}/matches/{MATCH_ID}/analysis",
            params={"style": style}
        )
        response.raise_for_status()
        data = response.json()
        return data.get('narrative', '')  # Agora usando o campo correto
    except Exception as e:
        st.error(f"Erro ao obter análise: {str(e)}")
        return ""

def generate_llm_summary(match_data: Dict) -> str:
    """Gera um resumo personalizado usando GPT-4"""
    try:
        events_text = "\n".join([
            f"{event['minute']}' - {event['type']} - {event['player']} ({event['team']})"
            for event in match_data['events']
        ])
        
        prompt = f"""
        Você é um especialista em análise de futebol. Analise esta partida:
        
        {match_data['home_team']} vs {match_data['away_team']}
        Placar: {match_data['score']}
        Data: {match_data['date']}
        Estádio: {match_data['stadium']}
        
        Eventos:
        {events_text}
        
        Forneça:
        1. Análise tática
        2. Momentos-chave
        3. Destaques individuais
        4. Conclusão
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um analista de futebol profissional."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Erro ao gerar resumo com LLM: {str(e)}")
        return "Não foi possível gerar o resumo."

def create_timeline(events: List[Dict]) -> go.Figure:
    """Cria timeline de eventos com visual melhorado"""
    fig = go.Figure()
    
    # Cores e símbolos por tipo de evento
    event_styles = {
        "Goal": {"color": "green", "symbol": "star", "size": 25},
        "Card": {"color": "yellow", "symbol": "square", "size": 20}
    }
    
    # Adiciona eventos
    for event in events:
        style = event_styles.get(event['type'], {"color": "gray", "symbol": "circle", "size": 15})
        
        # Texto do evento
        event_text = []
        event_text.append(f"{event['minute']}'")
        event_text.append(event['player'])
        if event.get('assist'):
            event_text.append(f"(Assist: {event['assist']})")
        if event.get('description'):
            event_text.append(f"- {event['description']}")
        
        fig.add_trace(go.Scatter(
            x=[event['minute']],
            y=[event['team']],
            mode='markers+text',
            name=event['type'],
            text=[" ".join(event_text)],
            textposition="top center",
            marker=dict(
                size=style['size'],
                symbol=style['symbol'],
                color=style['color'],
                line=dict(color='black', width=1)
            )
        ))
    
    # Layout melhorado
    fig.update_layout(
        title={
            'text': "Timeline da Partida",
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title="Minuto do Jogo",
        yaxis_title="Time",
        showlegend=True,
        height=400,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12),
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            range=[-5, 95]
        ),
        yaxis=dict(
            showgrid=False
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def show_event_details(events: List[Dict]):
    """Mostra detalhes dos eventos em um formato mais organizado"""
    st.markdown("### 📝 Detalhes dos Eventos")
    
    # Separar eventos por tipo
    goals = [e for e in events if e['type'] == 'Goal']
    cards = [e for e in events if e['type'] == 'Card']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚽ Gols")
        for goal in goals:
            details = []
            if goal.get('assist'):
                details.append(f"🎯 Assist: {goal['assist']}")
            if goal.get('description'):
                details.append(f"📝 {goal['description']}")
            
            st.markdown(f"""
            **{goal['minute']}'** - {goal['player']} ({goal['team']})  
            {' | '.join(details) if details else ''}
            """)
    
    with col2:
        st.markdown("#### 🟨 Cartões")
        for card in cards:
            st.markdown(f"""
            **{card['minute']}'** - {card['player']} ({card['team']})  
            {f"📝 {card['description']}" if card.get('description') else ''}
            """)

def show_player_stats(player: Dict):
    """Mostra estatísticas do jogador em um formato mais visual"""
    if not player or 'info' not in player or 'statistics' not in player:
        st.error("Dados do jogador não disponíveis")
        return
    
    info = player['info']
    stats = player['statistics']
    
    # Informações básicas
    st.markdown(f"""
    ## 👤 {info['player_name']}
    ### {info['team']} | #{info['number']} | {info['position']}
    """)
    
    # Estatísticas em cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🎯 Passes")
        st.metric(
            "Total de Passes",
            f"{stats['passes']['successful']}/{stats['passes']['total']}",
            f"{stats['passes']['accuracy']}% precisão"
        )
    
    with col2:
        st.markdown("### ⚽ Finalizações")
        st.metric(
            "No Gol/Total",
            f"{stats['shots']['on_target']}/{stats['shots']['total']}",
            f"{stats['shots']['goals']} gols"
        )
    
    with col3:
        st.markdown("### 🛡️ Desarmes")
        st.metric(
            "Bem Sucedidos",
            f"{stats['tackles']['successful']}/{stats['tackles']['total']}",
            f"{int(stats['tackles']['successful']/stats['tackles']['total']*100)}% sucesso"
        )

def chat_with_context(prompt: str, match_data: Dict) -> str:
    """Chat com contexto usando OpenAI"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Você é um especialista em análise de futebol."},
                {"role": "user", "content": f"Dados da partida:\n{json.dumps(match_data, indent=2)}\n\nPergunta: {prompt}"}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

def main():
    # Estilo CSS para tema escuro
    st.markdown("""
        <style>
        .main {
            padding: 2rem;
            background-color: #1a1a1a;
            color: #ffffff;
        }
        .stMetric {
            background-color: #2d2d2d;
            padding: 1rem;
            border-radius: 10px;
            border: 1px solid #404040;
            color: #ffffff;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 24px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 10px 20px;
            border-radius: 5px;
            background-color: #2d2d2d;
            color: #ffffff;
        }
        .custom-header {
            background-color: #2d2d2d;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            border: 1px solid #404040;
            text-align: center;
        }
        .custom-header h1 {
            color: #ffffff;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .custom-header h2 {
            color: #ffffff;
        }
        .custom-header p {
            color: #b3b3b3;
            font-size: 1.2em;
        }
        .event-card {
            background-color: #2d2d2d;
            padding: 15px;
            border-radius: 8px;
            border: 1px solid #404040;
            margin-bottom: 10px;
            color: #ffffff;
        }
        div[data-testid="stMetricValue"] {
            color: #ffffff !important;
        }
        div[data-testid="stMetricDelta"] {
            color: #b3b3b3 !important;
        }
        div[data-testid="stMetricLabel"] {
            color: #b3b3b3 !important;
        }
        .stMarkdown {
            color: #ffffff;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("⚽ Análise de Futebol")
    
    # Carrega dados da partida
    match_data = get_match_data()
    if not match_data:
        st.error("Não foi possível carregar os dados da partida")
        return
    
    # Cabeçalho da partida
    st.markdown(f"""
    <div class="custom-header">
        <h2>🇹🇷 {match_data['home_team']} vs {match_data['away_team']} 🇮🇹</h2>
        <h1>{match_data['score']}</h1>
        <p>{match_data['date']} | {match_data['stadium']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Tabs principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Timeline do Jogo",
        "📝 Resumo da Partida",
        "👤 Análise do Jogador",
        "🎯 Narrativas Personalizadas"
    ])
    
    # Tab 1: Timeline e Eventos
    with tab1:
        # Configurando o tema escuro para o gráfico
        fig = create_timeline(match_data['events'])
        fig.update_layout(
            plot_bgcolor='#1a1a1a',
            paper_bgcolor='#1a1a1a',
            font=dict(color='#ffffff'),
            xaxis=dict(gridcolor='#404040'),
            yaxis=dict(gridcolor='#404040')
        )
        st.plotly_chart(fig, use_container_width=True)
        show_event_details(match_data['events'])
    
    # Tab 2: Resumo (mantido como estava)
    with tab2:
        with st.spinner("Gerando resumo detalhado..."):
            summary = generate_llm_summary(match_data)
            if summary:
                st.markdown(summary)
    
    # Tab 3: Jogador
    with tab3:
        player = get_player_profile(include_analysis=True)
        show_player_stats(player)
        
        if player and 'analysis' in player:
            st.markdown("---")
            st.markdown("### 📊 Análise Detalhada do Jogador")
            st.markdown(player['analysis'])
    
    # Tab 4: Narrativas
    with tab4:
        st.markdown("### 📖 Narrativas Personalizadas")
        
        style = st.selectbox(
            "Selecione o estilo de narrativa",
            ["formal", "humoristico", "tecnico"],
            format_func=lambda x: {
                "formal": "🎯 Formal - Análise objetiva e profissional",
                "humoristico": "😄 Humorístico - Narrativa descontraída",
                "tecnico": "📊 Técnico - Foco em dados e estatísticas"
            }[x],
            key="narrative_style"
        )
        
        if st.button("Gerar Narrativa Personalizada", key="narrative_button"):
            with st.spinner("Gerando narrativa personalizada..."):
                narrative = get_match_analysis(style)
                if narrative:
                    st.markdown(f"""
                    <div class="event-card">
                        {narrative}
                    </div>
                    """, unsafe_allow_html=True)
    
    # Chat
    st.markdown("---")
    st.header("💬 Chat Interativo")
    
    # Histórico
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Input com label adequado
    if prompt := st.chat_input(
        "Digite sua pergunta sobre a partida...",
        key="chat_input"
    ):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)
        
        # Resposta
        response = chat_with_context(prompt, match_data)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.write(response)

if __name__ == "__main__":
    main()