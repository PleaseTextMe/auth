import os
import uuid

import pytest

from src.domain.dtos.user import UserCreateDatabaseDTO
from src.infrastructure.repositories.session import SQLAlchemySessionRepository
from src.infrastructure.repositories.user import SQLAlchemyUserRepository


@pytest.fixture
def repo(db_session):
    return SQLAlchemySessionRepository(session=db_session)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_session_repository_create_and_get(repo: SQLAlchemySessionRepository, db_session):

    # Create a user first
    user_repo = SQLAlchemyUserRepository(session=db_session)
    suffix = str(uuid.uuid4())[:8]
    user_dto = UserCreateDatabaseDTO(
        username=f"sess_user_{suffix}",
        email=f"sess_user_{suffix}@test.com",
        password_hash=b"haaaaasssssssssh",
        public_bundle={},
        vault={}
    )
    user = await user_repo.create(user_dto)

    from src.domain.entities.session import Session

    auth_token_hash = os.urandom(32)

    session_entity = Session.create(
        user_id=user.id,
        auth_token_hash=auth_token_hash,
        user_agent="integration-test",
        user_ip="127.0.0.1",
    )

    created_session = await repo.create(session_entity)
    assert created_session.id is not None
    assert created_session.user_id == user.id
    assert created_session.auth_token_hash == auth_token_hash
    assert created_session.is_active is True

    fetched_session = await repo.get_by_hash(auth_token_hash)
    assert fetched_session is not None
    assert fetched_session.id == created_session.id
    assert fetched_session.is_active is True

    await repo.deactivate_token(auth_token_hash)

    fetched_session_after = await repo.get_by_hash(auth_token_hash)
    assert fetched_session_after is not None
    assert fetched_session_after.is_active is False
