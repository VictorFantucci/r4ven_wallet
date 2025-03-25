"""
Script that contain the 'FIIs' Page of the streamlit app.
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
from components.components import set_page_main_menu, check_login
from components.components import \
    (
        get_valid_aggregate_options,
        aggregate_by_time,
        filter_data_by_time
    )

# VIZ
from components.viz import DataVisualizer
from components.viz import show_bar_chart, show_line_chart

# ------------------------------------------------------------------------------------------------ #
# DEFINE CONSTANTS
logs_folder = get_src_folder()

# ------------------------------------------------------------------------------------------------ #
# SUB PAGES FUNCTIONS

# 1. HOME PAGE
def display_data(assets_loader, viz):
    """Displays real estate funds data in an expander."""
    df = assets_loader.load_asset_real_estate_data()
    df = df[:-1]
    df.loc[:, ['% Ideal', '% Atual']] *= 100

    col1, col2 = st.columns(2)

    with col1:
        fig = viz.r4ven_pie_plot(df, 'Total (R$)', 'Ativo', 'FIIs')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = viz.r4ven_pie_plot(df, 'Total (R$)', 'Segmento', 'Segmentos')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('***')
    st.subheader('🗂️ Base de Dados')
    with st.expander('Carteira de FIIs'):
        st.dataframe(df, hide_index=True)

# 2. RESULTS PAGE
def display_portfolio_result(assets_loader):
    """Displays portfolio result based on active and liquidated stocks."""
    st.header('Resultado da Carteira', divider='gray')
    df_result = assets_loader.load_asset_result_data()
    df_result = df_result[df_result['Tipo Ativo'] == 'FII'].drop(columns={'Tipo Ativo'})
    df_result.loc[:, ['Ganho (%)', 'Ganho Ex (%)']] *= 100
    priority_columns = ['Ativo', 'Quantidade', 'Ganho (%)', 'Ganho Ex (%)']
    df_result = reorder_dataframe_columns(df_result, priority_columns)

    df_active = df_result[df_result['Status'] == 'Ativo na Carteira'].drop(columns='Status')
    df_liquidated = df_result[df_result['Status'] == 'Ativo Liquidado'].drop(columns='Status')

    st.dataframe(df_active, hide_index=True)
    with st.expander('🔥 Ver FIIs Liquidados'):
        st.dataframe(df_liquidated, hide_index=True)

# 3. DIVIDENDS PAGE
def display_dividends(assets_loader, log_loader):
    """Displays dividend information."""
    st.header('Dividendos da Carteira', divider='gray')
    df_dividends = assets_loader.load_asset_dividends_data()
    df_dividends = df_dividends[['Mês', 'Dia Final', 'Total - FII (R$)', 'Acumulado - FII (R$)',
                                 'Total Investido - FII (R$)', 'DY - FII (%)']][:-1]
    df_dividends.loc[:, ['DY - FII (%)']] *= 100

    # Load passive income data
    df = log_loader.load_passive_income_data()
    df.drop(columns={"Mês/Ano"}, inplace=True)

    # Filter stocks data
    df = df[df['Tipo Ativo'] == 'FII']

    with st.expander('DY - FIIs (%)'):
        show_line_chart(df_dividends,
                        'Mês',
                        'DY - FII (%)',
                        'DY - FII (%)',
                        '%Y-%m'
                        )

    st.subheader('1 - Visão Anualizada')

    # Extract unique years for filter selection
    years = sorted(df["Mês"].astype(str).str[:4].unique(), reverse=True)

    # Sidebar Year Selection
    selected_year = st.selectbox("Selecione o Ano", years, index=0)

    # Filter DataFrame by Selected Year
    df_filtered = df[df["Mês"].str[:4] == selected_year]

    # Pivot Table
    pivot_df = df_filtered.pivot_table(
        index="Ativo",
        columns="Mês",
        values="Valor Líquido (R$)",
        aggfunc="sum",
        fill_value=0
    )

    # Add "Total" Column
    pivot_df["Total"] = pivot_df.sum(axis=1)

    # Add "Soma" Row for Column Totals
    column_sums = pivot_df.sum(axis=0)  # Sum of columns
    pivot_df.loc['Soma'] = column_sums

    st.dataframe(pivot_df, use_container_width=True)

    st.subheader('2 - Visão por Período')

    # Get valid options for aggregation based on the date column
    valid_options = get_valid_aggregate_options(df=df, date_column='Data')

    # The selected time period from the dropdown menu.
    filter_by = filter_data_by_time(valid_options)

    df_agg = aggregate_by_time(df, 'Data', 'Valor Líquido (R$)', filter_by, {'sum'})
    df_agg.rename(columns={'sum - Valor Líquido (R$)': 'Valor Líquido (R$)'}, inplace=True)

    show_bar_chart(df_agg,
                   'Período',
                    'Valor Líquido (R$)',
                    'Valor Líquido (R$)',
                    f"Dividendos x {filter_by}",
                    '%Y-%m')

    st.markdown('***')
    st.subheader('🗂️ Base de Dados')

    with st.expander("💰 Ver Dividendos Consolidados"):
        st.dataframe(df_dividends, hide_index=True)

    with st.expander(f"💰 Ver Dividendos Agregados por {filter_by}"):
        st.dataframe(df_agg, hide_index=True)

# 4. VALUATION PAGE

# 5. PROTECTION PAGE

# ------------------------------------------------------------------------------------------------ #
# MAIN PAGE FUNCTION

def assets_fii_page():
    """Main Streamlit page function."""
    page_config = set_page_config(page_title='FIIs')
    st.set_page_config(**page_config)

    # Check login before loading the page
    check_login()

    st.title('Carteira de FIIs')
    st.markdown("***")

    assets_loader = AssetsDataLoader(logs_folder)
    logs_loader = LogsDataLoader(logs_folder)
    viz = DataVisualizer(logs_folder)


    selection_dict = {'FIIs': 'wallet',
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
    assets_fii_page()