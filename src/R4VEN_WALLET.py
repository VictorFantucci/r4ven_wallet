import os
import streamlit as st
from PIL import Image

def app() -> None:
    # Change page name and icon
    page_icon = Image.open('src/imgs/r4ven_icon.png')

    page_config = {'page_title': 'r4ven_wallet',
                   'page_icon': page_icon,
                   'layout': 'wide'}

    st.set_page_config(**page_config)

    st.title('Carteira - R4VEN')

if __name__ == '__main__':
    app()
