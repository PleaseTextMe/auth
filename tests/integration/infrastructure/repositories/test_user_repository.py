import uuid

import pytest

from src.domain.dtos.user import UserCreateDatabaseDTO
from src.infrastructure.repositories.user import SQLAlchemyUserRepository


@pytest.fixture
def repo(db_session):
    return SQLAlchemyUserRepository(session=db_session)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_repository_create_and_get(repo: SQLAlchemyUserRepository):
    suffix = str(uuid.uuid4())[:8]
    username = f"int_user_{suffix}"
    email = f"{username}@test.com"

    user_dto = UserCreateDatabaseDTO(
        username=username,
        email=email,
        password_hash=b"haaaaasssssssssh",
        public_bundle={},
        vault={}
    )

    created_user = await repo.create(user_dto)
    assert created_user.id is not None
    assert created_user.username == username
    assert created_user.email == email

    fetched_user_by_email = await repo.get_by_email(email)
    assert fetched_user_by_email is not None
    assert fetched_user_by_email.id == created_user.id

    fetched_user_by_username = await repo.get_by_username(username)
    assert fetched_user_by_username is not None
    assert fetched_user_by_username.id == created_user.id

    fetched_user_by_id = await repo.get_by_id(created_user.id)
    assert fetched_user_by_id is not None
    assert fetched_user_by_id.email == email

    all_users = await repo.get_all()
    assert len(all_users) >= 1
    assert any(u.id == created_user.id for u in all_users)
