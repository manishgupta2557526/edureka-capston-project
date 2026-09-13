from typing import Optional
import hashlib
import os

from app.config import ensure_data_dir, load_settings


class SimpleAuth:
    def __init__(self, users_file: Optional[str] = None) -> None:
        settings = load_settings()
        self.users_file = users_file or settings.auth_users_file
        ensure_data_dir(os.path.dirname(self.users_file) or ".")
        self._ensure_default_user(settings)

    def _ensure_default_user(self, settings) -> None:
        if os.path.exists(self.users_file):
            return

        credentials = []
        if settings.default_auth_username and settings.default_auth_password:
            hashed_password = self.hash_password(settings.default_auth_password)
            credentials.append(f"{settings.default_auth_username}:{hashed_password}\n")
        else:
            credentials.append(f"admin:{self.hash_password('admin123')}\n")

        with open(self.users_file, "w", encoding="utf-8") as handle:
            handle.writelines(credentials)

    def authenticate(self, username: str, password: str) -> bool:
        if not os.path.exists(self.users_file):
            return False
        entered_hash = self.hash_password(password)
        with open(self.users_file, "r", encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                stored_user, stored_password = line.split(":", 1)
                if stored_user != username:
                    continue

                if stored_password == entered_hash:
                    return True

                # Backward compatibility for old plain-text user files.
                if stored_password == password:
                    self._upgrade_plaintext_password(stored_user, entered_hash)
                    return True
        return False

    def create_user(self, username: str, password: str) -> None:
        with open(self.users_file, "a", encoding="utf-8") as handle:
            handle.write(f"{username}:{self.hash_password(password)}\n")

    def hash_password(self, password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def _upgrade_plaintext_password(self, username: str, hashed_password: str) -> None:
        with open(self.users_file, "r", encoding="utf-8") as handle:
            lines = handle.readlines()

        updated_lines = []
        for line in lines:
            raw = line.strip()
            if not raw:
                continue
            stored_user, stored_password = raw.split(":", 1)
            if stored_user == username and stored_password != hashed_password:
                updated_lines.append(f"{username}:{hashed_password}\n")
            else:
                updated_lines.append(line if line.endswith("\n") else f"{line}\n")

        with open(self.users_file, "w", encoding="utf-8") as handle:
            handle.writelines(updated_lines)
