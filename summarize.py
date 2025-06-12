import os
import asyncio
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Union
from dotenv import load_dotenv

import discord
from discord.ext import commands
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from colorama import init, Fore, Back, Style
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

# Initialize colorama
init(autoreset=True)

# Load environment variables
load_dotenv(override=True)

# Parse command line arguments
parser = argparse.ArgumentParser(
    description="Fetch and summarize chat history from Discord or Slack channels"
)
parser.add_argument("--since-days", type=int, required=True, help="Number of days to look back from today")
parser.add_argument("--platform", choices=["discord", "slack"], default="discord", help="Platform to fetch messages from (default: discord)")
parser.add_argument("--channel", required=True, help="Channel ID (Discord) or Channel name (Slack)")
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
args = parser.parse_args()

# Calculate the since_date based on the number of days to look back
since_date = datetime.now() - timedelta(days=args.since_days)
print(f"{Fore.CYAN}→ Looking back {Fore.YELLOW}{args.since_days}{Fore.CYAN} days from today ({Fore.GREEN}{since_date.date()}{Fore.CYAN}){Style.RESET_ALL}")

# Get channel ID/name
channel_identifier = args.channel

# Get platform-specific tokens
if args.platform == "discord":
    # Get Discord token
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    if not DISCORD_TOKEN:
        print(f"{Fore.RED}Error: DISCORD_TOKEN environment variable is not set{Style.RESET_ALL}")
        exit(1)
    
    try:
        channel_id = int(channel_identifier)
    except ValueError:
        print(f"{Fore.RED}Error: Invalid Discord channel ID{Style.RESET_ALL}")
        exit(1)
else:  # Slack
    # Get Slack token
    SLACK_TOKEN = os.getenv("SLACK_TOKEN")
    if not SLACK_TOKEN:
        print(f"{Fore.RED}Error: SLACK_TOKEN environment variable is not set{Style.RESET_ALL}")
        exit(1)

# Get OpenAI API key if using remote model
if args.model_source == "remote":
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        print(f"{Fore.RED}Error: OPENAI_API_KEY environment variable is not set{Style.RESET_ALL}")
        exit(1)

# User mapping cache
user_mapping = {}


async def fetch_discord_messages(
    channel_id: int, since_date: datetime
) -> tuple[str, datetime]:
    """Fetch messages from a Discord channel since a specific date and format them as a human-readable chat history.

    Returns:
        tuple: (formatted_history, first_message_date)
    """
    print(f"\n{Fore.CYAN}→ Fetching messages from Discord channel {Fore.YELLOW}{channel_id}{Fore.CYAN} since {Fore.GREEN}{since_date.date()}{Style.RESET_ALL}")

    channel = bot.get_channel(channel_id)
    if not channel:
        print(f"    {Fore.RED}Error: Channel {channel_id} not found{Style.RESET_ALL}")
        print(f"    {Fore.YELLOW}Available channels: {[ch.id for ch in bot.get_all_channels()]}{Style.RESET_ALL}")
        return "", since_date

    print(f"    {Fore.GREEN}Found channel: {channel.name}{Style.RESET_ALL}")

    # Create a human-readable chat history
    chat_history = []
    message_count = 0
    thread_count = 0
    print(f"    {Fore.CYAN}Fetching messages...{Style.RESET_ALL}", end="", flush=True)

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
                print(f"{Fore.CYAN}.{Style.RESET_ALL}", end="", flush=True)

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
                print(f"\n    {Fore.MAGENTA}Found thread: {thread.name}{Style.RESET_ALL}")

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
                    f"\n    {Fore.GREEN}Processed {thread_message_count} messages in thread {thread.name}{Style.RESET_ALL}"
                )
                chat_history.append("--- End of Thread ---\n")

    except discord.Forbidden as e:
        print(f"\n    {Fore.RED}Error: Bot doesn't have permission to read message history: {str(e)}{Style.RESET_ALL}")
        return "", since_date
    except discord.HTTPException as e:
        print(f"\n    {Fore.RED}Error: HTTP error while fetching messages: {str(e)}{Style.RESET_ALL}")
        return "", since_date
    except Exception as e:
        print(f"\n    {Fore.RED}Error: Unexpected error while fetching messages: {str(e)}{Style.RESET_ALL}")
        import traceback

        print(f"    {Fore.RED}Error Traceback: {traceback.format_exc()}{Style.RESET_ALL}")
        return "", since_date

    print(f"\n    {Fore.GREEN}Total messages scanned: {message_count}{Style.RESET_ALL}")
    print(f"    {Fore.GREEN}Total threads scanned: {thread_count}{Style.RESET_ALL}")
    print(f"    {Fore.GREEN}Total unique users: {len(user_mapping)}{Style.RESET_ALL}")

    # If no messages were found, use the since_date
    if first_message_date is None:
        first_message_date = since_date
    else:
        print(f"    {Fore.GREEN}First message date: {first_message_date.date()}{Style.RESET_ALL}")

    # Join all messages with newlines to create a single string
    formatted_history = "\n".join(chat_history)
    return formatted_history, first_message_date


