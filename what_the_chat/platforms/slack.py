"""Slack platform integration for fetching messages."""

from datetime import datetime
from typing import Dict, Tuple

from colorama import Fore, Style
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError


class SlackPlatform:
    """Slack platform integration for message fetching."""
    
    def __init__(self):
        self.user_mapping: Dict[str, str] = {}
    
    def fetch_messages(
        self, slack_token: str, channel_name: str, since_date: datetime
    ) -> Tuple[str, datetime]:
        """Fetch messages from a Slack channel since a specific date and format them as a human-readable chat history.

        Args:
            slack_token: Slack API token
            channel_name: Slack channel name
            since_date: Date to start fetching messages from

        Returns:
            tuple: (formatted_history, first_message_date)
        """
        print(
            f"\n{Fore.CYAN}→ Fetching messages from Slack channel {Fore.YELLOW}{channel_name}{Fore.CYAN} since {Fore.GREEN}{since_date.date()}{Style.RESET_ALL}"
        )

        # Initialize Slack client
        client = WebClient(token=slack_token)

        # Get channel ID from channel name
        try:
            # List all channels to find the one we want
            # include public and private channels
            public_result = client.conversations_list(types="public_channel")
            private_result = client.conversations_list(types="private_channel")
            channel_id = None
            channel_info = None
            for channel in public_result["channels"] + private_result["channels"]:
                if channel["name"] == channel_name:
                    channel_id = channel["id"]
                    channel_info = channel
                    break

            if not channel_id:
                print(
                    f"    {Fore.RED}Error: Channel {channel_name} not found{Style.RESET_ALL}"
                )
                return "", since_date

            print(f"    {Fore.GREEN}Found channel: {channel_info['name']}{Style.RESET_ALL}")

            # Create a human-readable chat history
            chat_history = []
            message_count = 0
            thread_count = 0
            print(
                f"    {Fore.CYAN}Fetching messages...{Style.RESET_ALL}", end="", flush=True
            )

            # Clear the user mapping cache for this fetch
            self.user_mapping = {}

            # Track the first message date
            first_message_date = None

            # Convert since_date to Unix timestamp
            since_timestamp = since_date.timestamp()

            # Fetch messages from the channel
            cursor = None
            has_more = True

            while has_more:
                try:
                    result = client.conversations_history(
                        channel=channel_id, oldest=since_timestamp, cursor=cursor, limit=100
                    )

                    messages = result["messages"]
                    has_more = result["has_more"]
                    cursor = result.get("response_metadata", {}).get("next_cursor")

                    for message in messages:
                        message_count += 1
                        if message_count % 100 == 0:
                            print(f"{Fore.CYAN}.{Style.RESET_ALL}", end="", flush=True)

                        # Skip messages without text
                        if "text" not in message:
                            continue

                        # Get message timestamp
                        message_timestamp = float(message["ts"])
                        message_date = datetime.fromtimestamp(message_timestamp)

                        # Update first message date if not set yet
                        if first_message_date is None:
                            first_message_date = message_date

                        # Get user info
                        user_id = message.get("user", "UNKNOWN")
                        username = "UNKNOWN"

                        if user_id != "UNKNOWN":
                            try:
                                user_info = client.users_info(user=user_id)
                                username = user_info["user"]["name"]
                                self.user_mapping[username] = user_id
                            except SlackApiError:
                                username = f"User_{user_id}"

                        # Format message
                        timestamp_str = message_date.strftime("%Y-%m-%d %H:%M:%S")
                        formatted_message = (
                            f"[{timestamp_str}] {username}: {message['text']}"
                        )

                        # Add message to chat history
                        chat_history.append(formatted_message)

                        # Check for thread replies
                        if "thread_ts" in message and message["thread_ts"] == message["ts"]:
                            # This is a thread parent message
                            thread_count += 1
                            print(f"\n    {Fore.MAGENTA}Found thread{Style.RESET_ALL}")

                            # Add thread header
                            chat_history.append("\n--- Thread ---")

                            # Fetch thread replies
                            thread_result = client.conversations_replies(
                                channel=channel_id, ts=message["ts"]
                            )

                            thread_messages = thread_result["messages"]
                            thread_message_count = 0

                            for thread_message in thread_messages[
                                1:
                            ]:  # Skip the parent message
                                thread_message_count += 1
                                if thread_message_count % 100 == 0:
                                    print(
                                        f"{Fore.CYAN}.{Style.RESET_ALL}", end="", flush=True
                                    )

                                # Skip messages without text
                                if "text" not in thread_message:
                                    continue

                                # Get thread message timestamp
                                thread_timestamp = float(thread_message["ts"])
                                thread_date = datetime.fromtimestamp(thread_timestamp)

                                # Get thread user info
                                thread_user_id = thread_message.get("user", "UNKNOWN")
                                thread_username = "UNKNOWN"

                                if thread_user_id != "UNKNOWN":
                                    try:
                                        thread_user_info = client.users_info(
                                            user=thread_user_id
                                        )
                                        thread_username = thread_user_info["user"]["name"]
                                        self.user_mapping[thread_username] = thread_user_id
                                    except SlackApiError:
                                        thread_username = f"User_{thread_user_id}"

                                # Format thread message
                                thread_timestamp_str = thread_date.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                                formatted_thread_message = f"[{thread_timestamp_str}] {thread_username}: {thread_message['text']}"

                                # Add thread message to chat history
                                chat_history.append(formatted_thread_message)

                            print(
                                f"\n    {Fore.GREEN}Processed {thread_message_count} messages in thread{Style.RESET_ALL}"
                            )
                            chat_history.append("--- End of Thread ---\n")

                except SlackApiError as e:
                    print(
                        f"\n    {Fore.RED}Error: Slack API error: {str(e)}{Style.RESET_ALL}"
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

            print(
                f"\n    {Fore.GREEN}Total messages scanned: {message_count}{Style.RESET_ALL}"
            )
            print(f"    {Fore.GREEN}Total threads scanned: {thread_count}{Style.RESET_ALL}")
            print(
                f"    {Fore.GREEN}Total unique users: {len(self.user_mapping)}{Style.RESET_ALL}"
            )

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

        except SlackApiError as e:
            print(f"\n    {Fore.RED}Error: Slack API error: {str(e)}{Style.RESET_ALL}")
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

    def get_user_mapping(self) -> Dict[str, str]:
        """Get the current user mapping dictionary."""
        return self.user_mapping.copy()
