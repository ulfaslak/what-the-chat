"""Summarization service using LLMs."""

from typing import Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.llms import Ollama
from colorama import Fore, Style


class SummarizationService:
    """Service for generating summaries of chat history using LLMs."""
    
    def __init__(self, model_source: str = "local", model: str = "deepseek-r1-distill-qwen-7b"):
        """Initialize the summarization service.
        
        Args:
            model_source: "local" for Ollama or "remote" for OpenAI
            model: Model name to use
        """
        self.model_source = model_source
        self.model = model
        self._llm = None
    
    def _get_llm(self):
        """Get or create the LLM instance."""
        if self._llm is None:
            if self.model_source == "remote":
                self._llm = ChatOpenAI(model=self.model, temperature=0)
            else:  # local model
                print(f"    {Fore.YELLOW}Using local model: {self.model}{Style.RESET_ALL}")
                self._llm = Ollama(model=self.model)
        return self._llm
    
    def generate_summary(self, chat_history: str, user_mapping: Dict[str, str] = None) -> str:
        """Generate a summary of the chat history using the specified model.
        
        Args:
            chat_history: The formatted chat history to summarize
            user_mapping: Optional user mapping for ID replacement
            
        Returns:
            Generated summary text
        """
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

            # Get the LLM
            llm = self._get_llm()

            # Create the chain
            chain = prompt | llm

            # Invoke the chain
            result = chain.invoke({"chat_history": chat_history})

            print(f"    {Fore.GREEN}Summary generated successfully{Style.RESET_ALL}")
            
            # Handle different response types
            if hasattr(result, 'content'):
                return result.content
            else:
                return str(result)
                
        except Exception as e:
            print(f"    {Fore.RED}Error generating summary: {str(e)}{Style.RESET_ALL}")
            import traceback

            print(
                f"    {Fore.RED}Error Traceback: {traceback.format_exc()}{Style.RESET_ALL}"
            )
            return f"Error generating summary: {str(e)}"
