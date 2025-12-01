from textwrap import dedent

from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.tool_context import ToolContext

from ..utils import retry_config


class Input(BaseModel):
    """Model representing the input schema for the answer evaluation agent"""
    current_quiz: str = Field(..., description="The full quiz content to be evaluated.")
    answers: str = Field(..., description="The student's submitted answers for the quiz.")
    reference_data: str | None = Field(None, description="Optional additional reference material to assist evaluation.")


def get_student_overall_performance(
    current_quiz_percentage: float,
    tool_context: ToolContext
) -> dict:
    """Tracks recent quiz percentages and calculates the student's overall performance.

    The overall performance is calculated as the rolling average of the last 25 quiz percentages.

    Args:
        current_quiz_percentage: The student's percentage score (0.0 to 100.0) from the
            most recently completed quiz.

    Returns:
        A dictionary containing the status and the calculated overall performance percentage.
        Example: {"status": "success", "overall_percentage": 78}
    """
    # Use .get() with a default value for cleaner initialization
    percentages = tool_context.state.get("recent_percentages", [])

    # Ensure list is manageable (maintains a rolling window of 25 scores)
    MAX_SCORES = 25
    if len(percentages) >= MAX_SCORES:
        percentages.pop(0) # Remove oldest percentage

    # Append the new percentage
    percentages.append(current_quiz_percentage)
    tool_context.state["recent_percentages"] = percentages

    # Calculating Percentage (as average of percentages)
    if percentages:
        # Overall percentage is the simple average of all stored percentages
        average_percentage = sum(percentages) / len(percentages)
        overall_percentage = round(average_percentage)
    else:
        overall_percentage = 0

    return {
        "status": "success",
        "overall_percentage": overall_percentage
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
        # Role
        Neutral Examination Grader and Comprehensive Performance Data Analyst. Your function is to systematically assess a submitted quiz, then integrate and compare that result with the student's available historical performance data.

        ## Objective
        Produce an accurate, clear, and comprehensive **Student Performance Report** that includes **three distinct sections**:
        1.  **Detailed Quiz Assessment:** Question-by-question scoring against the official answer key.
        2.  **Current Result:** Calculation of the percentage score for the quiz just taken.
        3.  **Overall Performance Summary:** The overall performance calculated automatically using the last recent scores by using the `get_student_overall_performance` tool.

        ## Instructions
        1.  **Verification Pass:** Systematically review each question and log the result for each one as either **[CORRECT]** or **[INCORRECT]** in a detailed table format.
        2.  **Report Structure:** The final report must be structured using **Markdown headers** and **two distinct Markdown tables**:
          * **Table 1:** Detailed, question-by-question scoring (Question ID, Student Answer, Correct Answer, Status [CORRECT/INCORRECT], Points Earned).
          * **Table 2:** Performance Summary (Total Questions, Total Points Possible, Total Points Earned, and both the **Current Quiz Percentage** and **Overall Performance Percentage**).

        ## Constraints
        * **Impartiality:** Maintain a strictly **neutral, professional, and impartial** tone throughout the report.
        * **Non-Modification:** **Do not** modify, correct, or analyze the student's submitted answers or the official answer key under any circumstance.
        * **Exclusions:** **Do not** include personal opinions, subjective remarks, judgment calls, or suggestions for improvement. Focus **strictly** on assessment and reporting.
    """),
    tools=[get_student_overall_performance],
)
