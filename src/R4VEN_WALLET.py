import os
import sys
import streamlit as st
from PIL import Image

app_directory =  os.path.dirname(os.path.dirname(__file__))
sys.path.append(app_directory)

def app() -> None:
    # Change page name and icon
    page_icon = Image.open(os.path.join(app_directory, 'src', 'imgs', 'r4ven_icon.png'))

    page_config = {'page_title': 'r4ven_wallet',
                   'page_icon': page_icon,
                   'layout': 'wide'}

    st.set_page_config(**page_config)

    st.title('R4VEN - Independência Financeira')

if __name__ == '__main__':
    app()
