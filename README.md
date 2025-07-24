# 🚆 CP TrainTracking ChatBot
[![smithery badge](https://smithery.ai/server/@leo04per/cp-train-tracking)](https://smithery.ai/server/@leo04per/cp-train-tracking)

Este projeto é um **servidor MCP (Middleware de Comunicação Preditiva)** que funciona como *wrapper* para APIs públicas da **CP - Comboios de Portugal** e das **Infraestruturas de Portugal**.

## 🎯 Objetivo

O principal objetivo deste serviço é permitir o **acesso simplificado, via linguagem natural**, a **dados em tempo real** sobre o estado da rede ferroviária nacional, nomeadamente:

- Horários de comboios
- Localizações em tempo real
- Atrasos e interrupções na circulação

Este wrapper expõe uma API simplificada, mais acessível e útil para o utilizador final, podendo ser integrada facilmente em aplicações compatíveis com o protocolo MCP.

## 🧪 Funcionalidades

- Integração com APIs públicas da CP e Infraestruturas de Portugal
- Conversão de linguagem natural em queries estruturadas
- Respostas informativas e contextuais para utilizadores finais
- Compatibilidade com clientes MCP

## 🧑‍💻 Autores

Este projeto foi desenvolvido por:

- **Leonardo Pereira** [@leo04per](https://github.com/leo04per)
- **Daniel Silva** [@Danielramos07](https://github.com/Danielramos07)

## Requisitos

- Python 3.10+
- uv

## Instalação

### Installing via Smithery

To install cp_traintracking_chatbot for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@leo04per/cp_traintracking_chatbot):

```bash
npx -y @smithery/cli install @leo04per/cp_traintracking_chatbot --client claude
```

### Manual Installation
1. Clone o repositório:
```bash
git clone [URL_DO_REPOSITÓRIO]
cd CP_TrainTracking_ChatBot
cd cp_traintracking
```

2. Instale uv para gerir os pacotes python

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

3. Crie um ambiente virtual e instale as dependências usando uv:
```bash
uv venv
uv add mcp[cli] httpx
```

## Uso

1. Ative o ambiente virtual:
```bash
# No Windows
.venv\Scripts\activate

# No Linux/Mac
source .venv/bin/activate
```

2. Execute o servidor:
```bash
uv run .\cp_traintracking.py
```
## Uso no Claude Desktop
1. Instalação Claude Desktop https://claude.ai/download

2. ```Arquivo/Configurações/Desenvolvedor``` e clicar em ```Editar Configurações```

3. Inserir as configurações do servidor MCP no ```claude_desktop_config.json```
```json
{
    "mcpServers": {
        "cp-traintracking": {
            "command": "uv",
            "args": [
                "--directory",
                "/ABSOLUTE/PATH/TO/PARENT/FOLDER/",
                "run",
                "cp_traintracking.py"
            ]
        }
    }
}
```

4. Reniciar o Claude Desktop 

## Estrutura do Projeto

```
├── cp_traintracking/
│   └── cp_traintracking.py
└── README.md
```

