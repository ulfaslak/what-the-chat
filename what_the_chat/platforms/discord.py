"""Discord platform integration for fetching messages and managing bots."""

from datetime import datetime
from typing import Dict, Tuple

import discord
from discord.ext import commands
from colorama import Fore, Style


class DiscordPlatform:
    """Discord platform integration for message fetching and bot management."""
    
    def __init__(self):
        self.user_mapping: Dict[str, str] = {}
    
    def create_bot(self) -> commands.Bot:
        """Create and configure a Discord bot instance."""
        intents = discord.Intents.default()
        intents.message_content = True
        return commands.Bot(command_prefix="!", intents=intents)
    
    async def fetch_messages(
        self, bot: commands.Bot, channel_id: int, since_date: datetime
    ) -> Tuple[str, datetime]:
        """Fetch messages from a Discord channel since a specific date and format them as a human-readable chat history.

        Args:
            bot: Discord bot instance
            channel_id: Discord channel ID
            since_date: Date to start fetching messages from

        Returns:
            tuple: (formatted_history, first_message_date)
        """
        print(
            f"\n{Fore.CYAN}→ Fetching messages from Discord channel {Fore.YELLOW}{channel_id}{Fore.CYAN} since {Fore.GREEN}{since_date.date()}{Style.RESET_ALL}"
        )

        channel = bot.get_channel(channel_id)
        if not channel:
            print(f"    {Fore.RED}Error: Channel {channel_id} not found{Style.RESET_ALL}")
            print(
                f"    {Fore.YELLOW}Available channels: {[ch.id for ch in bot.get_all_channels()]}{Style.RESET_ALL}"
            )
            return "", since_date

        print(f"    {Fore.GREEN}Found channel: {channel.name}{Style.RESET_ALL}")

        # Create a human-readable chat history
        chat_history = []
        message_count = 0
        thread_count = 0
        print(f"    {Fore.CYAN}Fetching messages...{Style.RESET_ALL}", end="", flush=True)

        # Clear the user mapping cache for this fetch
        self.user_mapping = {}

        # Track the first message date
        first_message_date = None

        try:
            # First, fetch messages from the main channel
            async for message in channel.history(limit=None, after=since_date):
                message_count += 1
                if message_count % 100 == 0:
                    print(f"{Fore.CYAN}.{Style.RESET_ALL}", end="", flush=True)

                # Update first message date if not set yet
                if first_message_date is None:
                    first_message_date = message.created_at

                # Store user mapping
                user_id = message.author.id
                username = message.author.name
                self.user_mapping[username] = user_id

                # Format each message with timestamp and author
                timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
                author = message.author.name

                # Add message to chat history
                chat_history.append(f"[{timestamp}] {author}: {message.content}")

                # Check if the message has a thread
                if hasattr(message, "thread") and message.thread:
                    thread = message.thread
                    thread_count += 1
                    print(
                        f"\n    {Fore.MAGENTA}Found thread: {thread.name}{Style.RESET_ALL}"
                    )

                    # Add thread header to chat history
                    chat_history.append(f"\n--- Thread: {thread.name} ---")

                    # Fetch messages from the thread
                    thread_message_count = 0
                    async for thread_message in thread.history(
                        limit=None, after=since_date
                    ):
                        thread_message_count += 1
                        if thread_message_count % 100 == 0:
                            print(f"{Fore.CYAN}.{Style.RESET_ALL}", end="", flush=True)

                        # Update first message date if not set yet
                        if first_message_date is None:
                            first_message_date = thread_message.created_at

                        # Store user mapping for thread messages
                        thread_user_id = thread_message.author.id
                        thread_username = thread_message.author.name
                        self.user_mapping[thread_username] = thread_user_id

                        # Format thread message
                        thread_timestamp = thread_message.created_at.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        thread_author = thread_message.author.name

                        # Add thread message to chat history
                        chat_history.append(
                            f"[{thread_timestamp}] {thread_author}: {thread_message.content}"
                        )

                    print(
                        f"\n    {Fore.GREEN}Processed {thread_message_count} messages in thread {thread.name}{Style.RESET_ALL}"
                    )
                    chat_history.append("--- End of Thread ---\n")

        except discord.Forbidden as e:
            print(
                f"\n    {Fore.RED}Error: Bot doesn't have permission to read message history: {str(e)}{Style.RESET_ALL}"
            )
            return "", since_date
        except discord.HTTPException as e:
            print(
                f"\n    {Fore.RED}Error: HTTP error while fetching messages: {str(e)}{Style.RESET_ALL}"
            )
            return "", since_date
        except Exception as e:
            print(
                f"\n    {Fore.RED}Error: Unexpected error while fetching messages: {str(e)}{Style.RESET_ALL}"
            )
            import traceback

            print(
                f"    {Fore.RED}Error Traceback: {traceback.format_exc()}{Style.RESET_ALL}"
            )
            return "", since_date

        print(f"\n    {Fore.GREEN}Total messages scanned: {message_count}{Style.RESET_ALL}")
        print(f"    {Fore.GREEN}Total threads scanned: {thread_count}{Style.RESET_ALL}")
        print(f"    {Fore.GREEN}Total unique users: {len(self.user_mapping)}{Style.RESET_ALL}")

        # If no messages were found, use the since_date
        if first_message_date is None:
            first_message_date = since_date
        else:
            print(
                f"    {Fore.GREEN}First message date: {first_message_date.date()}{Style.RESET_ALL}"
            )

        # Join all messages with newlines to create a single string
        formatted_history = "\n".join(chat_history)
        return formatted_history, first_message_date

    def get_user_mapping(self) -> Dict[str, str]:
        """Get the current user mapping dictionary."""
        return self.user_mapping.copy()
