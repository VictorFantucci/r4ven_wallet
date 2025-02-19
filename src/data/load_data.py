"""
Script that contains classes used to load multiple sheets and worksheets from my Google Drive.
"""

# Load imports
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

# General data
class WalletDataLoader:
    def __init__(self, logs_folder: str):
        """
        Initializes the WalletDataLoader instance with the given logs folder path.

        Args:
            logs_folder (str): Path to the folder where logs are stored.
        """
        self.credentials_file = 'credentials.json'  # File containing credentials for Google Sheets API
        self.logs_folder = logs_folder  # Folder to store logs
        self.reader = GoogleSheetsReader(self.credentials_file, self.logs_folder)  # Google Sheets reader instance
        self.sheet_id = os.environ.get('wallet_sheet_id')  # Sheet ID from environment variable
        self.worksheet_id = os.environ.get('general_worksheet_id')  # Worksheet ID from environment variable

        # Raise error if sheet ID or worksheet ID is missing
        if not self.sheet_id or not self.worksheet_id:
            raise ValueError("Environment variables for sheet ID or worksheet ID are missing.")

        # Initialize log manager for logging
        self.log_manager = r4venLogManager(logs_folder)

    def get_logger(self):
        """
        Helper method to get a logger dynamically for the current file.

        Returns:
            Logger instance for logging.
        """
        return self.log_manager.function_logger(__file__, console_level=logging.INFO)

    def _fetch_data(self) -> pd.DataFrame:
        """
        Fetches data from the Google Sheets document.

        Returns:
            pd.DataFrame: Data fetched from the specified sheet and worksheet.
            None: If an error occurs while fetching data.
        """
        logger = self.get_logger()  # Get logger for error reporting
        try:
            # Fetch the sheet as a DataFrame
            df = self.reader.get_sheet_as_dataframe(self.sheet_id, self.worksheet_id)
            return df  # Return the fetched DataFrame
        except Exception as e:
            # Log any error encountered while fetching data
            logger.error(f"Error fetching data: {e}")
            return None  # Return None if error occurs

    def load_wallet_overview(self) -> pd.DataFrame:
        """
        Fetches wallet overview data and preprocesses it.

        Returns:
            pd.DataFrame: Preprocessed wallet overview data.
            None: If data fetching fails.
        """
        df = self._fetch_data()  # Fetch the data
        if df is not None:
            # Extract the first row for wallet overview
            df = df.iloc[[0]]
            df = df.iloc[:, :-1]  # Remove the last column

            # Drop empty rows
            df = df.dropna(how="all").reset_index(drop=True)

            # Remove comma from thousands separator and convert values to float
            df = df.applymap(lambda x: float(x.replace(",", "")) if isinstance(x, str) else x)

            # Convert all columns to numeric, coercing errors
            df = df.apply(pd.to_numeric, errors="coerce")

            return df  # Return the preprocessed DataFrame
        else:
            return None  # Return None if data fetching fails

    def load_wallet_division(self) -> pd.DataFrame:
        """
        Fetches wallet division data and preprocesses it.

        Returns:
            pd.DataFrame: Preprocessed wallet division data.
            None: If data fetching fails.
        """
        df = self._fetch_data()  # Fetch the data
        if df is not None:
            # Extract the relevant rows for wallet division
            df_division = df.iloc[2:6]

            # Set the first row as the new header
            df_division.columns = df_division.iloc[0]

            # Drop the first row (now used as header)
            df_division = df_division.drop(2)

            # Reset the index for proper DataFrame structure
            df_division = df_division.reset_index(drop=True)

            # Drop empty rows
            df_division = df_division.dropna(how="all").reset_index(drop=True)

            # Specify columns to convert (excluding 'Classe' and 'Sugestão')
            columns_to_convert = df_division.columns.difference(['Classe', 'Sugestão'])

            # Remove commas from thousands separator in the relevant columns
            df_division[columns_to_convert] = df_division[columns_to_convert].\
                applymap(lambda x: float(x.replace(",", "")) if isinstance(x, str) else x)

            # Convert the specified columns to float
            df_division[columns_to_convert] = df_division[columns_to_convert].apply(pd.to_numeric, errors="coerce")

            return df_division  # Return the preprocessed division data
        else:
            return None  # Return None if data fetching fails

    def load_wallet_goal(self) -> pd.DataFrame:
        """
        Fetches wallet goal data and preprocesses it.

        Returns:
            pd.DataFrame: Preprocessed wallet goal data.
            None: If data fetching fails.
        """
        df = self._fetch_data()  # Fetch the data
        if df is not None:
            # Extract the relevant rows for wallet goal
            df_goal = df.iloc[7:9]

            # Set the first row as the new header
            df_goal.columns = df_goal.iloc[0]

            # Drop the first row (now used as header)
            df_goal = df_goal.drop(7)

            # Reset the index for proper DataFrame structure
            df_goal = df_goal.reset_index(drop=True)

            # Drop empty rows
            df_goal = df_goal.dropna(how="all").reset_index(drop=True)

            # Keep only the first 3 columns
            df_goal = df_goal.iloc[:, :3]

            # Remove commas from thousands separator in the relevant columns
            df_goal = df_goal.applymap(lambda x: float(x.replace(",", "")) if isinstance(x, str) else x)

            # Convert all columns to float
            df_goal = df_goal.apply(pd.to_numeric, errors="coerce")

            return df_goal  # Return the preprocessed goal data
        else:
            return None  # Return None if data fetching fails

