from src.infrastructure.models.session import mapped_session_table
from src.infrastructure.models.user import mapped_user_table


def start_mappers():
    mapped_session_table()
    mapped_user_table()
