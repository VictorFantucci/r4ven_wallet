"""
Script that contain the 'Proventos' Page of the streamlit app.
"""

# ------------------------------------------------------------------------------------------------ #
# IMPORTS

import streamlit as st
import pandas as pd

# ------------------------------------------------------------------------------------------------ #
# RELATIVE IMPORTS

from utils import get_src_folder

# DATA
from data.load_data import LogsDataLoader

# COMPONENTS
from components.components import set_page_config
from components.components import \
    (
        get_valid_aggregate_options,
        aggregate_by_time,
        filter_data_by_time
    )

# VIZ
from components.viz import show_stacked_bar_chart, show_accumulated_bar_chart

# ------------------------------------------------------------------------------------------------ #
# DEFINE CONSTANTS
logs_folder = get_src_folder()


# ------------------------------------------------------------------------------------------------ #
# MAIN PAGE FUNCTION

def log_passive_income_page():
    """Main Streamlit page function."""

    # Create configuration dict
    page_config = set_page_config(page_title='Proventos')
    # Set page configuration
    st.set_page_config(**page_config)

    st.title('Proventos')
    st.markdown("***")

    # Create an instance of the LogsDataLoader class
    data_loader = LogsDataLoader(get_src_folder())

    # Load passive income data
    df = data_loader.load_passive_income_data()
    df.drop(columns={"Mês/Ano"}, inplace=True)

    # Get valid options for aggregation based on the date column
    valid_options = get_valid_aggregate_options(df=df, date_column='Data')

    # The selected time period from the dropdown menu.
    filter_by = filter_data_by_time(valid_options)

    df_agg = aggregate_by_time(df, 'Data', 'Valor Líquido (R$)', filter_by, {'sum'}, 'Tipo Ativo')
    df_agg.rename(columns={'sum - Valor Líquido (R$)': 'Valor Líquido (R$)'}, inplace=True)

    col1, col2 = st.columns(2)

    with col1:
        show_stacked_bar_chart(df_agg,
                                'Período',
                                'Tipo Ativo',
                                'Valor Líquido (R$)',
                                f"Proventos x {filter_by}"
                                      )
    with col2:
        show_accumulated_bar_chart(df_agg,
                                    'Período',
                                    'Valor Líquido (R$)',
                                    'Valor Líquido Acumulado(R$)',
                                    f"Proventos Acumulados x {filter_by}")

    st.markdown('***')
    with st.expander(f"💰 Ver Proventos Agregados por {filter_by}"):
        st.dataframe(df, hide_index=True)

    with st.expander("💰 Ver Histórico de Proventos"):
        st.dataframe(df, hide_index=True)

if __name__ == "__main__":
    log_passive_income_page()