"""
Script that contains the class used to fetches data from Google Sheets.
"""

# ------------------------------------------------------------------------------------------------ #
# IMPORT
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import logging
from r4ven_utils.log4me import r4venLogManager

# ------------------------------------------------------------------------------------------------ #
# GOOGLE SHEET DATA FETCH CLASS
class GoogleSheetsReader:
    def __init__(self, credentials_file: str, base_log_dir: str):
        """
        Initializes the GoogleSheetsReader instance.

        Args:
            credentials_file (str): Path to the credentials JSON file for Google Sheets API.
            base_log_dir (str): Base directory for storing logs.
        """
        self.credentials_file = credentials_file
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']

        # Initialize logger
        self.log_manager = r4venLogManager(base_log_dir)

        # Authorize credentials
        self.client = self._authorize()

    def get_logger(self):
        """ Helper method to get the logger dynamically"""
        return self.log_manager.function_logger(__file__, console_level=logging.INFO)

    def _authorize(self):
        """Authorizes the Google Sheets API client."""
        logger = self.get_logger()
        logger.info("Authorizing Google Sheets API client.")
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(self.credentials_file, self.scopes)
            logger.info("Authorization successful.")
            return gspread.authorize(credentials)
        except Exception as e:
            logger.error(f"Authorization failed: {e}")
            raise

    def get_sheet_as_dataframe(self,
                               sheet_id: str,
                               worksheet_id: int,
                               drop_last_row: bool = False) -> pd.DataFrame:
        """
        Fetches data from a Google Sheets worksheet and returns it as a pandas DataFrame.

        Args:
            sheet_id (str): The ID of the Google Sheet.
            worksheet_id (int): The ID of the worksheet within the sheet.
            drop_last_row (bool): If True, the last row of the DataFrame will be dropped.

        Returns:
            pandas.DataFrame: containing the worksheet data
        """
        logger = self.get_logger()
        try:
            logger.info(f"Opening Google Sheet with ID: {sheet_id}")
            sheet = self.client.open_by_key(sheet_id)

            logger.info(f"Accessing worksheet with ID: {worksheet_id}")
            worksheet = sheet.get_worksheet_by_id(worksheet_id)

            logger.info(f"Fetching data from worksheet ID: {worksheet_id}")
            data = worksheet.get_all_values()

            df = pd.DataFrame(data[1:], columns=data[0])  # Use the first row as column names

            if drop_last_row:
                logger.info("Dropping the last row of the DataFrame as requested.")
                df = df[:-1]

            logger.info(f"Data successfully loaded for sheet: {sheet_id}, worksheet: {worksheet_id}")
            return df
        except Exception as e:
            logger.error(f"Error fetching data from sheet {sheet_id}, worksheet {worksheet_id}: {e}")
            raise
