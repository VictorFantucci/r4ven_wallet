# 📊 R4VEN WALLET

Este é um aplicativo desenvolvido em **Streamlit** para monitoramento e análise de uma carteira de investimentos em **FIIs e Ações**.
O app consome dados de uma planilha Google Sheets via **API do Google** e **gspreads**, fornecendo um painel completo para acompanhamento de ativos.

## 🚀 Funcionalidades

- **📌 Home Page** - Visão geral da carteira de investimentos.
- **📈 Ações** - Informações detalhadas sobre a carteira de ações, incluindo resultados e proventos.
- **🏢 FIIs** - Análise da carteira de FIIs, com dados de rendimento e desempenho
- **📜 Lançamentos** - Histórico completo de ordens de compra e venda.
- **💰 Proventos** - Histórico consolidado dos proventos recebidos.
- **🔮 Simulações** - Permite simular cenários de investimentos, calculando o tempo necessário para atingir uma meta de investimento, considerando contribuições mensais, taxa de retorno e inflação.

## 🛠️ Tecnologias Utilizadas

- [Streamlit](https://streamlit.io/) - Framework para criação de dashboards interativos.
- [Google Sheets API](https://developers.google.com/sheets/api) - Para consumo dos dados em tempo real.
- [gspread](https://github.com/burnash/gspread) - Biblioteca para interação com o Google Sheets.
- [Pandas](https://pandas.pydata.org/) - Manipulação e análise de dados.
- [python-dotenv](https://pypi.org/project/python-dotenv/) - Gerenciamento de variáveis de ambiente.
- [Plotly](https://plotly.com/) - Biblioteca para visualização interativa de dados.
- [r4ven_utils](https://github.com/seuusuario/r4ven_utils) - Biblioteca para logging do projeto.

## 📦 Como Instalar e Executar

1. Clone este repositório:
   ```bash
   git clone https://github.com/VictorFantucci/r4ven_wallet
   ```
2. Acesse o diretório do projeto:
   ```bash
   cd seu-repositorio
   ```
3. Crie um ambiente virtual e instale as dependências:
   ```bash
   python -m venv env
   source env/bin/activate  # No Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```
4. Configure as credenciais da API do Google Sheets:
   - Baixe o arquivo JSON das credenciais e salve na pasta `src` do projeto.
   - Crie um arquivo `.env` na pasta `src` do projeto e preencha conforme o arquivo `.env` disponível no GitHub:
   - O aplicativo carregará automaticamente as variáveis do `.env` usando `python-dotenv`.

5. Acesse o diretório `src` antes de executar o aplicativo:
   ```bash
   cd src
   ```
6. Execute o aplicativo:
   ```bash
   streamlit run R4VEN_WALLET.py
   ```

## 📌 Roadmap Futuro

- Implementação de **valuation** de ativos.
- Ferramentas de **proteção de carteira**.
- Melhorias na interface e experiência do usuário.

## 📄 Licença

Este projeto é distribuído sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

---

🔍 **Contribuições são bem-vindas!** Sinta-se à vontade para abrir issues ou pull requests para melhorias.

