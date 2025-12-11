from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

class Downloader:
    def download_sheet_as_csv(self):
        outpath = "./csv/avatar_match.csv"
        load_dotenv("keys/.env")

        # 認証
        creds = service_account.Credentials.from_service_account_file(
            os.getenv("SERVICE_ACCOUNT_JSON"),
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )

        drive = build("drive", "v3", credentials=creds)

        export_mime = "text/csv"

        file_id = os.getenv("SHEET_ID")
        request = drive.files().export_media(fileId=file_id, mimeType=export_mime)
        data = request.execute()

        with open(outpath, "wb") as f:
            f.write(data)

        print(f"Downloaded: {outpath}")
        return outpath

Downloader().download_sheet_as_csv()