def fetch_slack_messages(
    channel_name: str, since_date: datetime
) -> tuple[str, datetime]:
    """Fetch messages from a Slack channel since a specific date and format them as a human-readable chat history.

    Returns:
        tuple: (formatted_history, first_message_date)
    """
    print(f"\n{Fore.CYAN}→ Fetching messages from Slack channel {Fore.YELLOW}{channel_name}{Fore.CYAN} since {Fore.GREEN}{since_date.date()}{Style.RESET_ALL}")

    # Initialize Slack client
    client = WebClient(token=SLACK_TOKEN)
    
    # Get channel ID from channel name
    try:
        # List all channels to find the one we want
        result = client.conversations_list()
        channel_id = None
        channel_info = None
        
        for channel in result["channels"]:
            if channel["name"] == channel_name:
                channel_id = channel["id"]
                channel_info = channel
                break
        
        if not channel_id:
            print(f"    {Fore.RED}Error: Channel {channel_name} not found{Style.RESET_ALL}")
            return "", since_date
        
        print(f"    {Fore.GREEN}Found channel: {channel_info['name']}{Style.RESET_ALL}")
        
        # Create a human-readable chat history
        chat_history = []
        message_count = 0
        thread_count = 0
        print(f"    {Fore.CYAN}Fetching messages...{Style.RESET_ALL}", end="", flush=True)
        
        # Clear the user mapping cache for this fetch
        global user_mapping
        user_mapping = {}
        
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
                    channel=channel_id,
                    oldest=since_timestamp,
                    cursor=cursor,
                    limit=100
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
                            user_mapping[username] = user_id
                        except SlackApiError:
                            username = f"User_{user_id}"
                    
                    # Format message
                    timestamp_str = message_date.strftime("%Y-%m-%d %H:%M:%S")
                    formatted_message = f"[{timestamp_str}] {username}: {message['text']}"
                    
                    # Add message to chat history
                    chat_history.append(formatted_message)
                    
                    # Check for thread replies
                    if "thread_ts" in message and message["thread_ts"] == message["ts"]:
                        # This is a thread parent message
                        thread_count += 1
                        print(f"\n    {Fore.MAGENTA}Found thread{Style.RESET_ALL}")
                        
                        # Add thread header
                        chat_history.append(f"\n--- Thread ---")
                        
                        # Fetch thread replies
                        thread_result = client.conversations_replies(
                            channel=channel_id,
                            ts=message["ts"]
                        )
                        
                        thread_messages = thread_result["messages"]
                        thread_message_count = 0
                        
                        for thread_message in thread_messages[1:]:  # Skip the parent message
                            thread_message_count += 1
                            if thread_message_count % 100 == 0:
                                print(f"{Fore.CYAN}.{Style.RESET_ALL}", end="", flush=True)
                            
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
                                    thread_user_info = client.users_info(user=thread_user_id)
                                    thread_username = thread_user_info["user"]["name"]
                                    user_mapping[thread_username] = thread_user_id
                                except SlackApiError:
                                    thread_username = f"User_{thread_user_id}"
                            
                            # Format thread message
                            thread_timestamp_str = thread_date.strftime("%Y-%m-%d %H:%M:%S")
                            formatted_thread_message = f"[{thread_timestamp_str}] {thread_username}: {thread_message['text']}"
                            
                            # Add thread message to chat history
                            chat_history.append(formatted_thread_message)
                        
                        print(f"\n    {Fore.GREEN}Processed {thread_message_count} messages in thread{Style.RESET_ALL}")
                        chat_history.append("--- End of Thread ---\n")
                
            except SlackApiError as e:
                print(f"\n    {Fore.RED}Error: Slack API error: {str(e)}{Style.RESET_ALL}")
                return "", since_date
            except Exception as e:
                print(f"\n    {Fore.RED}Error: Unexpected error while fetching messages: {str(e)}{Style.RESET_ALL}")
                import traceback
                
                print(f"    {Fore.RED}Error Traceback: {traceback.format_exc()}{Style.RESET_ALL}")
                return "", since_date
        
        print(f"\n    {Fore.GREEN}Total messages scanned: {message_count}{Style.RESET_ALL}")
        print(f"    {Fore.GREEN}Total threads scanned: {thread_count}{Style.RESET_ALL}")
        print(f"    {Fore.GREEN}Total unique users: {len(user_mapping)}{Style.RESET_ALL}")
        
        # If no messages were found, use the since_date
        if first_message_date is None:
            first_message_date = since_date
        else:
            print(f"    {Fore.GREEN}First message date: {first_message_date.date()}{Style.RESET_ALL}")
        
        # Join all messages with newlines to create a single string
        formatted_history = "\n".join(chat_history)
        return formatted_history, first_message_date
        
    except SlackApiError as e:
        print(f"\n    {Fore.RED}Error: Slack API error: {str(e)}{Style.RESET_ALL}")
        return "", since_date
    except Exception as e:
        print(f"\n    {Fore.RED}Error: Unexpected error while fetching messages: {str(e)}{Style.RESET_ALL}")
        import traceback
        
        print(f"    {Fore.RED}Error Traceback: {traceback.format_exc()}{Style.RESET_ALL}")
        return "", since_date


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
        f"<@{user_id}>": f"@{username}" for username, user_id in user_mapping.items()
    }

    # Replace user IDs with usernames
    processed_summary = summary
    for id_mention, username in id_to_username.items():
        processed_summary = processed_summary.replace(id_mention, username)

    return processed_summary


