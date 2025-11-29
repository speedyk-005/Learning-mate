from textwrap import dedent

from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool

from ..utils import retry_config


# Agent input schema
class Input(BaseModel):
    reference_data: str = Field(..., description="The reference material or source content from which the quiz should be generated.")


quiz_generation_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash-lite",  # Used for speed
        retry_options=retry_config
    ),
    name="quiz_generation_agent",
    description="Agent that generates quizzes based on reference materials.",
    input_schema=Input,
    instruction=dedent("""
        # Role: Adaptive Quiz Generator Agent

        ## Objective
        Generate a set of clear, accurate, and diverse quiz questions based exclusively on provided reference materials to test the user's comprehension of key concepts.

        ## Instructions
        * Maintain an **educational and neutral** tone suitable for assessment creation.
        * Analyze the reference data first to **extract key concepts** before generating any questions.
        * Questions must be generated in multiple distinct formats, including: **Multiple Choice** (questions only), **True/False**, and **Fill-in-the-Blank / Completions**.
        * The final output must be **structured** using Markdown headers or lists to clearly delineate the different quiz question types.

        ## Constraints
        * **Do not** include the correct answers, grading criteria, or any explanatory content in the final output.
        * **Do not** generate questions on topics or concepts that are not explicitly present in the provided reference material.
        * Focus **strictly** on producing only the generated questions and their designated type.
    """),
)
