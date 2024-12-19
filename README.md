# Football Match Analysis API

Uma API avançada para análise de partidas de futebol utilizando dados do StatsBomb, integrada com IA generativa para análises narrativas personalizadas.

## Recursos

### 1. Dados Brutos da Partida
**Endpoint:** `/matches/{match_id}`
- Retorna dados detalhados de uma partida específica
- Inclui todos os eventos registrados (média de ~3800 eventos por partida)
- Formato JSON estruturado

### 2. Perfil do Jogador
**Endpoint:** `/matches/{match_id}/player/{player_id}`
- Análise detalhada do desempenho individual
- Estatísticas chave:
  - Passes (total e bem-sucedidos)
  - Finalizações (total e gols)
- Análise narrativa gerada por IA sobre o desempenho do jogador

### 3. Sumário da Partida
**Endpoint:** `/matches/{match_id}/summary`
- Visão geral rápida dos principais eventos
- Inclui:
  - Total de gols marcados
  - Cartões mostrados
  - Eventos-chave da partida

### 4. Análise Narrativa
**Endpoint:** `/matches/{match_id}/analysis?style={style}`

Gera análises narrativas personalizadas com três estilos diferentes:
- **Formal**: Análise profissional e detalhada (~2200 caracteres)
- **Humorístico**: Abordagem leve e divertida (~1400 caracteres)
- **Técnico**: Foco em aspectos táticos e estatísticos (~1600 caracteres)

## Tecnologias Utilizadas

- **FastAPI**: Framework web de alta performance
- **StatsBombPy**: Acesso aos dados oficiais do StatsBomb
- **OpenAI GPT**: Geração de análises narrativas com IA
- **Pandas**: Processamento e análise de dados
- **Python 3.8+**: Linguagem base do projeto

## Instalação

1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
```

2. Instale as dependências:
```bash
pip install -e .
```

3. Configure as variáveis de ambiente:
Crie um arquivo `.env` com:
```env
OPENAI_API_KEY=sua_chave_api_aqui
```

## Executando a API

```bash
uvicorn api.main:app --reload
```

## Testes

Execute os testes de integração:
```bash
python tests/test_api_integration.py
```

Os testes cobrem todos os endpoints principais e verificam:
- Integridade dos dados retornados
- Funcionamento da integração com IA
- Diferentes estilos de narrativa
- Precisão das estatísticas

## Documentação Adicional

Após iniciar o servidor, acesse:
- Documentação Swagger UI: `http://localhost:8000/docs`
- Documentação ReDoc: `http://localhost:8000/redoc`

## Contribuindo

1. Fork o projeto
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---
Desenvolvido por Giovano M Panatta - giovano.m.panatta@gmail.com