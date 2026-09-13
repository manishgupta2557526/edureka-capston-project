from app.auth import SimpleAuth
from app.config import load_settings


def test_auth_can_create_and_verify_hashed_users(tmp_path):
    users_file = tmp_path / "users.txt"
    auth = SimpleAuth(users_file=str(users_file))

    auth.create_user("ops", "super-secret")

    assert auth.authenticate("ops", "super-secret")
    assert not auth.authenticate("ops", "wrong-password")


def test_auth_accepts_legacy_plaintext_and_upgrades(tmp_path):
    users_file = tmp_path / "users.txt"
    users_file.write_text("admin:admin123\n", encoding="utf-8")

    auth = SimpleAuth(users_file=str(users_file))

    assert auth.authenticate("admin", "admin123")
    upgraded = users_file.read_text(encoding="utf-8")
    assert "admin:admin123" not in upgraded
    assert auth.hash_password("admin123") in upgraded


def test_settings_loads_environment_values(monkeypatch, tmp_path):
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("DEFAULT_AUTH_USERNAME", "produser")
    monkeypatch.setenv("DEFAULT_AUTH_PASSWORD", "prodpass")
    monkeypatch.setenv("UPLOAD_DIR", str(tmp_path / "uploads"))

    settings = load_settings()

    assert settings.app_env == "production"
    assert settings.default_auth_username == "produser"
    assert settings.default_auth_password == "prodpass"
    assert settings.upload_dir == str(tmp_path / "uploads")
