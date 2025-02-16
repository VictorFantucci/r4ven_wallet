import os
import sys
import streamlit as st
from PIL import Image

# Load relative imports
from utils import get_src_folder
from data.load_data import WalletDataLoader
from components.components import set_page_config

app_directory =  os.path.dirname(os.path.dirname(__file__))
sys.path.append(app_directory)

import streamlit as st

def investment_goals(current_value: float) -> None:
    """
    Displays a list of financial goals in Markdown format, striking through those already achieved.

    Args:
        current_value (float): The current investment value.
    """

    # List of financial goals with their respective values formatted in Brazilian Real (R$)
    goals = [
        (50000, 'R$ 50,000'),
        (100000, 'R$ 100,000'),
        (500000, 'R$ 500,000'),
        (1000000, 'R$ 1,000,000'),
        (2500000, 'R$ 2,500,000'),
        (5000000, 'R$ 5,000,000'),
    ]

    # Creates a Markdown text where achieved goals are struck through using '~~'
    markdown_text = "\n".join(
        f"- {'~~' + text + '~~' if current_value >= amount else text}"
        for amount, text in goals
    )

    # Displays the formatted text in Streamlit
    st.markdown(markdown_text)

# Main function
def app() -> None:

    # Create configuration dict
    page_config = set_page_config(page_title='r4ven_wallet')
    # Set page configuration
    st.set_page_config(**page_config)

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
    with col2:
        st.subheader('Metas a bater:')
        investment_goals(wallet_goal.iloc[0, 1])

    # Wallet Overview
    st.subheader('Resultado da Carteira')
    wallet_overview = wallet_loader.load_wallet_overview()
    st.dataframe(wallet_overview, hide_index=True)

    # Wallet Division
    st.subheader("Alocação da Carteira")
    wallet_division = wallet_loader.load_wallet_division()
    st.dataframe(wallet_division, hide_index=True)

if __name__ == '__main__':
    app()
