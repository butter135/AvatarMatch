from scripts import download_csv, create_graph, auto_push
from scripts.auto_push import AutoPush
from scripts.create_graph import CreateGraph
from scripts.download_csv import Downloader
from pathlib import Path
from dotenv import load_dotenv


def find_repo_root() -> Path:
    p = Path(__file__).resolve()
    for parent in [p] + list(p.parents):
        if (parent / ".git").exists():
            return parent
    raise RuntimeError(".git が見つかりませんでした")


repo_root = find_repo_root()
load_dotenv((repo_root / "keys" / ".env"))
Downloader(repo_root).download_sheet_as_csv()
CreateGraph(repo_root).run()
AutoPush(repo_root).push()

