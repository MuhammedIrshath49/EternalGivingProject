"""Admin command handlers for broadcasting messages"""

import logging
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import User, BroadcastMessage
from config import ADMIN_IDS
from bot.security import verify_critical_operation_allowed, log_critical_operation

logger = logging.getLogger(__name__)
router = Router()


class BroadcastStates(StatesGroup):
    """States for broadcast message flow"""
    waiting_for_message = State()


def is_admin(user_id: int) -> bool:
    """Check if user is an admin"""
    return user_id in ADMIN_IDS if ADMIN_IDS else False


@router.message(Command("broadcast"))
async def cmd_broadcast(message: Message, state: FSMContext):
    """Handle /broadcast command - Admin only"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ This command is only available to administrators.")
        return
    
    # Security check
    if not verify_critical_operation_allowed("broadcast"):
        await message.answer(
            "🔒 *Security Alert*\n\n"
            "Broadcast functionality is temporarily disabled due to security measures.\n"
            "Please check the security logs and contact the security team.",
            parse_mode="Markdown"
        )
        return
    
    log_critical_operation("broadcast_initiated", message.from_user.id, "Admin initiated broadcast")
    
    await state.set_state(BroadcastStates.waiting_for_message)
    await message.answer(
        "📢 *Broadcast Message*\n\n"
        "Please send the message you want to broadcast to all users.\n\n"
        "You can send:\n"
        "• Text messages\n"
        "• Photos with captions\n"
        "• Videos with captions\n"
        "• Documents\n\n"
        "Send /cancel to cancel the broadcast.",
        parse_mode="Markdown"
    )


@router.message(BroadcastStates.waiting_for_message, Command("cancel"))
async def cancel_broadcast(message: Message, state: FSMContext):
    """Cancel the broadcast"""
    await state.clear()
    await message.answer("❌ Broadcast cancelled.")


@router.message(BroadcastStates.waiting_for_message)
async def process_broadcast_message(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    """Process and send the broadcast message to all users"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ This command is only available to administrators.")
        return
    
    await state.clear()
    
    # Get all users
    try:
        result = await session.execute(select(User))
        users = result.scalars().all()
        
        if not users:
            await message.answer("No users found in the database.")
            return
        
        # Store broadcast message in database for tracking
        broadcast_msg = BroadcastMessage(
            admin_id=message.from_user.id,
            message_text=message.text or message.caption or "[Media]",
            telegram_message_id=message.message_id
        )
        session.add(broadcast_msg)
        await session.commit()
        
        # Send message to all users
        success_count = 0
        failed_count = 0
        
        progress_msg = await message.answer(
            f"📤 Broadcasting message to {len(users)} users...\n"
            f"✅ Success: 0\n"
            f"❌ Failed: 0"
        )
        
        for idx, user in enumerate(users):
            try:
                # Copy the message to each user
                if message.text:
                    sent_msg = await bot.send_message(
                        user.id,
                        message.text,
                        parse_mode=message.parse_mode
                    )
                elif message.photo:
                    sent_msg = await bot.send_photo(
                        user.id,
                        message.photo[-1].file_id,
                        caption=message.caption,
                        parse_mode=message.parse_mode
                    )
                elif message.video:
                    sent_msg = await bot.send_video(
                        user.id,
                        message.video.file_id,
                        caption=message.caption,
                        parse_mode=message.parse_mode
                    )
                elif message.document:
                    sent_msg = await bot.send_document(
                        user.id,
                        message.document.file_id,
                        caption=message.caption,
                        parse_mode=message.parse_mode
                    )
                else:
                    # Try to copy the message as-is
                    sent_msg = await message.copy_to(user.id)
                
                # Store the sent message ID for potential deletion later
                from database.models import BroadcastMessageRecipient
                recipient = BroadcastMessageRecipient(
                    broadcast_id=broadcast_msg.id,
                    user_id=user.id,
                    sent_message_id=sent_msg.message_id
                )
                session.add(recipient)
                
                success_count += 1
                
                # Update progress every 10 users
                if (idx + 1) % 10 == 0:
                    await progress_msg.edit_text(
                        f"📤 Broadcasting message to {len(users)} users...\n"
                        f"✅ Success: {success_count}\n"
                        f"❌ Failed: {failed_count}\n"
                        f"Progress: {idx + 1}/{len(users)}"
                    )
                
            except Exception as e:
                logger.error(f"Failed to send broadcast to user {user.id}: {e}")
                failed_count += 1
        
        await session.commit()
        
        # Final report
        await progress_msg.edit_text(
            f"✅ *Broadcast Complete*\n\n"
            f"Total users: {len(users)}\n"
            f"✅ Successfully sent: {success_count}\n"
            f"❌ Failed: {failed_count}\n\n"
            f"Broadcast ID: `{broadcast_msg.id}`\n"
            f"Use `/deletebroadcast {broadcast_msg.id}` to delete this broadcast from all users.",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error during broadcast: {e}")
        await session.rollback()
        await message.answer(
            "❌ An error occurred while broadcasting the message. Please check the logs."
        )


@router.message(Command("deletebroadcast"))
async def cmd_delete_broadcast(message: Message, session: AsyncSession, bot: Bot):
    """Delete a broadcast message from all users - Admin only"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ This command is only available to administrators.")
        return
    
    # Extract broadcast ID from command
    args = message.text.split()
    if len(args) < 2:
        await message.answer(
            "Usage: `/deletebroadcast <broadcast_id>`\n\n"
            "Example: `/deletebroadcast 123`",
            parse_mode="Markdown"
        )
        return
    
    try:
        broadcast_id = int(args[1])
    except ValueError:
        await message.answer("Invalid broadcast ID. Please provide a numeric ID.")
        return
    
    try:
        # Get the broadcast and its recipients
        from database.models import BroadcastMessageRecipient
        
        result = await session.execute(
            select(BroadcastMessage).where(BroadcastMessage.id == broadcast_id)
        )
        broadcast = result.scalar_one_or_none()
        
        if not broadcast:
            await message.answer(f"❌ Broadcast with ID {broadcast_id} not found.")
            return
        
        # Get all recipients
        result = await session.execute(
            select(BroadcastMessageRecipient).where(
                BroadcastMessageRecipient.broadcast_id == broadcast_id
            )
        )
        recipients = result.scalars().all()
        
        # Delete messages from all users
        deleted_count = 0
        failed_count = 0
        
        progress_msg = await message.answer(
            f"🗑️ Deleting broadcast from {len(recipients)} users...\n"
            f"✅ Deleted: 0\n"
            f"❌ Failed: 0"
        )
        
        for idx, recipient in enumerate(recipients):
            try:
                await bot.delete_message(recipient.user_id, recipient.sent_message_id)
                deleted_count += 1
                
                # Update progress every 10 deletions
                if (idx + 1) % 10 == 0:
                    await progress_msg.edit_text(
                        f"🗑️ Deleting broadcast from {len(recipients)} users...\n"
                        f"✅ Deleted: {deleted_count}\n"
                        f"❌ Failed: {failed_count}\n"
                        f"Progress: {idx + 1}/{len(recipients)}"
                    )
            except Exception as e:
                logger.error(f"Failed to delete message for user {recipient.user_id}: {e}")
                failed_count += 1
        
        # Mark broadcast as deleted
        broadcast.is_deleted = True
        await session.commit()
        
        # Final report
        await progress_msg.edit_text(
            f"✅ *Broadcast Deletion Complete*\n\n"
            f"Total recipients: {len(recipients)}\n"
            f"✅ Successfully deleted: {deleted_count}\n"
            f"❌ Failed: {failed_count}",
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Error deleting broadcast: {e}")
        await session.rollback()
        await message.answer(
            "❌ An error occurred while deleting the broadcast. Please check the logs."
        )


@router.message(Command("listbroadcasts"))
async def cmd_list_broadcasts(message: Message, session: AsyncSession):
    """List all broadcasts - Admin only"""
    if not is_admin(message.from_user.id):
        await message.answer("⛔ This command is only available to administrators.")
        return
    
    try:
        result = await session.execute(
            select(BroadcastMessage).order_by(BroadcastMessage.created_at.desc()).limit(20)
        )
        broadcasts = result.scalars().all()
        
        if not broadcasts:
            await message.answer("📭 No broadcasts found.")
            return
        
        text = "📋 *Recent Broadcasts*\n\n"
        
        for broadcast in broadcasts:
            status = "🗑️ Deleted" if broadcast.is_deleted else "✅ Active"
            text += (
                f"ID: `{broadcast.id}` - {status}\n"
                f"Date: {broadcast.created_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"Message: {broadcast.message_text[:50]}...\n\n"
            )
        
        text += "\nUse `/deletebroadcast <id>` to delete a broadcast."
        
        await message.answer(text, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Error listing broadcasts: {e}")
        await message.answer("❌ An error occurred while listing broadcasts.")
