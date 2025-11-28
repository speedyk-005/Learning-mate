from textwrap import dedent

from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool

from ..utils import retry_config

class GenerateQuizInput(BaseModel):
    reference_data: str = Field(..., description="The reference material or source content from which the quiz should be generated.")

generate_quiz = AgentTool(
    Agent(
        model=Gemini(
            model="gemini-2.5-flash-lite",  # Used for speed
            retry_options=retry_config
        ),
        name="quiz_maker",
        description="An agent that generates quizzes based on reference materials.",
        input_schema=GenerateQuizInput,
        instruction=dedent("""
            You are a quiz creation agent.

            Available information:
            - `reference_data`: The reference material or source content to base the quiz on.

            Your tasks:
            1. Analyze the provided reference data to extract key concepts.
            2. Generate quiz questions in multiple formats, including:
               - Multiple choice (questions only, without answers)
               - True/False
               - Fill-in-the-blank / completions
            3. Ensure clarity and correctness in all questions.
            4. Produce a structured output containing only the questions and their type.
            5. Avoid adding answers or unrelated content; focus strictly on the reference material.
        """),
    )
)
