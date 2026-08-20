from unittest.mock import patch

import pytest

from src.domain.dtos.user import UserCreateDatabaseDTO
from src.infrastructure.repositories.user import SQLAlchemyUserRepository


@pytest.fixture
def mock_select():
    with patch("src.infrastructure.repositories.user.select") as mock:
        yield mock


@pytest.fixture
def mock_insert():
    with patch("src.infrastructure.repositories.user.insert") as mock:
        yield mock


@pytest.fixture
def mock_model_validate():
    with patch("src.infrastructure.repositories.user.User.model_validate") as mock:
        yield mock


@pytest.fixture
def repo(mock_session):
    return SQLAlchemyUserRepository(session=mock_session)


@pytest.mark.asyncio
async def test_user_repo_create(
    mock_model_validate, mock_insert, repo, mock_session, mock_query, mock_result, mock_db_model, mock_domain_model
):
    mock_model_validate.return_value = mock_domain_model
    mock_insert.return_value.values.return_value.returning.return_value = mock_query

    mock_result.unique.return_value.scalar_one.return_value = mock_db_model

    user_data = UserCreateDatabaseDTO(
        username="Venya", email="axel@harlem.hui", password_hash=b"diss_on_windows", public_bundle={}, vault={}
    )

    result = await repo.create(user_data)

    assert result is mock_domain_model
    mock_session.execute.assert_called_once_with(mock_query)
    mock_model_validate.assert_called_once_with(mock_db_model)


@pytest.mark.asyncio
async def test_user_repo_get_by_email_found(
    mock_model_validate, mock_select, repo, mock_session, mock_query, mock_result, mock_db_model, mock_domain_model
):
    mock_model_validate.return_value = mock_domain_model
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result.scalar_one_or_none.return_value = mock_db_model

    result = await repo.get_by_email("axel@harlem.hui")

    assert result is mock_domain_model
    mock_session.execute.assert_called_once_with(mock_query)
    mock_model_validate.assert_called_once_with(mock_db_model)


@pytest.mark.asyncio
async def test_user_repo_get_by_email_not_found(mock_select, repo, mock_session, mock_query, mock_result):
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result.scalar_one_or_none.return_value = None

    result = await repo.get_by_email("axel@harlem.hui")

    assert result is None
    mock_session.execute.assert_called_once_with(mock_query)


@pytest.mark.asyncio
async def test_user_repo_get_by_username_found(
    mock_model_validate, mock_select, repo, mock_session, mock_query, mock_result, mock_db_model, mock_domain_model
):
    mock_model_validate.return_value = mock_domain_model
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result.scalar_one_or_none.return_value = mock_db_model

    result = await repo.get_by_username("Venya")

    assert result is mock_domain_model
    mock_session.execute.assert_called_once_with(mock_query)
    mock_model_validate.assert_called_once_with(mock_db_model)


@pytest.mark.asyncio
async def test_user_repo_get_by_username_not_found(mock_select, repo, mock_session, mock_query, mock_result):
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result.scalar_one_or_none.return_value = None

    result = await repo.get_by_username("Venya")

    assert result is None
    mock_session.execute.assert_called_once_with(mock_query)


@pytest.mark.asyncio
async def test_user_repo_get_by_id_found(
    mock_model_validate, mock_select, repo, mock_session, mock_query, mock_result, mock_db_model, mock_domain_model
):
    mock_model_validate.return_value = mock_domain_model
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result.scalar_one_or_none.return_value = mock_db_model

    result = await repo.get_by_id(1)

    assert result is mock_domain_model
    mock_session.execute.assert_called_once_with(mock_query)
    mock_model_validate.assert_called_once_with(mock_db_model)


@pytest.mark.asyncio
async def test_user_repo_get_by_id_not_found(mock_select, repo, mock_session, mock_query, mock_result):
    mock_select.return_value.filter_by.return_value = mock_query

    mock_result.scalar_one_or_none.return_value = None

    result = await repo.get_by_id(1)

    assert result is None
    mock_session.execute.assert_called_once_with(mock_query)


@pytest.mark.asyncio
async def test_user_repo_get_all(
    mock_model_validate, mock_select, repo, mock_session, mock_query, mock_result, mock_db_model, mock_domain_model
):
    mock_model_validate.return_value = mock_domain_model
    mock_select.return_value = mock_query

    mock_result.unique.return_value.scalars.return_value.all.return_value = [
        mock_db_model,
        mock_db_model,
    ]

    result = await repo.get_all()

    assert result == [mock_domain_model, mock_domain_model]
    mock_session.execute.assert_called_once_with(mock_query)
    assert mock_model_validate.call_count == 2

