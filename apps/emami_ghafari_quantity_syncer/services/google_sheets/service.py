import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import gspread_dataframe
from apps.emami_ghafari_quantity_syncer.services.google_sheets import credentials


class GoogleSheetsService:
    def __init__(self):
        creds = Credentials.from_service_account_info(
            credentials.GOOGLE_SHEETS_CREDENTIALS,
            scopes=credentials.GOOGLE_SHEETS_SCOPES,
        )
        self.client = gspread.authorize(creds)

        sheet_id = credentials.GOOGLE_SHEETS_TARGET_SHEET_ID
        sheet_name = credentials.GOOGLE_SHEETS_TARGET_SHEET_SHEET_NAME
        self.worksheet = self.client.open_by_key(sheet_id).worksheet(sheet_name)

    def update_sheet(self, new_df: pd.DataFrame):
        if new_df.empty:
            print("⚠️ DataFrame is empty. Nothing to update.")
            return

        self.worksheet.clear()
        gspread_dataframe.set_with_dataframe(
            self.worksheet, new_df, include_index=False, include_column_header=True
        )