#
class AssetsDataLoader:
    def __init__(self, logs_folder):
        """
        Initializes the AssetsDataLoader instance with the given logs folder path.

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

    def _fetch_data(self) -> pd.DataFrame:
        """
        Fetches data from the Google Sheets document.

        Returns:
            pd.DataFrame: Data fetched from the specified sheet and worksheet.
            None: If an error occurs while fetching data.
        """
        logger = self.get_logger()  # Get logger for error reporting
        try:
            # Fetch the sheet as a DataFrame
            df = self.reader.get_sheet_as_dataframe(self.sheet_id, self.worksheet_id, True)
            return df  # Return the fetched DataFrame
        except Exception as e:
            # Log any error encountered while fetching data
            logger.error(f"Error fetching data: {e}")
            return None  # Return None if error occurs

    def _load_data_from_sheet(self, sheet_id, worksheet_id, numeric_columns):
        """
        Loads and preprocesses data from a Google Sheet.

        Args:
            sheet_id (str): ID of the Google Sheets document.
            worksheet_id (str): ID of the worksheet in the sheet.
            date_column (str): Name of the column containing date values.
            numeric_columns (list): List of columns containing numeric values to convert.

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

            # Convert specified columns to numeric
            for column in numeric_columns:
                df[column] = pd.to_numeric(df[column].str.replace(",", " ", regex=True), errors="coerce")

            return df  # Return the preprocessed DataFrame

        except Exception as e:
            # Log any error encountered
            logger.error(f"Error loading data from sheet {worksheet_id}: {e}")
            return None  # Return None if error occurs

    def load_asset_stocks_data(self):
        """
        Fetches and preprocesses stocks data.

        Returns:
            pd.DataFrame: Preprocessed stocks data.
        """
        sheet_id = os.environ.get('wallet_sheet_id')  # Fetch sheet ID from environment variables
        worksheet_id = os.environ.get('asset_stocks_worksheet_id')  # Fetch worksheet ID for transactions

        # Define numeric columns
        numeric_columns = ['% Ideal', 'Quantidade',
                           'Total (R$)', 'Cotação (R$)',
                           'Preço Médio (R$)', '% Atual',
                           'Meta (R$)', 'Falta (R$)',
                           'Sugestão']

        return self._load_data_from_sheet(sheet_id, worksheet_id, numeric_columns)

    def load_asset_real_estate_data(self):
        """
        Fetches and preprocesses real estate data.

        Returns:
            pd.DataFrame: Preprocessed real estate data.
        """
        sheet_id = os.environ.get('wallet_sheet_id')  # Fetch sheet ID from environment variables
        worksheet_id = os.environ.get('asset_real_estate_worksheet_id')  # Fetch worksheet ID for transactions

        # Define numeric columns
        numeric_columns = ['% Ideal', 'Quantidade',
                           'Total (R$)', 'Cotação (R$)',
                           'Preço Médio (R$)', '% Atual',
                           'Meta (R$)', 'Falta (R$)',
                           'Sugestão']

        return self._load_data_from_sheet(sheet_id, worksheet_id, numeric_columns)

    def load_asset_small_caps_data(self):
        """
        Fetches and preprocesses small caps data.

        Returns:
            pd.DataFrame: Preprocessed small caps data.
        """
        sheet_id = os.environ.get('wallet_sheet_id')  # Fetch sheet ID from environment variables
        worksheet_id = os.environ.get('asset_small_caps_worksheet_id')  # Fetch worksheet ID for transactions

        # Define numeric columns
        numeric_columns = ['% Ideal', 'Quantidade',
                           'Total (R$)', 'Cotação (R$)',
                           'Preço Médio (R$)', '% Atual',
                           'Meta (R$)', 'Falta (R$)',
                           'Sugestão']

        return self._load_data_from_sheet(sheet_id, worksheet_id, numeric_columns)

    def load_asset_result_data(self):
        """
        Fetches and preprocesses assets results data.

        Returns:
            pd.DataFrame: Preprocessed assets results data.
        """
        sheet_id = os.environ.get('wallet_sheet_id')  # Fetch sheet ID from environment variables
        worksheet_id = os.environ.get('asset_result_worksheet_id')  # Fetch worksheet ID for transactions

        # Define numeric columns
        numeric_columns = ['Quantidade', 'Gasto (R$)',
                           'Investido (R$)', 'Vendido (R$)',
                           'Cotação (R$)', 'Preço Médio (R$)',
                           'Ganho (R$)', 'Proventos (R$)',
                           'Ganho Ex (R$)', 'Lucro Vendas (R$)',
                           'Ganho (%)', 'Ganho Ex (%)'
                           ]

        return self._load_data_from_sheet(sheet_id, worksheet_id, numeric_columns)

    def load_asset_dividends_data(self):
        """
        Fetches and preprocesses assets dividends data.

        Returns:
            pd.DataFrame: Preprocessed assets dividends data.
        """
        sheet_id = os.environ.get('wallet_sheet_id')  # Fetch sheet ID from environment variables
        worksheet_id = os.environ.get('asset_dividends_worksheet_id')  # Fetch worksheet ID for transactions

        # Define numeric columns
        numeric_columns = ['Total (R$)', 'Acumulado (R$)',
                           'Total Investido (R$)', 'DY - Carteira (%)',
                           'Total - FII (R$)', 'Acumulado - FII (R$)',
                           'Total Investido - FII (R$)', 'DY - FII (%)',
                           'Total - Ações (R$)', 'Acumulado - Ações (R$)',
                           'Total Investido - Ações (R$)', 'DY - Ações (%)',
                           'Total - Small Caps (R$)', 'Acumulado - Small Caps (R$)',
                           'Total Investido - Small Caps (R$)', 'DY - Small Caps (%)',
                           ]

        df = self._load_data_from_sheet(sheet_id, worksheet_id, numeric_columns)

        # Rename column Mês/Ano
        df.rename(columns={'Mês/Ano':'Mês'}, inplace=True)

        return df
