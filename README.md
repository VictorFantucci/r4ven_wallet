# 📊 R4VEN WALLET

Este é um aplicativo desenvolvido em **Streamlit** para monitoramento e análise de uma carteira de investimentos em **FIIs e Ações**.
O app consome dados de uma planilha Google Sheets via **API do Google** e **gspreads**, fornecendo um painel completo para acompanhamento de ativos.

## 🚀 Funcionalidades

- **📌 Home Page** - Visão geral da carteira de investimentos.
- **📈 Ações** - Informações detalhadas sobre a carteira de ações, incluindo resultados e proventos. Futuramente: valuation e proteção de carteira.
- **🏢 FIIs** - Análise da carteira de FIIs, com dados de rendimento e desempenho. Futuramente: valuation e proteção de carteira.
- **📜 Lançamentos** - Histórico completo de ordens de compra e venda.
- **💰 Proventos** - Histórico consolidado dos proventos recebidos.

## 🛠️ Tecnologias Utilizadas

- [Streamlit](https://streamlit.io/) - Framework para criação de dashboards interativos.
- [Google Sheets API](https://developers.google.com/sheets/api) - Para consumo dos dados em tempo real.
- [gspread](https://github.com/burnash/gspread) - Biblioteca para interação com o Google Sheets.
- [Pandas](https://pandas.pydata.org/) - Manipulação e análise de dados.
- [python-dotenv](https://pypi.org/project/python-dotenv/) - Gerenciamento de variáveis de ambiente.

## 📦 Como Instalar e Executar

1. Clone este repositório:
   ```bash
   git clone https://github.com/seuusuario/seu-repositorio.git
   ```
2. Acesse o diretório do projeto:
   ```bash
   cd seu-repositorio
   ```
3. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Configure as credenciais da API do Google Sheets:
   - Baixe o arquivo JSON das credenciais e salve na raiz do projeto.
   - Crie um arquivo `.env` na raiz do projeto e adicione:
     ```ini
     GOOGLE_APPLICATION_CREDENTIALS=caminho/para/credenciais.json
     ```
   - O aplicativo carregará automaticamente as variáveis do `.env` usando `python-dotenv`.

5. Acesse o diretório `src` antes de executar o aplicativo:
   ```bash
   cd src
   ```
6. Execute o aplicativo:
   ```bash
   streamlit run app.py
   ```

## 📌 Roadmap Futuro

- Implementação de **valuation** de ativos.
- Ferramentas de **proteção de carteira**.
- Melhorias na interface e experiência do usuário.

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

🔍 **Contribuições são bem-vindas!** Sinta-se à vontade para abrir issues ou pull requests para melhorias.

