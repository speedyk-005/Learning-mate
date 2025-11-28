from textwrap import dedent

from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool

from ..utils import retry_config

class CoursePlannerInput(BaseModel):
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

plan_course = AgentTool(
    Agent(
        model=Gemini(
            model="gemini-2.5-flash",
            retry_options=retry_config
        ),
        name="course_planner",
        description="Produces structured course plans using the given schema-defined inputs.",
        input_schema=CoursePlannerInput,
        instruction=dedent("""
            Build well-structured course plans based entirely on the input fields you receive.

            Requirements:
            1. Use 'course_goal' as the central anchor for the entire curriculum.
            2. Integrate 'additional_info' only when relevant and never fabricate content.
            3. Break the course into units with clear progression.
            4. Include estimated time for every unit.
            5. Specify when quizzes or evaluations should occur.
            6. Assign a score requirement for advancing past each evaluation.
            7. Produce structured output suitable for downstream lesson and quiz agents.
    """),
))
