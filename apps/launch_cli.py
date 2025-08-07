import argparse
import asyncio
import os
import signal
import sys
from datetime import datetime, timedelta

from colorama import Fore, Style, init
from dotenv import load_dotenv

from what_the_chat.summarize import (
    DiscordPlatform,
    SlackPlatform,
    SummarizationService,
    ChatService,
    replace_user_ids_with_names,
    standardize_user_references,
)

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv(override=True)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Fetch and summarize chat history from Discord or Slack channels"
    )
    parser.add_argument(
        "--since-days",
        type=int,
        required=True,
        help="Number of days to look back from today",
    )
    parser.add_argument(
        "--platform",
        choices=["discord", "slack"],
        default="discord",
        help="Platform to fetch messages from (default: discord)",
    )
    parser.add_argument(
        "--channel", required=True, help="Channel ID (Discord) or Channel name (Slack)"
    )
    parser.add_argument(
        "--model-source",
        choices=["local", "remote"],
        default="local",
        help="Source of the model to use for summarization (default: local)",
    )
    parser.add_argument(
        "--model",
        default="deepseek-r1-distill-qwen-7b",
        help="Name of the model to use (default: deepseek-r1-distill-qwen-7b)",
    )
    parser.add_argument(
        "--dump-file",
        nargs="?",
        const=".",
        help="Optional: Save summary to a markdown file. If no path is provided, saves to current directory.",
    )
    parser.add_argument(
        "--dump-collected-chat-history",
        action="store_true",
        help="Optional: Save the collected chat history to a file alongside the summary",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Optional: Start an interactive chat session with the collected conversation history",
    )
    return parser.parse_args()


def validate_environment(args):
    """Validate environment variables based on the arguments."""
    # Get OpenAI API key if using remote model
    if args.model_source == "remote":
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            print(
                f"{Fore.RED}Error: OPENAI_API_KEY environment variable is not set{Style.RESET_ALL}"
            )
            exit(1)

    # Get platform-specific tokens
    if args.platform == "discord":
        # Get Discord token
        discord_token = os.getenv("DISCORD_TOKEN")
        if not discord_token:
            print(
                f"{Fore.RED}Error: DISCORD_TOKEN environment variable is not set{Style.RESET_ALL}"
            )
            exit(1)

        try:
            channel_id = int(args.channel)
        except ValueError:
            print(f"{Fore.RED}Error: Invalid Discord channel ID{Style.RESET_ALL}")
            exit(1)

        return discord_token, channel_id
    else:  # Slack
        # Get Slack token
        slack_token = os.getenv("SLACK_TOKEN")
        if not slack_token:
            print(
                f"{Fore.RED}Error: SLACK_TOKEN environment variable is not set{Style.RESET_ALL}"
            )
            exit(1)

        return slack_token, args.channel


