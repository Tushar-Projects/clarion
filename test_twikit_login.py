import asyncio
import os
from twikit import Client
from dotenv import load_dotenv  # Add support for .env files

# Load environment variables from .env file
load_dotenv()

async def main():
    client = Client('en-US')

    try:
        # Check if the session file exists
        session_file = 'twitter_session.json'
        if os.path.exists(session_file):
            print("ℹ️ Loading session cookies...")
            result = client.load_cookies(session_file)  # Removed `await` if `load_cookies` is not async
            if asyncio.iscoroutine(result):  # Check if the result is a coroutine
                await result
            print("✅ Cookies loaded successfully.")
        else:
            print(f"❌ Session file '{session_file}' not found. Please log in to create a session.")

        # Check if the client is authenticated
        if hasattr(client, "is_authenticated") and client.is_authenticated:
            print("✅ Client is authenticated.")
        else:
            print("❌ Client is not authenticated. Attempting manual login...")

            # Manual login fallback
            TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
            TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")

            if not TWITTER_USERNAME or not TWITTER_PASSWORD:
                raise Exception(
                    "Missing Twitter credentials in environment variables. "
                    "Set TWITTER_USERNAME and TWITTER_PASSWORD in your environment or a .env file."
                )

            await client.login(
                auth_info_1=TWITTER_USERNAME,
                password=TWITTER_PASSWORD
            )
            await client.save_cookies(session_file)
            print("✅ Manual login successful. Session cookies saved.")

        # Optional: Check user information if `user_me` exists
        if hasattr(client, "user_me"):
            me = await client.user_me()
            print("✅ Logged in as:", me.username)
        else:
            print("⚠️ `user_me` method not found in the Client class. Verify the `twikit` library version.")

    except Exception as e:
        print("❌ Error during login check:", e)

asyncio.run(main())
