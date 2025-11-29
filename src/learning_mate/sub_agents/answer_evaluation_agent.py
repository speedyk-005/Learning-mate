from textwrap import dedent
from collections import deque

from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.tool_context import ToolContext

from ..utils import retry_config

# Agent input schema
class Input(BaseModel):
    current_quiz: str = Field(..., description="The full quiz content to be evaluated.")
    answers: str = Field(..., description="The student's submitted answers for the quiz.")
    reference_data: str | None = Field(None, description="Optional additional reference material to assist evaluation.")


def get_student_overall_performance(new_score: int, tool_context: ToolContext) -> dict:
    """
    Tracks recent quiz scores and calculates the student's overall performance as a percentage.
    """
    # Get existing deque or create one with maxlen 25
    scores = tool_context.state().get("recent_scores")
    if scores is None:
        scores = deque(maxlen=25)

    # Append the new score
    scores.append(new_score)
    tool_context.state["recent_scores"] = scores

    # Calculate percentage
    # Multiply by 5 because each score is based on a 0–5 scale
    percentage = round((sum(scores) / 100) * len(scores) * 5) if scores else 0

    return {
        "status": "success",
        "percentage": percentage
    }


answer_evaluation_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash-lite",  # Used for speed
        retry_options=retry_config
    ),
    name="answer_evaluation_agent",
    description="Agent that precisely evaluates quiz answers, computes performance metrics, and generates a formal, objective student report.",
    input_schema=Input,
    instruction=dedent("""
        # Role: Answer Assessment Specialist

        ## Objective
        Produce an accurate, clear, and comprehensive Student Performance Report by systematically reviewing quiz content, determining question-by-question correctness, and calculating the final percentage score.

        ## Instructions
        * Maintain a strictly **neutral, professional, and impartial** tone.
        * Systematically perform a verification pass, logging the result for each question as **[CORRECT]** or **[INCORRECT]**.
        * The final report must use Markdown tables and headers for maximum clarity.
        * End the response by stating the final percentage score, which must be **bolded** and tagged with **#rate 🎯**.

        ## Constraints
        * **Do not** modify or correct the student's submitted answers under any circumstance.
        * **Do not** include any personal opinions, subjective remarks, or judgment calls.
        * Score calculations must strictly utilize the latest provided scoring data (e.g., total points, weightings).
    """),
    tools=[get_student_overall_performance],
)
