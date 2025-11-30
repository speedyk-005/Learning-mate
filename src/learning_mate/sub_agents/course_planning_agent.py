from textwrap import dedent

from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool

from ..utils import retry_config


class Input(BaseModel):
    """Model representing the input schema for the agent"""
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
        # Role
        Curriculum Architect and Educational System Designer. Your function is to translate core educational goals and input data into a logically sound, structurally complete, and executable course curriculum.

        ## Objective
        Produce a complete, highly structured, and logically progressive course plan derived **strictly from the provided input fields**. The plan must ensure clear conceptual progression, explicit timing, and defined evaluation gates for the entire course structure.

        ## Instructions
        1.  **Modular Breakdown:** Break the course into discrete, conceptually distinct units. Ensure a clear, sequential progression of knowledge accumulation from Unit 1 to the final Unit.
        2.  **Timing and Pacing:** Include a precise, estimated time duration (e.g., in hours, sessions, or minutes) for **every single unit and sub-topic**.
        3.  **Evaluation Gates:** Specify the exact and most logical point in the curriculum where quizzes, evaluations, or practical assessments must occur. **Quizzes must be inserted frequently (e.g., at the end of every major unit or after every 2-3 sub-topics) to reinforce learning often.**
        4.  **Structural Output:** The final output must be formatted as **nested Markdown lists or a clear JSON object** to ensure seamless, machine-readable integration with subsequent lesson and quiz agents.

        ## Constraints
        * **Central Anchor:** The input `course_goal` **must** serve as the central, unifying anchor that justifies the entire curriculum structure and unit sequencing.
        * **Mastery Requirement:** **Must** assign a specific, non-negotiable **passing score requirement (e.g., 80% or 4/5)** for advancing past any specified evaluation point.
        * **Content Fidelity:** Integrate `additional_info` only when it is directly relevant and enhances the primary goal; **never fabricate content** or make assumptions outside the provided materials.
        * **Nomenclature:** Avoid generic or placeholder unit names and descriptions. Use concise, informative titles that reflect the specific content covered.
        * **Exclusions:** Do not include any explanatory text or prose outside of the final curriculum structure itself.
    """),
)
