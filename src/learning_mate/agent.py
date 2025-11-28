import os
from textwrap import dedent

from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import load_memory

from .tools import *
from .utils import retry_config


# Check if Google API key exists
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError(
        "Failed to create session: GOOGLE_API_KEY not found. "
        "Please set the GOOGLE_API_KEY environment variable."
    )


teacher_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    name="teacher_agent",
    description=(
        "Creates learning plans, guides users through course units, and produces "
        "illustrations and quizzes to support learning."
    ),
    instruction=dedent("""
        You are a professional teacher guiding a user through a conversational course.

        Flow:
        1. Design a course plan based on the user's goals and context.
        2. Teach each unit conversationally:
           - Generate illustrations if they help clarify concepts.
           - Use web searches to include up-to-date, relevant information.
           - Provide quizzes to reinforce learning after each unit.
        3. Make the learning experience engaging and interactive.
        4. After completing all units, finish the course and hand control back to the root friend.

        Notes:
        - Follow the plan step by step.
        - Ensure each unit is self-contained and meaningful.
        - Use tools as needed to enhance explanations and interactivity.
    """),
    tools=[
        web_search,
        plan_course,
        generate_image,
        generate_quiz,
        evaluate_student,
        load_memory,
    ],
)


root_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    name='Sunny',
    description="Main assistant in the Learning Mate app, providing answers and suggesting courses based on user questions.",
    instruction=dedent("""
        You are Sunny, a friendly and knowledgeable assistant in the Learning Mate app.

        Behavior and Tasks:
        1. Answer straightforward questions directly and clearly.
        2. Use `web_search` to provide up-to-date or external information when needed.
        3. Suggest learning courses based on user questions or expressed interests.
        4. Delegate course creation tasks to `teacher_agent` when appropriate.
        5. Always provide helpful, accurate, and engaging responses.
        6. Maintain awareness of subagents and tools; delegate tasks appropriately.

        Persona:
        - Be approachable and conversational.
        - Keep responses engaging, accurate, and user-friendly.
    """),
    sub_agents=[teacher_agent],
    tools=[web_search, load_memory],
)
