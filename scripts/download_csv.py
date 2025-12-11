from google.oauth2 import service_account
from googleapiclient.discovery import build
import os

class Downloader:
    def __init__(self, repo_root) -> None:
        self.outpath = (repo_root / "csv" / "vatar_match.csv")
        self.account_path = (repo_root / "keys" / str(os.getenv("SERVICE_ACCOUNT_JSON")))

    def download_sheet_as_csv(self):
        # 認証
        creds = service_account.Credentials.from_service_account_file(
            self.account_path,
            scopes=["https://www.googleapis.com/auth/drive.readonly"]
        )

        drive = build("drive", "v3", credentials=creds)

        export_mime = "text/csv"

        file_id = os.getenv("SHEET_ID")
        request = drive.files().export_media(fileId=file_id, mimeType=export_mime)
        data = request.execute()

        with open(self.outpath, "wb") as f:
            f.write(data)

        print(f"Downloaded: {self.outpath}")
        return self.outpath