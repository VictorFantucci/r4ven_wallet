"""
Script that contain the 'Simulações' Page of the streamlit app.
"""

# ------------------------------------------------------------------------------------------------ #
# IMPORTS
import streamlit as st
from datetime import datetime

# ------------------------------------------------------------------------------------------------ #
# RELATIVE IMPORTS

# UTILS
from utils import get_src_folder

# CALCULATIONS
from calculations.calc import *

# COMPONENTS
from components.components import set_page_config, check_login
from components.components import \
    (
        get_valid_aggregate_options,
        aggregate_by_time,
        filter_data_by_time
    )

# VIZ
from components.viz import show_line_chart, show_bar_chart

# ------------------------------------------------------------------------------------------------ #
# DEFINE CONSTANTS
logs_folder = get_src_folder()

# ------------------------------------------------------------------------------------------------ #
# SIMULATIONS

def simulate_time_to_goal():
    st.title("Calculadora de Tempo para Meta de Investimento")

    # Input fields
    with st.expander("Configurações do Investimento", expanded=True):
        initial_investment = st.number_input("Investimento Inicial", min_value=0.0, value=10000.0, step=0.01)
        monthly_contribution = st.number_input("Contribuição Mensal", min_value=0.0, value=500.0, step=0.01)
        monthly_rate = st.number_input("Taxa de Retorno Mensal (%)", min_value=0.0, value=0.77, step=0.01) / 100
        annual_inflation = st.number_input("Inflação Anual (%)", min_value=0.0, value=4.5, step=0.1) / 100
        goal = st.number_input("Meta de Investimento", min_value=0.0, value=100000.0, step=1000.0)
        annual_contribution_adjustment = st.number_input("Ajuste Anual da Contribuição (%)", min_value=0.0, value=5.0, step=0.1) / 100

        # Get the current date
        current_date = datetime.today()

        # Create a date selector with the current date as the default value
        start_date = st.date_input("Data de Início", current_date)

        # Convert the selected date to a string in the format YYYY-MM
        start_date_str = start_date.strftime('%Y-%m')

    # Calculation
    result = calculate_time_to_goal(initial_investment,
                                    monthly_contribution,
                                    monthly_rate,
                                    annual_inflation,
                                    goal,
                                    annual_contribution_adjustment,
                                    start_date_str)

    df = result['dataframe']

    # Show summary of the result with all input data
    st.subheader("Resultado do Investimento", divider='grey')
    st.markdown(f"- **Investimento Inicial**: R${initial_investment:,.2f}")
    st.markdown(f"- **Contribuição Mensal**: R${monthly_contribution:,.2f}")
    st.markdown(f"- **Taxa de Retorno Mensal**: {monthly_rate * 100:.2f}%")
    st.markdown(f"- **Inflação Anual**: {annual_inflation * 100:.2f}%")
    st.markdown(f"- **Ajuste Anual da Contribuição**: {annual_contribution_adjustment * 100:.2f}%")
    st.markdown(f"- **Data de Início**: {start_date_str}")

    st.markdown("***")

    # Show the time it takes to reach the goal
    st.markdown(f"A meta será atingida, provavelmente, em **{result['expected_year_month']}**. "
                f"Serão necessários **{result['years']} anos e {result['months']} meses**.")
    st.markdown(f"Os **R\$ {goal:,.2f}** da meta desejada, "
                f"considerando uma inflação anual de **{annual_inflation * 100:.2f}%**, "
                f"equivale a **R\$ {result['adjusted_goal']:,.2f}** em **{result['expected_year_month']}**.")

    # Convert pd.Period to str
    df['Mês'] = df['Mês'].astype(str)

    # Convert all columns except 'Mês' to float
    df.loc[:, df.columns != 'Mês'] = df.loc[:, df.columns != 'Mês'].apply(pd.to_numeric, errors='coerce')

    # Keep the original data
    df_result = df.copy()

    st.subheader("Visualização do Resultado", divider='grey')

    # Get valid options for aggregation based on the date column
    valid_options = get_valid_aggregate_options(df=df, date_column='Mês')

    # The selected time period from the dropdown menu.
    filter_by = filter_data_by_time(valid_options)

    df_agg = aggregate_by_time(df,
                                'Mês',
                                ['Patrimônio (R$)', 'Proventos (R$)'],
                                filter_by,
                                {'max'})

    df_agg.rename(columns={'max - Patrimônio (R$)': 'Patrimônio (R$)',
                           'max - Proventos (R$)': 'Proventos (R$)'}, inplace=True)

    col1, col2 = st.columns(2)

    with col1:
        show_line_chart(df_agg,
                        'Período',
                        'Patrimônio (R$)',
                        'Evolução do Patrimonial',
                        '%Y-%m'
                        )
    with col2:
        show_bar_chart(df_agg,
                        'Período',
                        'Proventos (R$)',
                        'Proventos (R$)',
                        'Evolução dos Proventos(R$)',
                        '%Y-%m')

    # Section separator and header
    st.markdown('***')
    st.subheader('🗂️ Base de Dados')

    # Expandable section for displaying stock portfolio details
    with st.expander('Progresso do Investimento - Mensal'):
        st.dataframe(df_result, hide_index=True)

    if filter_by != 'Mês':
        with st.expander(f'Progresso do investimento - {filter_by}'):
            st.dataframe(df_agg, hide_index=True)

# ------------------------------------------------------------------------------------------------ #
# MAIN FUNCTION

def simulation_page() -> None:

    # Create configuration dict
    page_config = set_page_config(page_title='Simulações')
    # Set page configuration
    st.set_page_config(**page_config)

    # Check login before loading the page
    check_login()

    simulate_time_to_goal()

if __name__ == '__main__':
    simulation_page()
