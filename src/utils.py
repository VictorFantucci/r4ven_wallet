import os
import sys
import pandas as pd

# Load relative imports
from data.gspread_fetcher import GoogleSheetsReader

# Load environment variables
from dotenv import load_dotenv, find_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

utils_directory =  os.path.dirname(os.path.dirname(__file__))

def get_src_folder() -> str:
    """
    Returns the path to the source (src) folder.

    Returns:
        str: The absolute path to the src folder.
    """
    return os.path.join(utils_directory, "src")

def load_transaction_data():
    """Fetch transaction log and preprocess data."""
    logs_folder = get_src_folder()
    reader = GoogleSheetsReader('credentials.json', logs_folder)

    sheet_id = os.environ.get('wallet_sheet_id')
    worksheet_id = os.environ.get('log_transactions_worksheet_id')

    df = reader.get_sheet_as_dataframe(sheet_id, worksheet_id)

    # Convert columns
    df["Data Negócio"] = pd.to_datetime(df["Data Negócio"], errors="coerce")
    df["Preço (R$)"] = pd.to_numeric(df["Preço (R$)"], errors="coerce")
    df["Preço Total (R$)"] = pd.to_numeric(df["Preço Total (R$)"], errors="coerce")

    # Create month column
    df["Mês"] = df["Data Negócio"].dt.to_period("M").astype(str)

    return df

def load_passive_income_data():
    """Fetch transaction log and preprocess data."""
    logs_folder = get_src_folder()
    reader = GoogleSheetsReader('credentials.json', logs_folder)

    sheet_id = os.environ.get('wallet_sheet_id')
    worksheet_id = os.environ.get('log_passive_income_worksheet_id')

    df = reader.get_sheet_as_dataframe(sheet_id, worksheet_id)

    # Convert columns
    df["Data"] = pd.to_datetime(df["Data"], errors="coerce")
    df["Valor Líquido (R$)"] = pd.to_numeric(df["Valor Líquido (R$)"], errors="coerce")

    # Create month column
    df["Mês"] = df["Data"].dt.to_period("M").astype(str)

    return df
