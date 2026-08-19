import re

with open('tests/conftest.py', 'r') as f:
    content = f.read()

replacement = """
    print("Waiting for Postgres to be ready...")
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text
    import asyncio
    
    engine = create_async_engine("postgresql+asyncpg://test_user:test_password@localhost:5435/please_text_me_test_db")
    
    async def check_db():
        for _ in range(10):
            try:
                async with engine.connect() as conn:
                    await conn.execute(text("SELECT 1"))
                    return True
            except Exception:
                await asyncio.sleep(1)
        return False
        
    is_ready = asyncio.run(check_db())
    if not is_ready:
        print("Warning: Postgres did not become ready in time.")
"""

content = re.sub(
    r'    print\("Waiting for Postgres to be ready\."\)\n    time\.sleep\(3\) # Wait for db to accept connections',
    replacement.strip("\n"),
    content
)

with open('tests/conftest.py', 'w') as f:
    f.write(content)
