import os
import logging
import pandas as pd
import warnings
from r4ven_utils.log4me import r4venLogManager

# Ignore specific warning
warnings.filterwarnings("ignore", category=FutureWarning)

# Load relative imports
from utils import get_src_folder
from data.gspread_fetcher import GoogleSheetsReader

# Load environment variables
from dotenv import load_dotenv, find_dotenv
dotenv_path = find_dotenv()
load_dotenv(dotenv_path)


# Log data
class LogsDataLoader:
    def __init__(self, logs_folder):
        """
        Initializes the LogsDataLoader instance with the given logs folder path.

        Args:
            logs_folder (str): Path to the folder where logs are stored.
        """
        self.credentials_file = 'credentials.json'  # File containing credentials for Google Sheets API
        self.logs_folder = logs_folder  # Folder to store logs
        self.reader = GoogleSheetsReader(self.credentials_file, self.logs_folder)  # Google Sheets reader instance

        # Initialize log manager for logging
        self.log_manager = r4venLogManager(logs_folder)

    def get_logger(self):
        """
        Helper method to get a logger dynamically for the current file.

        Returns:
            Logger instance for logging.
        """
        return self.log_manager.function_logger(__file__, console_level=logging.INFO)

    def _load_data_from_sheet(self, sheet_id, worksheet_id, date_column, amount_columns):
        """
        Loads and preprocesses data from a Google Sheet.

        Args:
            sheet_id (str): ID of the Google Sheets document.
            worksheet_id (str): ID of the worksheet in the sheet.
            date_column (str): Name of the column containing date values.
            amount_columns (list): List of columns containing numeric values to convert.

        Returns:
            pd.DataFrame: Preprocessed data in a DataFrame format.
            None: If an error occurs while loading or processing data.
        """
        logger = self.get_logger()  # Get logger for error reporting
        try:
            # Ensure sheet and worksheet IDs are provided
            if not sheet_id or not worksheet_id:
                raise ValueError("Environment variables for sheet ID or worksheet ID are missing.")

            # Fetch data from the Google Sheet
            df = self.reader.get_sheet_as_dataframe(sheet_id, worksheet_id)

            # Convert date column to datetime
            df[date_column] = pd.to_datetime(df[date_column], errors="coerce")

            # Convert specified amount columns to numeric
            for column in amount_columns:
                df[column] = pd.to_numeric(df[column], errors="coerce")

            # Create a new column 'Mês' representing the month of each date entry
            df["Mês"] = df[date_column].dt.to_period("M").astype(str)

            return df  # Return the preprocessed DataFrame

        except Exception as e:
            # Log any error encountered
            logger.error(f"Error loading data from sheet {worksheet_id}: {e}")
            return None  # Return None if error occurs

    def load_transaction_data(self):
        """
        Fetches and preprocesses transaction log data.

        Returns:
            pd.DataFrame: Preprocessed transaction data.
        """
        sheet_id = os.environ.get('wallet_sheet_id')  # Fetch sheet ID from environment variables
        worksheet_id = os.environ.get('log_transactions_worksheet_id')  # Fetch worksheet ID for transactions
        return self._load_data_from_sheet(sheet_id, worksheet_id, "Data Negócio", ["Preço (R$)", "Preço Total (R$)"])

    def load_passive_income_data(self):
        """
        Fetches and preprocesses passive income log data.

        Returns:
            pd.DataFrame: Preprocessed passive income data.
        """
        sheet_id = os.environ.get('wallet_sheet_id')  # Fetch sheet ID from environment variables
        worksheet_id = os.environ.get('log_passive_income_worksheet_id')  # Fetch worksheet ID for passive income logs
        return self._load_data_from_sheet(sheet_id, worksheet_id, "Data", ["Valor Líquido (R$)"])
