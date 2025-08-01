"""
Script that contain the 'Lançamentos' Page of the streamlit app.
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
from data.load_data import LogsDataLoader

# COMPONENTS
from components.components import set_page_config, check_login
from components.components import \
    (
        get_valid_aggregate_options,
        aggregate_by_time,
        filter_data_by_time
    )

#WIDGETS
from components.components import set_page_main_menu

# VIZ
from components.viz import show_stacked_bar_chart
# ------------------------------------------------------------------------------------------------ #
# DEFINE CONSTANTS
logs_folder = get_src_folder()

# Main function
def log_transaction_page():
    """Main Streamlit page function."""

    # Create configuration dict
    page_config = set_page_config(page_title='Lançamentos')
    # Set page configuration
    st.set_page_config(**page_config)

    # Check login before loading the page
    check_login()

    st.title('Lançamentos')
    st.markdown("***")

    selection_dict = {'Compras': 'building-add',
                      'Vendas': 'building-dash'}

    selection, options = set_page_main_menu(selection_dict)

    # Create an instance of the LogsDataLoader class
    data_loader = LogsDataLoader(get_src_folder())

    # Load transaction data
    df = data_loader.load_transaction_data()

    # Get valid options for aggregation based on the date column
    valid_options = get_valid_aggregate_options(df=df, date_column='Data')

    # The selected time period from the dropdown menu.
    filter_by = filter_data_by_time(valid_options)

    df_agg = aggregate_by_time(df, 'Data', 'Preço Total (R$)', filter_by, {'sum'}, ['Compra/Venda', 'Tipo Ativo'])
    df_agg.rename(columns={'sum - Preço Total (R$)': 'Preço Total (R$)'}, inplace=True)

    if selection == options[0]:

        # Filter purchases
        purchases = df_agg[df_agg["Compra/Venda"] == "C"]

        # Purchases
        show_stacked_bar_chart(purchases,
                            'Período',
                                'Tipo Ativo',
                                'Preço Total (R$)',
                                f'Compras x {filter_by}')

        st.markdown('***')
        with st.expander(f"📝 Ver compras agregadas por: {filter_by}"):
            st.dataframe(df_agg[df_agg["Compra/Venda"] == "C"], hide_index=True)

        with st.expander("📝 Ver histórico de compras"):
            st.dataframe(df[df["Compra/Venda"] == "C"], hide_index=True)

    elif selection == options[1]:

        # Filter sales
        sales = df_agg[df_agg["Compra/Venda"] == "V"]


        # Sales
        show_stacked_bar_chart(sales,
                            'Período',
                                'Tipo Ativo',
                                'Preço Total (R$)',
                                f'Vendas x {filter_by}')

        st.markdown('***')
        with st.expander(f"📝 Ver vendas agregadas por: {filter_by}"):
            st.dataframe(df_agg[df_agg["Compra/Venda"] == "V"], hide_index=True)

        with st.expander("📝 Ver histórico de vendas"):
            st.dataframe(df[df["Compra/Venda"] == "V"], hide_index=True)

if __name__ == "__main__":
    log_transaction_page()