def generate_summary(chat_history: str) -> str:
    """Generate a summary of the chat history using the specified model."""
    print(f"\n{Fore.CYAN}→ Generating summary...{Style.RESET_ALL}")

    try:
        # Create the system prompt
        system_prompt = """
You are an expert summarizer for PyMC Labs, specializing in internal Discord chat related to consulting projects involving Bayesian modeling.
Your task is to read a sequence of messages and generate a clear, structured summary that captures the project's current state.

First, determine the time span covered by the chat messages you receive:
	•	If the messages span 0–2 days, produce a Project Event Update.
	•	If the messages span 3–7 days, produce a Periodical Digest.
	•	If the messages span 8 or more days, produce a Full Project Status Summary.

⸻

Instructions for a Project Event Update (0–2 days):
	•	Focus on what was done, what remains open, and immediate actionables.
	•	Capture individual contributions: who did or said what.
	•	Highlight any assumptions, modeling choices, data sources, or constraints discussed.
	•	Flag anything time-sensitive or urgent.
	•	Write in bullet points, grouped under clear headings like "Completed", "Open Actions", "Contributors", "Notes".
	•	Suitable for project manager who wants a daily digest.


Instructions for a Periodical Digest (3–7 days):
	•	Focus on trends, major developments, and overall project movement.
	•	Summarize key achievements and broader tasks or challenges.
	•	Group contributions by theme or workstream rather than by individual post.
	•	Note general roles only if important for context.
	•	Identify any emerging risks, open technical questions, or important strategic discussions.
	•	Keep it compact but higher-level, suitable for someone catching up after a few days away.

Instructions for a Full Project Status Summary (8+ days):
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
                    "Here is the chat history to summarize: {chat_history}",
                ),
            ]
        )

        # Initialize the appropriate model
        if args.model_source == "remote":
            llm = ChatOpenAI(model=args.model, temperature=0)
        else:  # local model
            print(f"    {Fore.YELLOW}Using local model: {args.model}{Style.RESET_ALL}")
            llm = Ollama(model=args.model)

        # Create the chain
        chain = prompt | llm

        # Invoke the chain
        result = chain.invoke({"chat_history": chat_history})

        print(f"    {Fore.GREEN}Summary generated successfully{Style.RESET_ALL}")
        return result.content
    except Exception as e:
        print(f"    {Fore.RED}Error generating summary: {str(e)}{Style.RESET_ALL}")
        import traceback

        print(f"    {Fore.RED}Error Traceback: {traceback.format_exc()}{Style.RESET_ALL}")
        return f"Error generating summary: {str(e)}"


def create_chat_chain(chat_history: str):
    """Create a chat chain for interactive chat with the collected history."""
    # Initialize the appropriate model
    if args.model_source == "remote":
        llm = ChatOpenAI(model=args.model, temperature=0.7)
    else:  # local model
        print(f"    {Fore.YELLOW}Using local model: {args.model}{Style.RESET_ALL}")
        llm = Ollama(model=args.model)
    
    # Create the system prompt
    system_prompt = f"""
