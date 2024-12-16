# Project Charter - Análise de Partidas de Futebol

## Visão Geral do Projeto
Desenvolvimento de uma aplicação dual para análise de partidas de futebol, consistindo em:
1. API REST (FastAPI + LLM)
2. Interface Web (Streamlit + LangChain)

## Objetivos
- Criar uma API robusta para análise de dados de futebol
- Desenvolver uma interface web intuitiva para consumo dos dados
- Implementar funcionalidades de análise avançada usando LLM e LangChain

## Escopo do Projeto

### Incluído no Escopo
1. Sistema API (FastAPI):
   - Endpoint para sumarização de partidas
   - Endpoint para perfil de jogadores
   - Integração com StatsBombPy
   - Geração de narrativas personalizadas

2. Interface Web (Streamlit):
   - Dashboard interativo
   - Integração com ReAct Agent
   - Visualizações gráficas
   - Sistema de consultas em linguagem natural

### Funcionalidades Principais
- Perfil detalhado de jogadores
- Sumarização de eventos de partidas
- Narração personalizada (formal, humorística, técnica)
- Análise comparativa entre jogadores
- Consultas interativas via agente ReAct

### Fora do Escopo
- Análise de campeonatos completos
- Previsões de resultados futuros
- Análise de dados em tempo real
- Integração com outras APIs de futebol

## Estrutura do Projeto
```
/
├── streamlit/           # Aplicação Streamlit
│   ├── requirements.txt # Dependências específicas Streamlit
│   └── ...
├── fastapi/            # Aplicação FastAPI
│   └── ...
├── requirements.txt    # Dependências globais
├── README.md
└── documents/         # Documentação
```

## Tecnologias Principais
- Python 3.8+
- FastAPI
- Streamlit
- LangChain
- StatsBombPy
- LLM (a definir modelo específico)

## Entregas
1. API REST funcional
2. Interface Streamlit interativa
3. Documentação completa
4. Código fonte no GitHub
5. Arquivos requirements.txt

## Critérios de Sucesso
- Todas as funcionalidades principais implementadas e funcionando
- Código bem documentado e organizado
- Interface intuitiva e responsiva
- API com endpoints funcionais e documentados
- Integração bem-sucedida entre todos os componentes
