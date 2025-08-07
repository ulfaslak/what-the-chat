"""Interactive chat service using LLMs."""

from typing import Dict, List

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from colorama import Fore, Style


class ChatService:
    """Service for interactive chat with chat history using LLMs."""
    
    def __init__(self, model_source: str = "local", model: str = "deepseek-r1-distill-qwen-7b"):
        """Initialize the chat service.
        
        Args:
            model_source: "local" for Ollama or "remote" for OpenAI
            model: Model name to use
        """
        self.model_source = model_source
        self.model = model
        self._llm = None
        self._chain = None
    
    def _get_llm(self):
        """Get or create the LLM instance."""
        if self._llm is None:
            if self.model_source == "remote":
                self._llm = ChatOpenAI(model=self.model, temperature=0.7)
            else:  # local model
                print(f"    {Fore.YELLOW}Using local model: {self.model}{Style.RESET_ALL}")
                self._llm = Ollama(model=self.model)
        return self._llm
    
    def create_chat_chain(self, chat_history: str):
        """Create a chat chain for interactive chat with the collected history.
        
        Args:
            chat_history: The formatted chat history to provide context
            
        Returns:
            Configured LangChain chain for chat
        """
        # Create the system prompt template
        system_prompt = """
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
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="history"),
                ("human", "{input}"),
            ]
        )

        # Get the LLM
        llm = self._get_llm()

        # Create the chain that passes chat_history as a variable
        self._chain = (
            RunnablePassthrough.assign(
                history=lambda x: x.get("history", []),
                chat_history=lambda x: chat_history
            )
            | prompt
            | llm
            | StrOutputParser()
        )

        return self._chain
    
    def chat(self, user_input: str, message_history: List) -> str:
        """Process a chat message and return the response.
        
        Args:
            user_input: User's input message
            message_history: List of previous messages
            
        Returns:
            AI response
        """
        if self._chain is None:
            raise ValueError("Chat chain not initialized. Call create_chat_chain first.")
        
        response = self._chain.invoke({"input": user_input, "history": message_history})
        return response
    
    def start_interactive_session(self, chat_history: str, user_mapping: Dict[str, str] = None):
        """Start an interactive chat session with the collected conversation history.
        
        Args:
            chat_history: The formatted chat history to provide context
            user_mapping: Optional user mapping for ID replacement
        """
        from ..utils.formatting import replace_user_ids_with_names
        from .summarization import SummarizationService
        
        print(f"\n{Fore.CYAN}→ Starting interactive chat session...{Style.RESET_ALL}")
        print(
            f"    {Fore.YELLOW}Type 'exit', 'quit', or 'q' to end the session{Style.RESET_ALL}"
        )
        print(f"    {Fore.YELLOW}Type 'help' for available commands{Style.RESET_ALL}")
        print(f"    {Fore.CYAN}{'-' * 50}{Style.RESET_ALL}")

        # Create the chat chain
        self.create_chat_chain(chat_history)

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
                    print(f"{Fore.GREEN}Thanks for using What The Chat! 👋{Style.RESET_ALL}")
                    break

                # Check for help command
                if user_input.lower() == "help":
                    print(f"\n{Fore.CYAN}→ Available commands:{Style.RESET_ALL}")
                    print(
                        f"    {Fore.YELLOW}help{Style.RESET_ALL} - Show this help message"
                    )
                    print(
                        f"    {Fore.YELLOW}exit/quit/q{Style.RESET_ALL} - End the chat session"
                    )
                    print(
                        f"    {Fore.YELLOW}summary{Style.RESET_ALL} - Generate a summary of the chat history"
                    )
                    print(
                        f"    {Fore.YELLOW}users{Style.RESET_ALL} - List all users mentioned in the chat history"
                    )
                    continue

                # Check for summary command
                if user_input.lower() == "summary":
                    print(f"\n{Fore.CYAN}→ Generating summary...{Style.RESET_ALL}")
                    summarizer = SummarizationService(self.model_source, self.model)
                    summary = summarizer.generate_summary(chat_history, user_mapping)
                    processed_summary = replace_user_ids_with_names(summary, user_mapping or {})
                    print(f"\n{Fore.CYAN}→ Summary:{Style.RESET_ALL}")
                    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
                    print(processed_summary)
                    print(f"{Fore.CYAN}{'=' * 80}{Style.RESET_ALL}")
                    continue

                # Check for users command
                if user_input.lower() == "users":
                    print(
                        f"\n{Fore.CYAN}→ Users mentioned in the chat history:{Style.RESET_ALL}"
                    )
                    if user_mapping:
                        for username, user_id in user_mapping.items():
                            print(
                                f"    {Fore.GREEN}@{username}{Style.RESET_ALL} ({Fore.YELLOW}<@{user_id}>{Style.RESET_ALL})"
                            )
                    else:
                        print(f"    {Fore.YELLOW}No user mapping available{Style.RESET_ALL}")
                    continue

                # Get response from the model
                response = self.chat(user_input, message_history)

                # Replace user IDs with usernames in the response
                processed_response = replace_user_ids_with_names(response, user_mapping or {})

                # Update message history with the original response (with IDs)
                message_history.append(HumanMessage(content=user_input))
                message_history.append(AIMessage(content=response))

                # Print the processed response (with usernames)
                print(f"\n{Fore.BLUE}Assistant:{Style.RESET_ALL} {processed_response}")

            except KeyboardInterrupt:
                print(f"\n{Fore.CYAN}→ Chat session interrupted by user{Style.RESET_ALL}")
                print(f"{Fore.GREEN}Thanks for using What The Chat! 👋{Style.RESET_ALL}")
                return  # Use return instead of break to properly exit the function
            except Exception as e:
                print(f"{Fore.RED}Error: {str(e)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}Please try again.{Style.RESET_ALL}")
