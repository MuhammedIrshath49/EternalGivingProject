"""
Database migration script to add broadcast tables
Run this after updating the models
"""

import asyncio
import logging
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from config import DATABASE_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_broadcast_tables():
    """Create broadcast-related tables"""
    logger.info("Creating broadcast tables...")
    
    engine = create_async_engine(DATABASE_URL)
    
    async with engine.begin() as conn:
        # Create BroadcastMessage table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS broadcast_messages (
                id BIGSERIAL PRIMARY KEY,
                admin_id BIGINT NOT NULL,
                message_text VARCHAR(4096),
                telegram_message_id BIGINT,
                is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        logger.info("✅ Created broadcast_messages table")
        
        # Create BroadcastMessageRecipient table
        await conn.execute(text("""
            CREATE TABLE IF NOT EXISTS broadcast_message_recipients (
                id BIGSERIAL PRIMARY KEY,
                broadcast_id BIGINT NOT NULL REFERENCES broadcast_messages(id) ON DELETE CASCADE,
                user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                sent_message_id BIGINT,
                created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        """))
        logger.info("✅ Created broadcast_message_recipients table")
        
        # Create indexes for better performance
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_broadcast_recipients_broadcast_id 
            ON broadcast_message_recipients(broadcast_id)
        """))
        
        await conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_broadcast_recipients_user_id 
            ON broadcast_message_recipients(user_id)
        """))
        
        logger.info("✅ Created indexes")
    
    logger.info("✅ Broadcast tables migration completed successfully")


async def main():
    """Main migration function"""
    engine = None
    try:
        await create_broadcast_tables()
        logger.info("🎉 Migration completed successfully!")
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
