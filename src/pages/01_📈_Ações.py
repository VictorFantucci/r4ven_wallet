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
from data.load_data import AssetsDataLoader, LogsDataLoader, StocksValuationDataLoader

# COMPONENTS
from components.components import reorder_dataframe_columns
from components.components import set_page_config, set_page_main_menu, check_login
from components.components import \
    (
        get_valid_aggregate_options,
        aggregate_by_time,
        filter_data_by_time
    )

# VIZ
from components.viz import DataVisualizer
from components.viz import show_stacked_bar_chart, show_line_chart

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

    col1, col2 = st.columns(2)

    with col1:
        fig = viz.r4ven_pie_plot(df, 'Total (R$)', 'Ativo', 'Ações')
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        fig = viz.r4ven_pie_plot(df, 'Total (R$)', 'Setor', 'Setores')
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('***')
    st.subheader('🗂️ Base de Dados')

    with st.expander('Carteira de Ações'):
        st.dataframe(df, hide_index=True)

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

    with st.expander('DY - Ações (%)'):
        show_line_chart(df_dividends,
                        'Mês',
                        'DY - Ações (%)',
                        'DY - Ações (%)',
                        '%Y-%m'
                        )

    st.subheader('1. Visão Anualizada')

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

    st.dataframe(pivot_df, use_container_width=True)

    st.subheader('2 - Visão por Período')

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
    st.subheader('🗂️ Base de Dados')

    with st.expander("💰 Ver Dividendos Consolidados"):
        st.dataframe(df_dividends, hide_index=True)

    with st.expander(f"💰 Ver Dividendos Agregados por {filter_by}"):
        st.dataframe(df_agg, hide_index=True)

# 4. VALUATION PAGE
def display_valuation(assets_loader, valuation_loader, viz):
    """Displays the stock portfolio valuation in an expandable section."""

    # Load stock portfolio data and remove the last row (possibly a summary row)
    stock_portfolio_df = assets_loader.load_asset_stocks_data()
    stock_portfolio_df = stock_portfolio_df[:-1]

    # Convert percentage columns to proper scale (0-100%)
    stock_portfolio_df.loc[:, ['% Ideal', '% Atual']] *= 100

    # Load stock valuation data
    stock_valuation_df = valuation_loader.load_asset_stocks_data()

    # Calculate the total invested amount in stocks
    total_invested_value = stock_valuation_df['TOTAL INVESTIDO'].sum()

    # Calculate the total predicted annual dividend yield
    total_annual_dividends = stock_valuation_df['DIVIDENDO ANUAL'].sum()

    # Calculate the expected total future value of the portfolio
    expected_portfolio_value = stock_valuation_df['VALOR FINAL'].sum()

    # Compute the current dividend yield of the portfolio
    portfolio_dividend_yield = total_annual_dividends / total_invested_value

    # Compute the expected portfolio growth percentage
    expected_growth_rate = (expected_portfolio_value - total_invested_value) / total_invested_value

    col1, col2, col3, col4 = st.columns(4)

    col1.metric('Total Investido', f"R${total_invested_value:,.2f}")
    col2.metric('Valor Esperado', f"R${expected_portfolio_value:,.2f}")
    col3.metric('Crescimento Esperado', f"{round(expected_growth_rate * 100, 2)}%")
    col4.metric('DY Anual da Carteira', f"{round(portfolio_dividend_yield * 100, 2)}%")

    # Display the stock valuation data as a dataframe
    st.dataframe(stock_valuation_df, hide_index=True)

    # Section separator and header
    st.markdown('***')
    st.subheader('🗂️ Base de Dados')

    # Expandable section for displaying stock portfolio details
    with st.expander('Carteira de Ações'):
        st.dataframe(stock_portfolio_df, hide_index=True)

def display_valuation_search(valuation_loader, viz):
    """"""
    # Load stock valuation database
    stock_valuation_df = valuation_loader.load_asset_stocks_data()

# 5. PROTECTION PAGE

# ------------------------------------------------------------------------------------------------ #
# MAIN PAGE FUNCTION

def assets_stocks_page():
    """Main Streamlit page function."""
    page_config = set_page_config(page_title='Ações')
    st.set_page_config(**page_config)

    # Check login before loading the page
    check_login()

    st.title('Carteira de Ações')
    st.markdown("***")

    assets_loader = AssetsDataLoader(logs_folder)
    logs_loader = LogsDataLoader(logs_folder)
    valuation_loader = StocksValuationDataLoader(logs_folder)
    viz = DataVisualizer(logs_folder)


    selection_dict = {'Ações': 'wallet',
                      'Resultado': 'bank',
                      'Proventos': 'piggy-bank',
                      'Valuation': 'crosshair'}

    selection, options = set_page_main_menu(selection_dict)

    if selection == options[0]:
        display_data(assets_loader, viz)
    elif selection == options[1]:
        display_portfolio_result(assets_loader)
    elif selection == options[2]:
        display_dividends(assets_loader, logs_loader)
    elif selection == options[3]:
        display_valuation(assets_loader, valuation_loader, viz)

if __name__ == "__main__":
    assets_stocks_page()