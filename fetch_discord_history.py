import os
import asyncio
import argparse
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv

import discord
from discord.ext import commands
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

# Load environment variables
load_dotenv(override=True)

# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Fetch Discord chat history and save to file"
)
parser.add_argument("--since", required=True, help="Start date in YYYY-MM-DD format")
parser.add_argument("--channel", required=True, help="Discord channel ID")
parser.add_argument(
    "--summarize", action="store_true", help="Generate a summary of the chat history"
)
args = parser.parse_args()

# Validate and parse the date
try:
    since_date = datetime.strptime(args.since, "%Y-%m-%d")
except ValueError:
    print("Error: Invalid date format. Please use YYYY-MM-DD")
    exit(1)

# Get channel ID
try:
    channel_id = int(args.channel)
except ValueError:
    print("Error: Invalid channel ID")
    exit(1)

# Get Discord token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
if not DISCORD_TOKEN:
    print("Error: DISCORD_TOKEN environment variable is not set")
    exit(1)

# Get OpenAI API key if summarization is requested
if args.summarize:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        print(
            "Error: OPENAI_API_KEY environment variable is not set (required for summarization)"
        )
        exit(1)

# Initialize Discord client with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# User mapping cache
user_mapping = {}


async def fetch_discord_messages(
    channel_id: int, since_date: datetime
) -> tuple[str, datetime]:
    """Fetch messages from a Discord channel since a specific date and format them as a human-readable chat history.

    Returns:
        tuple: (formatted_history, first_message_date)
    """
    print(f"\nFetching messages from channel {channel_id} since {since_date.date()}")

    channel = bot.get_channel(channel_id)
    if not channel:
        print(f"Error: Channel {channel_id} not found")
        print(f"Available channels: {[ch.id for ch in bot.get_all_channels()]}")
        return "", since_date

    print(f"Found channel: {channel.name}")

    # Create a human-readable chat history
    chat_history = []
    message_count = 0
    thread_count = 0
    print("Fetching messages...", end="", flush=True)

    # Clear the user mapping cache for this fetch
    global user_mapping
    user_mapping = {}

    # Track the first message date
    first_message_date = None

    try:
        # First, fetch messages from the main channel
        async for message in channel.history(limit=None, after=since_date):
            message_count += 1
            if message_count % 100 == 0:
                print(".", end="", flush=True)

            # Update first message date if not set yet
            if first_message_date is None:
                first_message_date = message.created_at

            # Store user mapping
            user_id = message.author.id
            username = message.author.name
            user_mapping[username] = user_id

            # Format each message with timestamp and author
            timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")
            author = message.author.name

            # Add message to chat history
            chat_history.append(f"[{timestamp}] {author}: {message.content}")

            # Check if the message has a thread
            if hasattr(message, "thread") and message.thread:
                thread = message.thread
                thread_count += 1
                print(f"\nFound thread: {thread.name}")

                # Add thread header to chat history
                chat_history.append(f"\n--- Thread: {thread.name} ---")

                # Fetch messages from the thread
                thread_message_count = 0
                async for thread_message in thread.history(
                    limit=None, after=since_date
                ):
                    thread_message_count += 1
                    if thread_message_count % 100 == 0:
                        print(".", end="", flush=True)

                    # Update first message date if not set yet
                    if first_message_date is None:
                        first_message_date = thread_message.created_at

                    # Store user mapping for thread messages
                    thread_user_id = thread_message.author.id
                    thread_username = thread_message.author.name
                    user_mapping[thread_username] = thread_user_id

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
                    f"\nProcessed {thread_message_count} messages in thread {thread.name}"
                )
                chat_history.append("--- End of Thread ---\n")

    except discord.Forbidden as e:
        print(f"\nError: Bot doesn't have permission to read message history: {str(e)}")
        return "", since_date
    except discord.HTTPException as e:
        print(f"\nError: HTTP error while fetching messages: {str(e)}")
        return "", since_date
    except Exception as e:
        print(f"\nError: Unexpected error while fetching messages: {str(e)}")
        import traceback

        print(f"Error Traceback: {traceback.format_exc()}")
        return "", since_date

    print(f"\nTotal messages scanned: {message_count}")
    print(f"Total threads scanned: {thread_count}")
    print(f"Total unique users: {len(user_mapping)}")

    # If no messages were found, use the since_date
    if first_message_date is None:
        first_message_date = since_date
    else:
        print(f"First message date: {first_message_date.date()}")

    # Join all messages with newlines to create a single string
    formatted_history = "\n".join(chat_history)
    return formatted_history, first_message_date


def standardize_user_references(chat_history: str) -> str:
    """Standardize user references in the chat history by replacing usernames with consistent IDs."""
    # Create a mapping of usernames to their IDs
    username_to_id = {
        username: f"<@{user_id}>" for username, user_id in user_mapping.items()
    }

    # Replace usernames with their ID mentions
    standardized_history = chat_history
    for username, id_mention in username_to_id.items():
        # Replace username in the format [timestamp] username: message
        standardized_history = standardized_history.replace(
            f"{username}", f"{id_mention}"
        )

    return standardized_history


def replace_user_ids_with_names(summary: str) -> str:
    """Replace Discord user IDs with actual usernames in the summary."""
    # Create a mapping of user IDs to usernames
    id_to_username = {
        f"<@{user_id}>": username for username, user_id in user_mapping.items()
    }

    # Replace user IDs with usernames
    processed_summary = summary
    for id_mention, username in id_to_username.items():
        processed_summary = processed_summary.replace(id_mention, username)

    return processed_summary


