from src.core.utils.hash import hash_token

def test_hash_token_returns_bytes():
    token = "test_token_123"
    result = hash_token(token)
    assert isinstance(result, bytes)

def test_hash_token_is_deterministic():
    token = "test_token_123"
    assert hash_token(token) == hash_token(token)

def test_hash_token_differs_for_different_inputs():
    assert hash_token("token1") != hash_token("token2")
