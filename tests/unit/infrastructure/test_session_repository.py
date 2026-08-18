from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.session import Session
from src.infrastructure.repositories.session import SQLAlchemySessionRepository


@pytest.fixture
def mock_session():
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def repo(mock_session):
    return SQLAlchemySessionRepository(session=mock_session)


@pytest.fixture
def mock_db_session():
    return MagicMock()


@pytest.fixture
def mock_session_instance():
    return MagicMock(spec=Session)


@pytest.mark.asyncio
@patch("src.infrastructure.repositories.session.insert")
@patch("src.infrastructure.repositories.session.Session.model_validate")
async def test_session_repo_create(
    mock_model_validate, mock_insert, repo, mock_session, mock_db_session, mock_session_instance
):
    mock_model_validate.return_value = mock_session_instance
    mock_query = MagicMock()
    mock_insert.return_value.values.return_value.returning.return_value = mock_query

    mock_result = MagicMock()
    mock_result.unique.return_value.scalar_one.return_value = mock_db_session
    mock_session.execute.return_value = mock_result

    session_data = MagicMock(spec=Session)
    session_data.model_dump.return_value = {"id": 1, "is_active": True}
    session_data.auth_token_hash = b"hash"

    result = await repo.create(session_data)

    assert result is mock_session_instance
    mock_session.execute.assert_called_once_with(mock_query)
    mock_model_validate.assert_called_once_with(mock_db_session)


@pytest.mark.asyncio
@patch("src.infrastructure.repositories.session.select")
@patch("src.infrastructure.repositories.session.Session.model_validate")
async def test_session_repo_get_by_hash_found(
    mock_model_validate, mock_select, repo, mock_session, mock_db_session, mock_session_instance
):
    mock_model_validate.return_value = mock_session_instance
    mock_query = MagicMock()
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_db_session
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_hash(b"hash")

    assert result is mock_session_instance
    mock_session.execute.assert_called_once_with(mock_query)
    mock_model_validate.assert_called_once_with(mock_db_session)


@pytest.mark.asyncio
@patch("src.infrastructure.repositories.session.select")
async def test_session_repo_get_by_hash_not_found(mock_select, repo, mock_session):
    mock_query = MagicMock()
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_hash(b"hash")

    assert result is None
    mock_session.execute.assert_called_once_with(mock_query)


@pytest.mark.asyncio
@patch("src.infrastructure.repositories.session.update")
@patch("src.infrastructure.repositories.session.Session")
async def test_session_repo_deactivate_token(mock_session_model, mock_update, repo, mock_session):
    mock_query = MagicMock()
    mock_update.return_value.where.return_value.values.return_value = mock_query

    await repo.deactivate_token(b"hash")
    mock_session.execute.assert_called_once_with(mock_query)
