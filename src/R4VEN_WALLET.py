"""
Script that contains the streamlit application of my financial independence wallet.
"""

# Load imports
import os
import sys
import streamlit as st
from PIL import Image

# Load relative imports
from utils import get_src_folder
from data.load_data import WalletDataLoader
from components.components import set_page_config, check_login

app_directory =  os.path.dirname(os.path.dirname(__file__))
sys.path.append(app_directory)

import streamlit as st

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

# Main function
def app() -> None:

    # Create configuration dict
    page_config = set_page_config(page_title='r4ven_wallet')
    # Set page configuration
    st.set_page_config(**page_config)

    # Check login before loading the page
    check_login()

    st.title('R4VEN - Independência Financeira')

    # Initialize the WalletDataLoader
    wallet_loader = WalletDataLoader(logs_folder=get_src_folder())

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

    st.header(" Visão Geral", divider='gray')

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

    with col1:
        # Wallet Overview
        st.subheader('Resultado da Carteira')
        wallet_overview = wallet_loader.load_wallet_overview()
        wallet_overview.loc[:, ['Variação (%)']] *= 100
        st.dataframe(wallet_overview, hide_index=True)

    with col1:
        # Wallet Division
        st.subheader("Alocação da Carteira")
        wallet_division = wallet_loader.load_wallet_division()
        wallet_division.loc[:, ['% Ideal', '% Atual']] *= 100
        st.dataframe(wallet_division, hide_index=True)

if __name__ == '__main__':
    app()
