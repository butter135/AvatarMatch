import subprocess
import datetime
from pathlib import Path
import sys

class AutoPush:
    def __init__(self, repo_root) -> None:
        self.repo_root = repo_root

    def _run(self, cmd, cwd=None):
        """サブプロセス実行ヘルパー"""
        if cwd is None:
            cwd = self.repo_root  # デフォルトでリポジトリルートで実行

        res = subprocess.run(
            cmd, cwd=cwd, text=True, capture_output=True
        )
        if res.returncode != 0:
            print(res.stdout)
            print(res.stderr, file=sys.stderr)
            raise RuntimeError(f"Command failed: {' '.join(cmd)}")
        return res.stdout.strip()

    def _is_git_repo(self, path: Path) -> bool:
        return (path / ".git").exists()

    def _has_changes(self, target: str) -> bool:
        """指定ディレクトリに差分があるかどうか"""
        # -- を挟んでおくとパス扱いが確実になる
        out = self._run(["git", "status", "--porcelain", "--", target])
        # デバッグしたければこれを一旦付ける:
        # print("DEBUG status output:", repr(out))
        return out != ""

    def push(self):
        repo_root = self.repo_root

        if not self._is_git_repo(repo_root):
            raise ValueError("このスクリプトは git リポジトリ内で実行してください。")

        # docs ディレクトリだけを対象にする場合
        target = "docs"

        if not self._has_changes(target):
            print(f"変更なし: {target}")
            return False

        # git add
        self._run(["git", "add", target])

        # commit
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg = f"[auto] update pages ({now})"
        self._run(["git", "commit", "-m", msg])

        # push
        self._run(["git", "push", "origin", "main"])
        print("push 完了！")

        return True