def generate_summary(chat_history: str) -> str:
    """Generate a summary of the chat history using OpenAI."""
    print("\nGenerating summary...")

    try:
        # Use LangChain to generate a summary with GPT-4 Turbo
        llm = ChatOpenAI(model="gpt-4-turbo", temperature=0)

        # Create the system prompt
        system_prompt = """
You are an expert summarizer for PyMC Labs, specializing in internal Discord chat related to consulting projects involving Bayesian modeling.
Your task is to read a sequence of messages and generate a clear, structured summary that captures the project's current state.

First, determine the time span covered by the chat messages you receive:
	•	If the messages span 0–2 days, produce a Project Event Update.
	•	If the messages span 3–6 days, produce a Periodical Digest.
	•	If the messages span 7 or more days, produce a Full Project Status Summary.

⸻

Instructions for a Project Event Update (0–2 days):
	•	Focus on what was done, what remains open, and immediate actionables.
	•	Capture individual contributions: who did or said what.
	•	Highlight any assumptions, modeling choices, data sources, or constraints discussed.
	•	Flag anything time-sensitive or urgent.
	•	Write in bullet points, grouped under clear headings like "Completed", "Open Actions", "Contributors", "Notes".
	•	Suitable for project manager who wants a daily digest.


Instructions for a Periodical Digest (3–6 days):
	•	Focus on trends, major developments, and overall project movement.
	•	Summarize key achievements and broader tasks or challenges.
	•	Group contributions by theme or workstream rather than by individual post.
	•	Note general roles only if important for context.
	•	Identify any emerging risks, open technical questions, or important strategic discussions.
	•	Keep it compact but higher-level, suitable for someone catching up after a few days away.

Instructions for a Full Project Status Summary (7+ days):
	•	Provide a comprehensive overview, blending a timeline of major actions with a strategic status view.
    •	Answer first the question: "What is this {{project/workshop/etc}} about?" (infer what it actually is from the chat history, and ask the right question).
	•	Then highlight:
	•	Completed tasks and milestones.
	•	Outstanding tasks and blocking issues.
	•	Key contributions and who made them.
	•	Infer roles where possible (e.g., project lead, technical expert, client).
	•	Critical modeling assumptions, data challenges, or client interactions.
	•	Any risks or open technical uncertainties.
	•	Organize in clear sections and bullet points.
	•	Aim to make the summary self-contained, so a team member unfamiliar with recent details can quickly understand the state of the project.
	•	Suitable for new joiners who needs to gain an overview of the project, as well as insight that will allow then to contribute effectively.

⸻

General Writing Instructions (all cases):
	•	Maintain a professional, internal tone appropriate for project management updates.
	•	Be specific but brief; avoid unnecessary commentary.
	•	Omit sections if not applicable (e.g., if no urgent items, don't include an "Urgent" section).
	•	Use clear headings and bullet points for readability.
    •	Use markdown formatting for bullet points and headings.
    •	Refer to users, not by their names but by their IDs (like <@123456789012345678>).
"""

        # Create the prompt template
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                (
                    "human",
                    "Here is the Discord chat history to summarize: {chat_history}",
                ),
            ]
        )

        # Create the chain
        chain = prompt | llm

        # Invoke the chain
        result = chain.invoke({"chat_history": chat_history})

        print("Summary generated successfully")
        return result.content
    except Exception as e:
        print(f"Error generating summary: {str(e)}")
        import traceback

        print(f"Error Traceback: {traceback.format_exc()}")
        return f"Error generating summary: {str(e)}"


@bot.event
async def on_ready():
    print(f"{bot.user} is now running!")

    try:
        # Fetch messages
        chat_history, first_message_date = await fetch_discord_messages(
            channel_id, since_date
        )

        if not chat_history:
            print("No messages found or error occurred")
            await bot.close()
            return

        # Standardize user references
        standardized_history = standardize_user_references(chat_history)

        # Create filename based on channel, first message date, and today's date
        channel = bot.get_channel(channel_id)
        channel_name = channel.name if channel else str(channel_id)
        today = datetime.now().strftime("%Y-%m-%d")
        first_date_str = first_message_date.strftime("%Y-%m-%d")

        # Determine if we're generating a summary
        prefix = "discord_history_summary" if args.summarize else "discord_history"
        filename = f"{prefix}_{channel_name}_{first_date_str}_{today}.txt"

        # Generate summary if requested
        if args.summarize:
            summary = generate_summary(standardized_history)

            # Post-process the summary to replace user IDs with usernames
            processed_summary = replace_user_ids_with_names(summary)

            # Save both the summary and the full history
            with open(filename, "w", encoding="utf-8") as f:
                f.write(processed_summary)

            # Save the full history to a separate file
            full_history_filename = (
                f"discord_history_{channel_name}_{first_date_str}_{today}.txt"
            )
            with open(full_history_filename, "w", encoding="utf-8") as f:
                f.write(standardized_history)

            print(f"\nSummary saved to {filename}")
            print(f"Full chat history saved to {full_history_filename}")
        else:
            # Save only the full history
            with open(filename, "w", encoding="utf-8") as f:
                f.write(standardized_history)

            print(f"\nChat history saved to {filename}")

    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback

        print(f"Error Traceback: {traceback.format_exc()}")

    finally:
        await bot.close()


async def main():
    async with bot:
        await bot.start(DISCORD_TOKEN)


if __name__ == "__main__":
    asyncio.run(main())
