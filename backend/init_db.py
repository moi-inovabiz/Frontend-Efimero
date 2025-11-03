"""
Database initialization script
Creates tables if they don't exist
"""
import asyncio
from app.core.database import init_db
# Import models to register them with SQLAlchemy Base
from app.models.db_models import UsuarioDB  # noqa: F401

async def main():
    print("🔄 Initializing database...")
    await init_db()
    print("✅ Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(main())
