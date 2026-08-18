from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.dtos.user import UserCreateDatabaseDTO
from src.domain.entities.user import User
from src.infrastructure.repositories.user import SQLAlchemyUserRepository


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def repo(mock_session):
    return SQLAlchemyUserRepository(session=mock_session)


@pytest.fixture
def mock_db_user():
    return MagicMock()


@pytest.fixture
def mock_user_instance():
    return MagicMock(spec=User)


@pytest.mark.asyncio
@patch("src.infrastructure.repositories.user.insert")
@patch("src.infrastructure.repositories.user.User.model_validate")
async def test_user_repo_create(
    mock_model_validate, mock_insert, repo, mock_session, mock_db_user, mock_user_instance
):
    mock_model_validate.return_value = mock_user_instance
    mock_query = MagicMock()
    mock_insert.return_value.values.return_value.returning.return_value = mock_query

    mock_result = MagicMock()
    mock_result.unique.return_value.scalar_one.return_value = mock_db_user
    mock_session.execute.return_value = mock_result

    user_data = UserCreateDatabaseDTO(
        username="test", email="test@test.com", password_hash=b"pwd", public_bundle={}, vault={}
    )

    result = await repo.create(user_data)

    assert result is mock_user_instance
    mock_session.execute.assert_called_once_with(mock_query)
    mock_model_validate.assert_called_once_with(mock_db_user)


@pytest.mark.asyncio
@patch("src.infrastructure.repositories.user.select")
@patch("src.infrastructure.repositories.user.User.model_validate")
async def test_user_repo_get_by_email_found(
    mock_model_validate, mock_select, repo, mock_session, mock_db_user, mock_user_instance
):
    mock_model_validate.return_value = mock_user_instance
    mock_query = MagicMock()
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_db_user
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_email("test@test.com")

    assert result is mock_user_instance
    mock_session.execute.assert_called_once_with(mock_query)
    mock_model_validate.assert_called_once_with(mock_db_user)


@pytest.mark.asyncio
@patch("src.infrastructure.repositories.user.select")
async def test_user_repo_get_by_email_not_found(mock_select, repo, mock_session):
    mock_query = MagicMock()
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_email("test@test.com")

    assert result is None
    mock_session.execute.assert_called_once_with(mock_query)


@pytest.mark.asyncio
@patch("src.infrastructure.repositories.user.select")
@patch("src.infrastructure.repositories.user.User.model_validate")
async def test_user_repo_get_by_username_found(
    mock_model_validate, mock_select, repo, mock_session, mock_db_user, mock_user_instance
):
    mock_model_validate.return_value = mock_user_instance
    mock_query = MagicMock()
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_db_user
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_username("test")

    assert result is mock_user_instance
    mock_session.execute.assert_called_once_with(mock_query)
    mock_model_validate.assert_called_once_with(mock_db_user)


@pytest.mark.asyncio
@patch("src.infrastructure.repositories.user.select")
async def test_user_repo_get_by_username_not_found(mock_select, repo, mock_session):
    mock_query = MagicMock()
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_username("test")

    assert result is None
    mock_session.execute.assert_called_once_with(mock_query)


@pytest.mark.asyncio
@patch("src.infrastructure.repositories.user.select")
@patch("src.infrastructure.repositories.user.User.model_validate")
async def test_user_repo_get_by_id_found(
    mock_model_validate, mock_select, repo, mock_session, mock_db_user, mock_user_instance
):
    mock_model_validate.return_value = mock_user_instance
    mock_query = MagicMock()
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_db_user
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_id(1)

    assert result is mock_user_instance
    mock_session.execute.assert_called_once_with(mock_query)
    mock_model_validate.assert_called_once_with(mock_db_user)


@pytest.mark.asyncio
@patch("src.infrastructure.repositories.user.select")
async def test_user_repo_get_by_id_not_found(mock_select, repo, mock_session):
    mock_query = MagicMock()
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_id(1)

    assert result is None
    mock_session.execute.assert_called_once_with(mock_query)


@pytest.mark.asyncio
@patch("src.infrastructure.repositories.user.select")
@patch("src.infrastructure.repositories.user.User.model_validate")
async def test_user_repo_get_all(
    mock_model_validate, mock_select, repo, mock_session, mock_db_user, mock_user_instance
):
    mock_model_validate.return_value = mock_user_instance
    mock_query = MagicMock()
    mock_select.return_value = mock_query

    mock_result = MagicMock()
    mock_result.unique.return_value.scalars.return_value.all.return_value = [
        mock_db_user,
        mock_db_user,
    ]
    mock_session.execute.return_value = mock_result

    result = await repo.get_all()

    assert result == [mock_user_instance, mock_user_instance]
    mock_session.execute.assert_called_once_with(mock_query)
    assert mock_model_validate.call_count == 2
