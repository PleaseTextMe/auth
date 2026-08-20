from src.infrastructure.models.session import session as session_table
from src.infrastructure.models.user import user as user_table


def test_user_table_schema():
    assert user_table.name == "user"
    column_names = {c.name for c in user_table.columns}
    expected = {
        "id",
        "username",
        "email",
        "password_hash",
        "public_bundle",
        "vault",
        "is_active",
        "created_at",
        "updated_at",
    }
    assert expected.issubset(column_names)


def test_session_table_schema():
    assert session_table.name == "session"
    column_names = {c.name for c in session_table.columns}
    expected = {
        "id",
        "user_id",
        "user_agent",
        "auth_token_hash",
        "user_ip",
        "is_active",
        "device_type",
        "created_at",
        "updated_at",
    }
    assert expected.issubset(column_names)
