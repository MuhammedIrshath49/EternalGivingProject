"""Security module for monitoring and protecting critical bot functions"""

import logging
import hashlib
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List
from datetime import datetime
from config import ADMIN_IDS

logger = logging.getLogger(__name__)

# Security configuration
KILL_SWITCH_ACTIVE = False
KILL_SWITCH_FILE = ".killswitch"

# Email configuration for alerts (set via environment variables)
SECURITY_EMAIL_ENABLED = os.getenv("SECURITY_EMAIL_ENABLED", "false").lower() == "true"
SECURITY_ALERT_EMAILS = os.getenv("SECURITY_ALERT_EMAILS", "").split(",")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", SMTP_USERNAME)

# Critical files to monitor for unauthorized changes
CRITICAL_FILES = [
    "bot/handlers/misc.py",  # Contains donation handlers
    "database/models.py",  # Database schema
    "config.py",  # Configuration
    "main.py",  # Main bot file
]

# Store file hashes for integrity checking
FILE_HASHES = {}


def calculate_file_hash(filepath: str) -> str:
    """Calculate SHA256 hash of a file"""
    try:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        logger.warning(f"File not found for hashing: {filepath}")
        return ""
    except Exception as e:
        logger.error(f"Error calculating hash for {filepath}: {e}")
        return ""


def initialize_file_hashes():
    """Initialize hashes for critical files"""
    global FILE_HASHES
    logger.info("Initializing file integrity monitoring...")
    
    for filepath in CRITICAL_FILES:
        file_hash = calculate_file_hash(filepath)
        if file_hash:
            FILE_HASHES[filepath] = file_hash
            logger.info(f"Monitoring: {filepath} (hash: {file_hash[:16]}...)")
    
    logger.info(f"Monitoring {len(FILE_HASHES)} critical files")


def check_file_integrity() -> List[str]:
    """Check if any critical files have been modified
    
    Returns:
        List of modified files
    """
    modified_files = []
    
    for filepath, original_hash in FILE_HASHES.items():
        current_hash = calculate_file_hash(filepath)
        if current_hash and current_hash != original_hash:
            modified_files.append(filepath)
            logger.warning(f"⚠️ SECURITY ALERT: File modified: {filepath}")
            logger.warning(f"   Original hash: {original_hash[:16]}...")
            logger.warning(f"   Current hash:  {current_hash[:16]}...")
    
    return modified_files


def send_security_alert(subject: str, message: str):
    """Send security alert email to administrators"""
    if not SECURITY_EMAIL_ENABLED or not SECURITY_ALERT_EMAILS:
        logger.warning("Security email alerts are disabled or no recipient emails configured")
        return
    
    try:
        msg = MIMEMultipart()
        msg['From'] = SMTP_FROM_EMAIL
        msg['To'] = ", ".join(SECURITY_ALERT_EMAILS)
        msg['Subject'] = f"🚨 ROM PeerBot Security Alert: {subject}"
        
        body = f"""
ROM PeerBot Security Alert
==========================

Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Alert Type: {subject}

{message}

This is an automated security alert from ROM PeerBot.
Please investigate immediately.

---
Rose of Madinah Institute
ROM PeerBot Security System
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        text = msg.as_string()
        server.sendmail(SMTP_FROM_EMAIL, SECURITY_ALERT_EMAILS, text)
        server.quit()
        
        logger.info(f"Security alert email sent to {len(SECURITY_ALERT_EMAILS)} recipients")
        
    except Exception as e:
        logger.error(f"Failed to send security alert email: {e}")


def activate_kill_switch(reason: str = "Unauthorized code changes detected"):
    """Activate the kill switch to stop critical bot functions"""
    global KILL_SWITCH_ACTIVE
    
    logger.critical(f"🚨 KILL SWITCH ACTIVATED: {reason}")
    KILL_SWITCH_ACTIVE = True
    
    # Create kill switch file
    try:
        with open(KILL_SWITCH_FILE, "w") as f:
            f.write(f"Kill switch activated at {datetime.now()}\n")
            f.write(f"Reason: {reason}\n")
        logger.info(f"Kill switch file created: {KILL_SWITCH_FILE}")
    except Exception as e:
        logger.error(f"Failed to create kill switch file: {e}")
    
    # Send security alert
    message = f"""
KILL SWITCH ACTIVATED

Reason: {reason}

Critical bot functions have been disabled to prevent potential security breaches.

The following actions are now blocked:
- Donation processing (/amaljariah, /supportnmsi)
- Standing instruction setup
- Broadcast messages

To deactivate the kill switch:
1. Investigate the security alert
2. Verify the integrity of all code
3. Remove the file: {KILL_SWITCH_FILE}
4. Restart the bot

DO NOT deactivate the kill switch until you have verified that the system is secure.
    """
    
    send_security_alert("Kill Switch Activated", message)


def check_kill_switch() -> bool:
    """Check if kill switch is active"""
    global KILL_SWITCH_ACTIVE
    
    # Check for kill switch file
    if os.path.exists(KILL_SWITCH_FILE):
        KILL_SWITCH_ACTIVE = True
        return True
    
    return KILL_SWITCH_ACTIVE


def deactivate_kill_switch():
    """Deactivate the kill switch (admin only)"""
    global KILL_SWITCH_ACTIVE
    
    logger.warning("Kill switch deactivated by admin")
    KILL_SWITCH_ACTIVE = False
    
    # Remove kill switch file
    try:
        if os.path.exists(KILL_SWITCH_FILE):
            os.remove(KILL_SWITCH_FILE)
            logger.info(f"Kill switch file removed: {KILL_SWITCH_FILE}")
    except Exception as e:
        logger.error(f"Failed to remove kill switch file: {e}")
    
    send_security_alert("Kill Switch Deactivated", "The kill switch has been manually deactivated by an administrator.")


async def periodic_security_check():
    """Periodic security check to be run by scheduler"""
    logger.debug("Running periodic security check...")
    
    # Check file integrity
    modified_files = check_file_integrity()
    
    if modified_files:
        logger.critical(f"🚨 UNAUTHORIZED CODE CHANGES DETECTED in {len(modified_files)} files!")
        
        # Build alert message
        files_list = "\n".join([f"- {f}" for f in modified_files])
        message = f"""
UNAUTHORIZED CODE CHANGES DETECTED

The following critical files have been modified:
{files_list}

This could indicate:
- Unauthorized access to the server
- Malicious code injection
- Accidental deployment of unverified code

The kill switch has been automatically activated to protect users and data.
        """
        
        # Activate kill switch
        activate_kill_switch("Unauthorized code changes detected")
        
        # Send alert
        send_security_alert("Unauthorized Code Changes", message)
        
        return False
    
    logger.debug("Security check passed - no unauthorized changes detected")
    return True


def verify_critical_operation_allowed(operation: str) -> bool:
    """Verify that a critical operation is allowed to proceed
    
    Args:
        operation: Name of the operation (e.g., 'donation', 'broadcast')
    
    Returns:
        True if operation is allowed, False if blocked by kill switch
    """
    if check_kill_switch():
        logger.warning(f"🚨 BLOCKED: {operation} operation prevented by active kill switch")
        return False
    
    return True


def log_critical_operation(operation: str, user_id: int, details: str = ""):
    """Log critical operations for audit trail"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_message = f"[CRITICAL OP] {timestamp} | Operation: {operation} | User: {user_id} | Details: {details}"
    logger.info(log_message)
    
    # Optionally write to a separate audit log file
    try:
        with open("security_audit.log", "a") as f:
            f.write(log_message + "\n")
    except Exception as e:
        logger.error(f"Failed to write to audit log: {e}")