You are a helpful assistant with access to a chat history. 
You can answer questions about the content of this chat history.

Here is the chat history you have access to:

{chat_history}

When answering questions:
1. Be concise and direct
2. Only reference information that is in the chat history
3. If you don't know something, say so
4. Use markdown formatting for better readability
5. When mentioning users, use their IDs (like <@123456789012345678>)
"""
    
    # Create the prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
    
    # Create the chain
    chain = (
        RunnablePassthrough.assign(
            history=lambda x: x.get("history", [])
        )
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return chain

def interactive_chat_session(chat_history: str):
    """Start an interactive chat session with the collected conversation history."""
    print(f"\n{Fore.CYAN}→ Starting interactive chat session...{Style.RESET_ALL}")
    print(f"    {Fore.YELLOW}Type 'exit', 'quit', or 'q' to end the session{Style.RESET_ALL}")
    print(f"    {Fore.YELLOW}Type 'help' for available commands{Style.RESET_ALL}")
    print(f"    {Fore.CYAN}{'-' * 50}{Style.RESET_ALL}")
    
    # Create the chat chain
    chain = create_chat_chain(chat_history)
    
    # Initialize message history
    message_history = []
    
    # Start the chat loop
    while True:
        try:
            # Get user input
            user_input = input(f"\n{Fore.GREEN}You:{Style.RESET_ALL} ").strip()
            
            # Check for exit commands
            if user_input.lower() in ["exit", "quit", "q"]:
                print(f"{Fore.CYAN}→ Ending chat session...{Style.RESET_ALL}")
                break
            
            # Check for help command
            if user_input.lower() == "help":
                print(f"\n{Fore.CYAN}→ Available commands:{Style.RESET_ALL}")
                print(f"    {Fore.YELLOW}help{Style.RESET_ALL} - Show this help message")
                print(f"    {Fore.YELLOW}exit/quit/q{Style.RESET_ALL} - End the chat session")
                print(f"    {Fore.YELLOW}summary{Style.RESET_ALL} - Generate a summary of the chat history")
                print(f"    {Fore.YELLOW}users{Style.RESET_ALL} - List all users mentioned in the chat history")
                continue
            
            # Check for summary command
            if user_input.lower() == "summary":
                print(f"\n{Fore.CYAN}→ Generating summary...{Style.RESET_ALL}")
                summary = generate_summary(chat_history)
                processed_summary = replace_user_ids_with_names(summary)
                print(f"\n{Fore.CYAN}→ Summary:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
                print(processed_summary)
                print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
                continue
            
            # Check for users command
            if user_input.lower() == "users":
                print(f"\n{Fore.CYAN}→ Users mentioned in the chat history:{Style.RESET_ALL}")
                for username, user_id in user_mapping.items():
                    print(f"    {Fore.GREEN}@{username}{Style.RESET_ALL} ({Fore.YELLOW}<@{user_id}>{Style.RESET_ALL})")
                continue
            
            # Get response from the model
            response = chain.invoke({
                "input": user_input,
                "history": message_history
            })
            
            # Replace user IDs with usernames in the response
            processed_response = replace_user_ids_with_names(response)
            
            # Update message history with the original response (with IDs)
            message_history.append(HumanMessage(content=user_input))
            message_history.append(AIMessage(content=response))
            
            # Print the processed response (with usernames)
            print(f"\n{Fore.BLUE}Assistant:{Style.RESET_ALL} {processed_response}")
            
        except KeyboardInterrupt:
            print(f"\n{Fore.CYAN}→ Ending chat session...{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Please try again.{Style.RESET_ALL}")

# Initialize Discord client with intents
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{Fore.GREEN}{bot.user}{Fore.CYAN} is now running!{Style.RESET_ALL}")

    try:
        # Fetch messages based on platform
        if args.platform == "discord":
            chat_history, first_message_date = await fetch_discord_messages(
                channel_id, since_date
            )
        else:  # Slack
            chat_history, first_message_date = fetch_slack_messages(
                channel_identifier, since_date
            )

        if not chat_history:
            print(f"{Fore.RED}No messages found or error occurred{Style.RESET_ALL}")
            await bot.close()
            return

        # Standardize user references
        standardized_history = standardize_user_references(chat_history)

        # Create filename based on channel, first message date, and today's date
        if args.platform == "discord":
            channel = bot.get_channel(channel_id)
            channel_name = channel.name if channel else str(channel_id)
        else:  # Slack
            channel_name = channel_identifier
            
        today = datetime.now().strftime("%Y-%m-%d")
        first_date_str = first_message_date.strftime("%Y-%m-%d")

        # Generate summary
        summary = generate_summary(standardized_history)

        # Post-process the summary to replace user IDs with usernames
        processed_summary = replace_user_ids_with_names(summary)

        if args.dump_file is not None:
            # Create the output directory if it doesn't exist
            output_dir = args.dump_file if os.path.isdir(args.dump_file) else os.path.dirname(args.dump_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # Determine the output path for the summary
            if os.path.isdir(args.dump_file):
                summary_filename = os.path.join(
                    args.dump_file,
                    f"{args.platform}_history_summary_{channel_name}_{first_date_str}_{today}.md"
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
                        f"{args.platform}_history_{channel_name}_{first_date_str}_{today}.md"
                    )
                else:
                    full_history_filename = os.path.join(
                        os.path.dirname(args.dump_file),
                        f"{args.platform}_history_{channel_name}_{first_date_str}_{today}.md"
                    )
                with open(full_history_filename, "w", encoding="utf-8") as f:
                    f.write(standardized_history)
                print(f"{Fore.GREEN}→ Full chat history saved to {full_history_filename}{Style.RESET_ALL}")
        else:
            # Print the summary to terminal
            print(f"\n{Fore.CYAN}{Style.BRIGHT}→ Generated Summary:{Style.RESET_ALL}")
            print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
            print(processed_summary)
            print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
        
        # Start interactive chat session if requested
        if args.chat:
            interactive_chat_session(standardized_history)

    except Exception as e:
        print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
        import traceback

        print(f"{Fore.RED}Error Traceback: {traceback.format_exc()}{Style.RESET_ALL}")

    finally:
        await bot.close()


async def main():
    if args.platform == "discord":
        async with bot:
            await bot.start(DISCORD_TOKEN)
    else:  # Slack
        # For Slack, we don't need to use the Discord bot
        try:
            # Fetch messages
            chat_history, first_message_date = fetch_slack_messages(
                channel_identifier, since_date
            )

            if not chat_history:
                print(f"{Fore.RED}No messages found or error occurred{Style.RESET_ALL}")
                return

            # Standardize user references
            standardized_history = standardize_user_references(chat_history)

            # Create filename based on channel, first message date, and today's date
            channel_name = channel_identifier
            today = datetime.now().strftime("%Y-%m-%d")
            first_date_str = first_message_date.strftime("%Y-%m-%d")

            # Generate summary
            summary = generate_summary(standardized_history)

            # Post-process the summary to replace user IDs with usernames
            processed_summary = replace_user_ids_with_names(summary)

            if args.dump_file is not None:
                # Create the output directory if it doesn't exist
                output_dir = args.dump_file if os.path.isdir(args.dump_file) else os.path.dirname(args.dump_file)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir)

                # Determine the output path for the summary
                if os.path.isdir(args.dump_file):
                    summary_filename = os.path.join(
                        args.dump_file,
                        f"slack_history_summary_{channel_name}_{first_date_str}_{today}.md"
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
                            f"slack_history_{channel_name}_{first_date_str}_{today}.md"
                        )
                    else:
                        full_history_filename = os.path.join(
                            os.path.dirname(args.dump_file),
                            f"slack_history_{channel_name}_{first_date_str}_{today}.md"
                        )
                    with open(full_history_filename, "w", encoding="utf-8") as f:
                        f.write(standardized_history)
                    print(f"{Fore.GREEN}→ Full chat history saved to {full_history_filename}{Style.RESET_ALL}")
            else:
                # Print the summary to terminal
                print(f"\n{Fore.CYAN}{Style.BRIGHT}→ Generated Summary:{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
                print(processed_summary)
                print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
            
            # Start interactive chat session if requested
            if args.chat:
                interactive_chat_session(standardized_history)

        except Exception as e:
            print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
            import traceback

            print(f"{Fore.RED}Error Traceback: {traceback.format_exc()}{Style.RESET_ALL}")


if __name__ == "__main__":
    asyncio.run(main())
