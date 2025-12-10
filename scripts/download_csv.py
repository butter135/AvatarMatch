from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

def download_sheet_as_csv(
        service_account_json: str,
        spreadsheet_id: str,
        gid: int = 0,
        out_path: str = "latest.csv"
):
    # 認証
    creds = service_account.Credentials.from_service_account_file(
        service_account_json,
        scopes=["https://www.googleapis.com/auth/drive.readonly"]
    )

    drive = build("drive", "v3", credentials=creds)

    export_mime = "text/csv"

    file_id = spreadsheet_id
    request = drive.files().export_media(fileId=file_id, mimeType=export_mime)
    data = request.execute()

    with open(out_path, "wb") as f:
        f.write(data)

    print(f"Downloaded: {out_path}")
    return out_path

load_dotenv("keys/.env")

download_sheet_as_csv(
    service_account_json=os.getenv("SERVICE_ACCOUNT_JSON"),
    spreadsheet_id=os.getenv("SHEET_ID"),
    out_path="../csv/avatar_match.csv"
)