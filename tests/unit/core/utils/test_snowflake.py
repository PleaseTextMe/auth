from src.core.utils.snowflake import generate_snowflake_id


def test_generate_snowflake_id_returns_int():
    result = generate_snowflake_id()
    assert isinstance(result, int)


def test_generate_snowflake_id_is_unique():
    id1 = generate_snowflake_id()
    id2 = generate_snowflake_id()
    assert id1 != id2
