"""
Script that contains the streamlit application of my financial independence wallet.
"""

# ------------------------------------------------------------------------------------------------ #
# IMPORTS
import os
import sys
import streamlit as st
from PIL import Image

# ------------------------------------------------------------------------------------------------ #
# RELATIVE IMPORTS

# UTILS
from utils import get_src_folder

# DATA
from data.load_data import AssetsDataLoader, WalletDataLoader

# COMPONENTS
from components.components import set_page_config, check_login
from components.components import \
    (
        get_valid_aggregate_options,
        aggregate_by_time,
        filter_data_by_time
    )

# VIZ
from components.viz import show_line_chart, show_pie_plot

# ------------------------------------------------------------------------------------------------ #
# DEFINE CONSTANTS
app_directory =  os.path.dirname(os.path.dirname(__file__))
sys.path.append(app_directory)

logs_folder = get_src_folder()

# ------------------------------------------------------------------------------------------------ #
# WALLET  FUNCTIONS
def display_wallet_goal(wallet_loader):
    """Display wallet goal"""

    st.header("Metas", divider='grey')

    # Wallet Goal
    wallet_goal = wallet_loader.load_wallet_goal()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader('Meta Atual da Carteira')
        st.dataframe(wallet_goal, hide_index=True)
        st.markdown("""
                    _**Quem não sabe onde quer chegar, qualquer lugar serve, ATÉ LUGAR NENHUM**._

                    > Prof. Mira
                    """)
    with col2:
        st.subheader('Metas a bater:')
        investment_goals(wallet_goal.iloc[0, 1])

def investment_goals(current_value: float) -> None:
    """
    Displays a list of financial goals in two columns in Markdown format,
    striking through those already achieved.

    Args:
        current_value (float): The current investment value.
    """

    # List of financial goals
    goals = [
        (25000, 'R$ 25,000'),
        (50000, 'R$ 50,000'),
        (75000, 'R$ 75,000'),
        (100000, 'R$ 100,000'),
        (250000, 'R$ 250,000'),
        (500000, 'R$ 500,000'),
        (750000, 'R$ 750,000'),
        (1000000, 'R$ 1,000,000'),
        (2500000, 'R$ 2,500,000'),
        (5000000, 'R$ 5,000,000'),
        (7500000, 'R$ 7,500,000'),
        (10000000, 'R$ 10,000,000')
    ]

    # Split goals into two halves for the columns
    mid_index = len(goals) // 2
    goals_col1 = goals[:mid_index]
    goals_col2 = goals[mid_index:]

    # Create two columns in Streamlit
    col1, col2 = st.columns(2)

    # Generate Markdown text for each column
    with col1:
        st.markdown("\n".join(
            f"- {'~~' + text + '~~' if current_value >= amount else text}"
            for amount, text in goals_col1
        ))

    with col2:
        st.markdown("\n".join(
            f"- {'~~' + text + '~~' if current_value >= amount else text}"
            for amount, text in goals_col2
        ))

# ------------------------------------------------------------------------------------------------ #
# WALLET DIVISION FUNCTIONS
def display_wallet_division(wallet_loader):
    """Display wallet division and strategy"""

    st.header("Alocação da Carteira", divider='gray')

    # Wallet Division
    wallet_division = wallet_loader.load_wallet_division()
    wallet_division.loc[:, ['% Ideal', '% Atual']] *= 100

    st.dataframe(wallet_division, hide_index=True)

# ------------------------------------------------------------------------------------------------ #
# WALLET OVERVIEW FUNCTIONS
def display_walllet_overview(wallet_loader, assets_loader):
    """Display Wallet Overview and Results"""

    st.header('Resultado da Carteira', divider='grey')

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    # Wallet Overview
    wallet_overview = wallet_loader.load_wallet_overview()
    wallet_overview.loc[:, ['Variação (%)']] *= 100

    with col1:
        st.metric('Gasto',
                  value=f"R${wallet_overview['Gasto (R$)'].iloc[0]:,.2f}")

    with col2:
        st.metric('Total Investido',
                  value=f"R${wallet_overview['Investido (R$)'].iloc[0]:,.2f}",
                  delta=f"{wallet_overview['Variação (%)'].iloc[0]:,.2f}%")

    with col3:
        st.metric('Ganho Total',
                  value=f"R${wallet_overview['Ganho Total (R$)'].iloc[0]:,.2f}")

    with col4:
        st.metric('Proventos',
                  value=f"R${wallet_overview['Proventos (R$)'].iloc[0]:,.2f}")

    with col5:
        st.metric('Vendido',
                  value=f"R${wallet_overview['Vendido (R$)'].iloc[0]:,.2f}")

    with col6:
        st.metric('Lucro Vendas',
                  value=f"R${wallet_overview['Lucro Vendas (R$)'].iloc[0]:,.2f}")

    display_dividends(assets_loader)

def display_dividends(assets_loader):
    """Displays dividend information."""

    df = assets_loader.load_asset_dividends_data()
    df = df[['Mês', 'Dia Final', 'Total (R$)', 'Acumulado (R$)',
                                 'Total Investido (R$)', 'DY - Carteira (%)']][:-1]
    df.loc[:, ['DY - Carteira (%)']] *= 100

    # Get valid options for aggregation based on the date column
    valid_options = get_valid_aggregate_options(df=df, date_column='Dia Final')

    # The selected time period from the dropdown menu.
    filter_by = filter_data_by_time(valid_options)

    df_agg = aggregate_by_time(df, 'Dia Final', 'DY - Carteira (%)', filter_by, {'sum'})
    df_agg.rename(columns={'sum - DY - Carteira (%)': 'DY - Carteira (%)'}, inplace=True)

    show_line_chart(df_agg,
                    'Período',
                    'DY - Carteira (%)',
                    'DY - Carteira (%)',
                    '%Y-%m'
                    )

# ------------------------------------------------------------------------------------------------ #
# MAIN FUNCTION

def app() -> None:

    # Create configuration dict
    page_config = set_page_config(page_title='r4ven_wallet')
    # Set page configuration
    st.set_page_config(**page_config)

    # Check login before loading the page
    check_login()

    st.title('R4VEN - Independência Financeira')

    # Initialize the Data Loaders
    wallet_loader = WalletDataLoader(logs_folder)
    assets_loader = AssetsDataLoader(logs_folder)

    with st.expander('O que me motiva?'):
        st.markdown("""
                    #### O que não quero para a minha vida:

                    - Não quero trabalhar a vida inteira.
                    - Não quero o que meus pais aspiravam para mim, que é a segurança no emprego e uma casa em um bairro de classe média alta.
                    - Não quero ser empregado.

                    #### O que quero para a minha vida:

                    - Quero ser financeiramente independente para viajar pelo mundo e viver o estilo de vida que gosto.
                    - Quero fazer isso ainda jovem.
                    - Quero controlar meu tempo e minha vida.
                    - Quero que o dinheiro trabalhe para mim.
                    - **Quero ser simplesmente livre.**
                    """)

    # WALLET GOAL
    display_wallet_goal(wallet_loader)

    # WALLET DIVISION
    display_wallet_division(wallet_loader)

    # WALLET OVERVIEW
    display_walllet_overview(wallet_loader, assets_loader)

if __name__ == '__main__':
    app()