def save_files(
    processed_summary: str,
    standardized_history: str,
    args,
    platform: str,
    channel_name: str,
    first_date_str: str,
    today: str,
):
    """Save summary and optionally full history to files."""
    if args.dump_file is not None:
        # Create the output directory if it doesn't exist
        output_dir = (
            args.dump_file
            if os.path.isdir(args.dump_file)
            else os.path.dirname(args.dump_file)
        )
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # Determine the output path for the summary
        if os.path.isdir(args.dump_file):
            summary_filename = os.path.join(
                args.dump_file,
                f"{platform}_history_summary_{channel_name}_{first_date_str}_{today}.md",
            )
        else:
            summary_filename = args.dump_file

        # Save the summary
        with open(summary_filename, "w", encoding="utf-8") as f:
            f.write(processed_summary)
        print(f"\n{Fore.GREEN}→ Summary saved to {summary_filename}{Style.RESET_ALL}")

        # Save the full history if requested
        if args.dump_collected_chat_history:
            if os.path.isdir(args.dump_file):
                full_history_filename = os.path.join(
                    args.dump_file,
                    f"{platform}_history_{channel_name}_{first_date_str}_{today}.md",
                )
            else:
                full_history_filename = os.path.join(
                    os.path.dirname(args.dump_file),
                    f"{platform}_history_{channel_name}_{first_date_str}_{today}.md",
                )
            with open(full_history_filename, "w", encoding="utf-8") as f:
                f.write(standardized_history)
            print(
                f"{Fore.GREEN}→ Full chat history saved to {full_history_filename}{Style.RESET_ALL}"
            )
    else:
        # Print the summary to terminal
        print(f"\n{Fore.CYAN}{Style.BRIGHT}→ Generated Summary:{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        print(processed_summary)
        print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")


async def process_discord_channel(args, discord_token, channel_id, since_date):
    """Process a Discord channel."""
    # Create Discord platform with token
    platform = DiscordPlatform(discord_token)
    bot = platform.create_bot()

    @bot.event
    async def on_ready():
        print(f"{Fore.GREEN}{bot.user}{Fore.CYAN} is now running!{Style.RESET_ALL}")

        try:
            # Fetch messages from Discord
            chat_history, first_message_date = await platform.fetch_messages(
                bot, channel_id, since_date
            )

            if not chat_history:
                print(f"{Fore.RED}No messages found or error occurred{Style.RESET_ALL}")
                await bot.close()
                return

            # Get user mapping from the platform
            user_mapping = platform.get_user_mapping()

            # Process the messages
            await process_messages(
                chat_history,
                first_message_date,
                user_mapping,
                args,
                "discord",
                bot.get_channel(channel_id).name
                if bot.get_channel(channel_id)
                else str(channel_id),
                bot=bot  # Pass the bot instance for clean shutdown
            )

        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
            import traceback

            print(
                f"{Fore.RED}Error Traceback: {traceback.format_exc()}{Style.RESET_ALL}"
            )
            await bot.close()

    # Start the bot
    async with bot:
        await bot.start(discord_token)


async def process_slack_channel(args, slack_token, channel_name, since_date):
    """Process a Slack channel."""
    try:
        # Create Slack platform with token
        platform = SlackPlatform(slack_token)
        
        # Fetch messages from Slack
        chat_history, first_message_date = platform.fetch_messages_with_token(
            channel_name, since_date
        )

        if not chat_history:
            print(f"{Fore.RED}No messages found or error occurred{Style.RESET_ALL}")
            return

        # Get user mapping from the platform
        user_mapping = platform.get_user_mapping()

        # Process the messages
        await process_messages(
            chat_history, first_message_date, user_mapping, args, "slack", channel_name
        )

    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        import traceback

        print(f"{Fore.RED}Error Traceback: {traceback.format_exc()}{Style.RESET_ALL}")


async def process_messages(
    chat_history, first_message_date, user_mapping, args, platform, channel_name, bot=None
):
    """Process the fetched messages (common logic for both platforms)."""
    # Standardize user references
    standardized_history = standardize_user_references(chat_history, user_mapping)

    # Create filename based on channel, first message date, and today's date
    today = datetime.now().strftime("%Y-%m-%d")
    first_date_str = first_message_date.strftime("%Y-%m-%d")

    # Get API key if using remote models
    api_key = None
    if args.model_source == "remote":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print(f"{Fore.RED}Error: OPENAI_API_KEY environment variable is required for remote models{Style.RESET_ALL}")
            return

    # Generate summary
    summarizer = SummarizationService(args.model_source, args.model, api_key)
    summary = summarizer.generate_summary(standardized_history, user_mapping)

    # Post-process the summary to replace user IDs with usernames
    processed_summary = replace_user_ids_with_names(summary, user_mapping)

    # Save files or print summary
    save_files(
        processed_summary,
        standardized_history,
        args,
        platform,
        channel_name,
        first_date_str,
        today,
    )

    # Start interactive chat session if requested
    if args.chat:
        try:
            chat_service = ChatService(args.model_source, args.model, api_key)
            chat_service.start_interactive_session(standardized_history, user_mapping)
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}→ Chat session interrupted...{Style.RESET_ALL}")
        finally:
            # If we have a Discord bot, close it after the chat session
            if bot:
                print(f"{Fore.CYAN}→ Shutting down Discord bot...{Style.RESET_ALL}")
                try:
                    await bot.close()
                except Exception:
                    pass  # Ignore errors during shutdown


async def main():
    """Main entry point for the CLI application."""
    # Parse arguments
    args = parse_arguments()

    # Calculate the since_date based on the number of days to look back
    since_date = datetime.now() - timedelta(days=args.since_days)
    print(
        f"{Fore.CYAN}→ Looking back {Fore.YELLOW}{args.since_days}{Fore.CYAN} days from today ({Fore.GREEN}{since_date.date()}{Fore.CYAN}){Style.RESET_ALL}"
    )

    # Validate environment and get tokens/identifiers
    if args.platform == "discord":
        discord_token, channel_id = validate_environment(args)
        await process_discord_channel(args, discord_token, channel_id, since_date)
    else:  # Slack
        slack_token, channel_name = validate_environment(args)
        await process_slack_channel(args, slack_token, channel_name, since_date)


def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully."""
    print(f"\n{Fore.CYAN}→ Shutting down gracefully...{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Thanks for using What The Chat! 👋{Style.RESET_ALL}")
    sys.exit(0)


if __name__ == "__main__":
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n{Fore.CYAN}→ Application terminated by user{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Thanks for using What The Chat! 👋{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}Unexpected error: {str(e)}{Style.RESET_ALL}")
        sys.exit(1)
