"""
Database migration script for new donation features
Run this script to add the new tables and columns
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.db import engine, Base
from database.models import User, UserSettings, Donation, StandingInstruction
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def run_migration():
    """Create all database tables"""
    try:
        logger.info("Starting database migration...")
        
        async with engine.begin() as conn:
            # Create all tables defined in models
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Migration completed successfully!")
        logger.info("New tables created:")
        logger.info("  - donations")
        logger.info("  - standing_instructions")
        logger.info("Updated tables:")
        logger.info("  - user_settings (added friday_khutbah column)")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    print("=" * 60)
    print("ROM PeerBot - Database Migration")
    print("=" * 60)
    print("\nThis will create/update the following database objects:")
    print("  • donations table")
    print("  • standing_instructions table")
    print("  • friday_khutbah column in user_settings")
    print("\n⚠️  Warning: Ensure you have backed up your database!")
    print("=" * 60)
    
    response = input("\nProceed with migration? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        asyncio.run(run_migration())
    else:
        print("Migration cancelled.")
