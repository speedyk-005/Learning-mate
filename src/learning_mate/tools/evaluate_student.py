from textwrap import dedent
from collections import deque

from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools import AgentTool
from google.adk.tools.tool_context import ToolContext

from ..utils import retry_config

class EvaluateStudentInput(BaseModel):
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


evaluate_student = AgentTool(
    Agent(
        model=Gemini(
            model="gemini-2.5-flash-lite",  # Used for speed
            retry_options=retry_config
        ),
        name="evaluator_agent",
        description="An unbiased agent that evaluates quizzes, calculates overall student performance, and provides a report after each evaluation.",
        input_schema=EvaluateStudentInput,
        instruction=dedent("""
            You are an unbiased quiz evaluator.

            Available information:
            - `current_quiz`: The full quiz content.
            - `answers`: The user's submitted answers.
            - `reference_data?`: Any additional relevant context or reference material.

            Your tasks:
            1. Review the quiz content and the submitted answers.
            2. Compare each answer against the quiz questions and determine correctness.
            3. Calculate the student's overall performance using the latest score.
            4. Produce a clear and concise report summarizing the evaluation and performance after each run.
            5. Remain neutral and impartial; do not add personal opinions or modify answers.
        """),
        tools=[get_student_overall_performance],
    )
)
