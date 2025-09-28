# /ai_rag_story_app/reset_password.py
import asyncio
import os
import getpass
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from dotenv import load_dotenv

# --- IMPORTANT ---
# This script must be run from the root of your project directory
# so that it can find the 'app' module and the '.env' file.
# ---

# Load environment variables from .env file
print("Loading environment variables from .env file...")
load_dotenv()

# We need to import the security context from the application
# This ensures we use the *exact same* hashing settings (argon2)
try:
    from app.core.security import get_password_hash
    print("Successfully imported password hashing function from the application.")
except ImportError as e:
    print("\n--- ERROR ---")
    print("Could not import the application's security module.")
    print("Please ensure you are running this script from the project's root directory.")
    print(f"Details: {e}")
    exit(1)

# --- Database Connection ---
# Construct the database URL from environment variables
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_HOST = os.getenv("POSTGRES_SERVER")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("POSTGRES_DB")

if not all([DB_USER, DB_PASSWORD, DB_HOST, DB_NAME]):
    print("\n--- ERROR ---")
    print("Database connection variables are missing in your .env file.")
    print("Please ensure POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_SERVER, and POSTGRES_DB are set.")
    exit(1)

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
print(f"Connecting to database: postgresql+asyncpg://{DB_USER}:********@{DB_HOST}:{DB_PORT}/{DB_NAME}")

async def reset_user_password():
    """Main function to handle the password reset process."""
    
    print("\n--- AI Story App: Manual Password Reset ---")
    
    # Get user input
    username_to_reset = input("Enter the username of the user to reset: ").strip()
    if not username_to_reset:
        print("Username cannot be empty. Aborting.")
        return

    new_password = getpass.getpass("Enter the new password: ")
    if not new_password:
        print("Password cannot be empty. Aborting.")
        return

    confirm_password = getpass.getpass("Confirm the new password: ")
    if new_password != confirm_password:
        print("Passwords do not match. Aborting.")
        return

    # Hash the new password using the app's function
    print(f"\nHashing new password for '{username_to_reset}' using argon2...")
    try:
        new_hashed_password = get_password_hash(new_password)
        print("Password hashed successfully.")
    except Exception as e:
        print(f"Error during password hashing: {e}")
        return

    # Connect to the database and update the user
    engine = create_async_engine(DATABASE_URL)
    async with engine.connect() as conn:
        async with conn.begin(): # Start a transaction
            # Check if user exists
            user_check_query = text("SELECT id FROM users WHERE username = :username")
            user_result = await conn.execute(user_check_query, {"username": username_to_reset})
            user = user_result.fetchone()

            if not user:
                print(f"\n--- ERROR ---")
                print(f"User '{username_to_reset}' not found in the database.")
                print("Aborting. No changes were made.")
                return

            # Update the password
            print(f"Updating password for user ID: {user.id}...")
            update_query = text(
                "UPDATE users SET hashed_password = :new_hash WHERE id = :user_id"
            )
            await conn.execute(
                update_query,
                {"new_hash": new_hashed_password, "user_id": user.id}
            )

    await engine.dispose()
    print("\n--- SUCCESS ---")
    print(f"Password for user '{username_to_reset}' has been reset successfully.")
    print("You can now log in with the new password.")


if __name__ == "__main__":
    try:
        asyncio.run(reset_user_password())
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")