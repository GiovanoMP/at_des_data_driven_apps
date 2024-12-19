# Análise de Partidas de Futebol

## Requisitos do AT e Status de Implementação

### 1. Configuração do Ambiente 
- Python 3.8+ configurado
- Requirements.txt criado
- Ambiente virtual configurado

### 2. Organização do Projeto 
- Estrutura de pastas organizada
- README.md completo
- Commits claros e descritivos

### 3. Sumarização de Partidas 
- Identificação de eventos principais
- Integração com GPT-4
- Saída clara e amigável

### 4. Perfil de Jogador 
- Nome, estatísticas e métricas
- Visualização em cards
- Dados organizados

### 5. API com FastAPI 
- Endpoints implementados:
  - `/matches/{match_id}`: Dados da partida
  - `/matches/{match_id}/summary`: Resumo da partida
  - `/matches/{match_id}/player/{player_id}`: Perfil do jogador
  - `/matches/{match_id}/analysis`: Narrativas personalizadas
- Validação com Pydantic
- Documentação automática

### 6. Narração Personalizada 
- Três estilos implementados:
  - Formal: Análise objetiva e profissional
  - Humorístico: Tom descontraído
  - Técnico: Foco em estatísticas
- Integração com GPT-4
- Interface de seleção

### 7. Interface Streamlit 
- Dashboard interativo com 4 seções:
  - Timeline do Jogo: Visualização cronológica dos eventos
  - Resumo da Partida: Análise detalhada gerada por IA
  - Análise do Jogador: Estatísticas e métricas
  - Narrativas Personalizadas: Diferentes estilos de análise
- Tema escuro para melhor legibilidade
- Chat interativo com contexto da partida

### 8. LangChain 
- Não implementado devido a conflitos de dependências
- Após inúmeras tentativas de instalações e configurações
- Substituído por integração direta com OpenAI GPT-4

### 9. Interface Avançada 
- Timeline interativa com eventos da partida
- Estatísticas visuais em cards
- Tema escuro para melhor experiência

### 10. Integração Completa 
- Fluxo funcional entre API e Dashboard
- API e Streamlit independentes
- Todas funcionalidades principais cobertas

### 11. Entrega 
- Código no GitHub
- Documentação atualizada
- Requirements.txt completo

## Estrutura do Projeto

```
.
├── api/
│   ├── routes/
│   │   └── match_routes.py
│   └── services/
│       └── match_analysis.py
├── streamlit/
│   ├── dashboard.py
│   └── utils/
│       ├── data_loader.py
│       └── visualization.py
└── requirements.txt
```

## Funcionalidades Implementadas

### Dashboard Principal
1. **Timeline Interativa**
   - Visualização cronológica de eventos
   - Cores e ícones distintos para cada tipo de evento
   - Interatividade com hover e clique

2. **Resumo da Partida**
   - Análise detalhada gerada por IA
   - Identificação de momentos-chave
   - Contexto tático e técnico

3. **Perfil do Jogador**
   - Cards com estatísticas
   - Métricas de performance
   - Visualização clara e organizada

4. **Narrativas Personalizadas**
   - Três estilos de narrativa
   - Integração com GPT-4
   - Interface de seleção intuitiva

5. **Chat Interativo**
   - Perguntas sobre a partida
   - Contexto completo dos eventos
   - Respostas personalizadas

## Observações Importantes

1. **Sobre o LangChain**
   - Múltiplas tentativas de implementação realizadas
   - Conflitos entre dependências impossibilitaram o uso
   - Solução: Integração direta com GPT-4 como Agente/LLM

2. **Dados Simulados**
   - Estrutura preparada para dados reais
   - Demonstração completa de funcionalidades
   - Fácil integração futura com APIs reais

## Como Executar

1. **Configuração do Ambiente**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

2. **Variáveis de Ambiente**
Crie um arquivo `.env` com:
```
OPENAI_API_KEY=sua_chave_aqui
```

3. **Executando a API**
```bash
uvicorn api.main:app --reload
```

4. **Executando o Dashboard**
```bash
streamlit run streamlit/dashboard.py
```

## Tecnologias Utilizadas

- **Backend**: FastAPI
- **Frontend**: Streamlit
- **IA**: OpenAI GPT-4
- **Visualização**: Plotly
- **Dados**: JSON simulado

## Próximos Passos

1. Integração com APIs reais de dados de futebol
2. Implementação de comparação entre jogadores
3. Mais opções de visualização
4. Expansão das capacidades do chat

## Licença

MIT License