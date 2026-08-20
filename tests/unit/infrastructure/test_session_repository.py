from unittest.mock import MagicMock, patch

import pytest

from src.domain.entities.session import Session
from src.infrastructure.repositories.session import SQLAlchemySessionRepository


@pytest.fixture
def repo(mock_session):
    return SQLAlchemySessionRepository(session=mock_session)


@pytest.fixture
def mock_insert():
    with patch("src.infrastructure.repositories.session.insert") as mock:
        yield mock


@pytest.fixture
def mock_select():
    with patch("src.infrastructure.repositories.session.select") as mock:
        yield mock


@pytest.fixture
def mock_update():
    with patch("src.infrastructure.repositories.session.update") as mock:
        yield mock


@pytest.fixture
def mock_model_validate():
    with patch("src.infrastructure.repositories.session.Session.model_validate") as mock:
        yield mock


@pytest.fixture
def mock_session_model():
    with patch("src.infrastructure.repositories.session.Session") as mock:
        yield mock


@pytest.mark.asyncio
async def test_session_repo_create(
    mock_model_validate, mock_insert, repo, mock_session, mock_query, mock_result, mock_db_model, mock_domain_model
):
    mock_model_validate.return_value = mock_domain_model
    mock_insert.return_value.values.return_value.returning.return_value = mock_query

    mock_result.unique.return_value.scalar_one.return_value = mock_db_model

    session_data = MagicMock(spec=Session)
    session_data.model_dump.return_value = {"id": 1, "is_active": True}
    session_data.auth_token_hash = b"hash"

    result = await repo.create(session_data)

    assert result is mock_domain_model
    mock_session.execute.assert_called_once_with(mock_query)
    mock_model_validate.assert_called_once_with(mock_db_model)


@pytest.mark.asyncio
async def test_session_repo_get_by_hash_found(
    mock_model_validate, mock_select, repo, mock_session, mock_query, mock_result, mock_db_model, mock_domain_model
):
    mock_model_validate.return_value = mock_domain_model
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result.scalar_one_or_none.return_value = mock_db_model

    result = await repo.get_by_hash(b"hash")

    assert result is mock_domain_model
    mock_session.execute.assert_called_once_with(mock_query)
    mock_model_validate.assert_called_once_with(mock_db_model)


@pytest.mark.asyncio
async def test_session_repo_get_by_hash_not_found(mock_select, repo, mock_session, mock_query, mock_result):
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result.scalar_one_or_none.return_value = None

    result = await repo.get_by_hash(b"hash")

    assert result is None
    mock_session.execute.assert_called_once_with(mock_query)


@pytest.mark.asyncio
async def test_session_repo_deactivate_token(mock_session_model, mock_update, repo, mock_session, mock_query):
    mock_update.return_value.where.return_value.values.return_value = mock_query

    await repo.deactivate_token(b"hash")
    mock_session.execute.assert_called_once_with(mock_query)
