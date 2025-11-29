from textwrap import dedent

from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool

from ..utils import retry_config


# Agent input schema
class Input(BaseModel):
    course_goal: str = Field(
        ...,
        description="Primary learning objective the course must accomplish."
    )
    additional_info: str | None = Field(
        None,
        description=(
            "Optional context such as research findings, performance metrics, "
            "recent developments, or recommended teaching practices."
        )
    )


course_planning_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=retry_config
    ),
    name="course_planning_agent",
    description="Agent that designs progressive, time-based course plans using specific goals and prepares the output for downstream lesson agents.",
    input_schema=Input,
    instruction=dedent("""
        # Role: Curriculum Architect Agent

        ## Objective
        Produce a complete, well-structured, and logically progressive course plan derived strictly from the provided input fields, ensuring the final structure meets all instructional requirements.

        ## Instructions
        * Break the course into discrete units, ensuring clear conceptual progression from start to finish.
        * Include an estimated time duration (e.g., in hours or sessions) for every unit.
        * Specify the exact point in the curriculum where quizzes or evaluations should occur.
        * The final output must be highly structured (e.g., JSON or nested Markdown) for seamless integration with lesson and quiz agents.

        ## Constraints
        * **Must** use the 'course_goal' as the central anchor for the entire curriculum structure.
        * **Must** assign a specific score requirement for advancing past any evaluation point.
        * Integrate 'additional_info' only when directly relevant; **never fabricate content** or make assumptions outside the provided materials.
        * Avoid generic or placeholder unit names and descriptions.
    """),
)
