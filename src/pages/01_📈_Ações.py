"""
Script that contain the 'Ações' Page of the streamlit app.
"""

# ------------------------------------------------------------------------------------------------ #
# IMPORTS
import streamlit as st
import pandas as pd

# ------------------------------------------------------------------------------------------------ #
# RELATIVE IMPORTS

# UTILS
from utils import get_src_folder

# DATA
from data.load_data import AssetsDataLoader, LogsDataLoader

# COMPONENTS
from components.components import set_page_config, reorder_dataframe_columns
from components.components import set_page_main_menu
from components.components import \
    (
        get_valid_aggregate_options,
        aggregate_by_time,
        filter_data_by_time
    )

# VIZ
from components.viz import DataVisualizer
from components.viz import show_stacked_bar_chart

# ------------------------------------------------------------------------------------------------ #
# DEFINE CONSTANTS
logs_folder = get_src_folder()

# ------------------------------------------------------------------------------------------------ #
# SUB PAGES FUNCTIONS

# 1. HOME PAGE
def display_data(assets_loader, viz):
    """Displays stocks data in an expander."""
    df = assets_loader.load_asset_stocks_data()
    df = df[:-1]
    df.loc[:, ['% Ideal', '% Atual']] *= 100

    st.dataframe(df, hide_index=True)

    col1, col2 = st.columns(2)

    with col1:
        fig = viz.r4ven_pie_plot(df, 'Total (R$)', 'Ativo', 'Ações')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = viz.r4ven_pie_plot(df, 'Total (R$)', 'Setor', 'Setores')
        st.plotly_chart(fig, use_container_width=True)

# 2. RESULTS PAGE
def display_portfolio_result(assets_loader):
    """Displays portfolio result based on active and liquidated stocks."""
    st.header('Resultado da Carteira', divider='gray')
    df_result = assets_loader.load_asset_result_data()
    df_result = df_result[df_result['Tipo Ativo'] == 'Ação'].drop(columns={'Tipo Ativo'})
    df_result.loc[:, ['Ganho (%)', 'Ganho Ex (%)']] *= 100
    priority_columns = ['Ativo', 'Quantidade', 'Ganho (%)', 'Ganho Ex (%)']
    df_result = reorder_dataframe_columns(df_result, priority_columns)

    df_active = df_result[df_result['Status'] == 'Ativo na Carteira'].drop(columns='Status')
    df_liquidated = df_result[df_result['Status'] == 'Ativo Liquidado'].drop(columns='Status')

    st.dataframe(df_active, hide_index=True)
    with st.expander('🔥 Ver Ações Liquidadas'):
        st.dataframe(df_liquidated, hide_index=True)

# 3. DIVIDENDS PAGE
def display_dividends(assets_loader, log_loader):
    """Displays dividend information."""
    st.header('Dividendos da Carteira', divider='gray')
    df_dividends = assets_loader.load_asset_dividends_data()
    df_dividends = df_dividends[['Mês', 'Dia Final', 'Total - Ações (R$)', 'Acumulado - Ações (R$)',
                                 'Total Investido - Ações (R$)', 'DY - Ações (%)']][:-1]
    df_dividends.loc[:, ['DY - Ações (%)']] *= 100

    # Load passive income data
    df = log_loader.load_passive_income_data()
    df.drop(columns={"Mês/Ano"}, inplace=True)

    # Filter stocks data
    df = df[df['Tipo Ativo'] == 'Ação']

    # Get valid options for aggregation based on the date column
    valid_options = get_valid_aggregate_options(df=df, date_column='Data')

    # The selected time period from the dropdown menu.
    filter_by = filter_data_by_time(valid_options)

    df_agg = aggregate_by_time(df, 'Data', 'Valor Líquido (R$)', filter_by, {'sum'}, ['Tipo Provento', 'Ativo'])
    df_agg.rename(columns={'sum - Valor Líquido (R$)': 'Valor Líquido (R$)'}, inplace=True)

    show_stacked_bar_chart(df_agg,
                           'Período',
                            'Tipo Provento',
                            'Valor Líquido (R$)',
                            f"Tipo Provento x {filter_by}")

    st.markdown('***')

    with st.expander("💰 Ver Dividendos Consolidados"):
        st.dataframe(df_dividends, hide_index=True)

    with st.expander(f"💰 Ver Dividendos Agregados por {filter_by}"):
        st.dataframe(df_agg, hide_index=True)

# 4. VALUATION PAGE

# 5. PROTECTION PAGE

# ------------------------------------------------------------------------------------------------ #
# MAIN PAGE FUNCTION

def assets_stocks_page():
    """Main Streamlit page function."""
    page_config = set_page_config(page_title='Ações')
    st.set_page_config(**page_config)
    st.title('Carteira de Ações')
    st.markdown("***")

    assets_loader = AssetsDataLoader(logs_folder)
    logs_loader = LogsDataLoader(logs_folder)
    viz = DataVisualizer(logs_folder)


    selection_dict = {'Ações': 'wallet',
                      'Resultado': 'bank',
                      "Proventos": 'piggy-bank'}

    selection, options = set_page_main_menu(selection_dict)

    if selection == options[0]:
        display_data(assets_loader, viz)
    elif selection == options[1]:
        display_portfolio_result(assets_loader)
    elif selection == options[2]:
        display_dividends(assets_loader, logs_loader)

if __name__ == "__main__":
    assets_stocks_page()