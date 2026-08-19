import re

with open('tests/unit/infrastructure/test_user_repository.py', 'r') as f:
    content = f.read()

# Remove imports related to fixtures we moved
content = re.sub(r'from unittest\.mock import AsyncMock, MagicMock, patch\n\n', 'from unittest.mock import MagicMock\n\n', content)
content = re.sub(r'from sqlalchemy\.ext\.asyncio import AsyncSession\n\n', '', content)
content = re.sub(r'from src\.domain\.entities\.user import User\n', '', content)

# Remove fixtures
content = re.sub(r'@pytest\.fixture\ndef mock_session\(\):\n    return AsyncMock\(spec=AsyncSession\)\n\n\n', '', content)
content = re.sub(r'@pytest\.fixture\ndef mock_db_user\(\):\n    return MagicMock\(\)\n\n\n', '', content)
content = re.sub(r'@pytest\.fixture\ndef mock_user_instance\(\):\n    return MagicMock\(spec=User\)\n\n\n', '', content)

# Remove @patch decorators and update function signatures
content = re.sub(r'@patch\("src\.infrastructure\.repositories\.user\.insert"\)\n@patch\("src\.infrastructure\.repositories\.user\.User\.model_validate"\)\n', '', content)
content = re.sub(r'@patch\("src\.infrastructure\.repositories\.user\.select"\)\n@patch\("src\.infrastructure\.repositories\.user\.User\.model_validate"\)\n', '', content)
content = re.sub(r'@patch\("src\.infrastructure\.repositories\.user\.select"\)\n', '', content)

with open('tests/unit/infrastructure/test_user_repository.py', 'w') as f:
    f.write(content)
