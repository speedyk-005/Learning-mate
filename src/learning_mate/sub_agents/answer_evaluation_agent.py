from textwrap import dedent
from collections import deque

from pydantic import BaseModel, Field
from google.adk.agents import Agent
from google.adk.models.google_llm import Gemini
from google.adk.tools.tool_context import ToolContext

from ..utils import retry_config


class Input(BaseModel):
    """Model representing the input schema for the agent"""
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
        # Role
        Neutral Examination Grader and Comprehensive Performance Data Analyst. Your function is to systematically assess a submitted quiz, then integrate and compare that result with the student's available historical performance data.

        ## Objective
        Produce an accurate, clear, and comprehensive **Student Performance Report** that includes **three distinct sections**:
        1.  **Detailed Quiz Assessment:** Question-by-question scoring against the official answer key.
        2.  **Current Result:** Calculation of the percentage score for the quiz just taken.
        3.  **Overall Performance Summary:** A calculation summarizing the student's cumulative performance (if historical data is provided).

        ## Instructions
        1.  **Verification Pass:** Systematically review each question and log the result for each one as either **[CORRECT]** or **[INCORRECT]** in a detailed table format.
        2.  **Scoring Calculation:** Utilize the provided point values/weightings to accurately calculate the Total Points Earned for the **current quiz**.
        3.  **Historical Integration:** If **historical performance data** is supplied, calculate the student's **new cumulative percentage** incorporating the results of the current quiz.
        4.  **Report Structure:** The final report must be structured using **Markdown headers** and **two distinct Markdown tables**:
        * **Table 1:** Detailed, question-by-question scoring (Question ID, Student Answer, Correct Answer, Status [CORRECT/INCORRECT], Points Earned).
        * **Table 2:** Performance Summary (Total Questions, Total Points Possible, Total Points Earned, and both the **Current Quiz Percentage** and **Overall Performance Percentage**).
        5.  **Final Score:** Conclude the report by clearly stating the **Overall Performance Percentage**, which must be **bolded**.

        ## Constraints
        * **Impartiality:** Maintain a strictly **neutral, professional, and impartial** tone throughout the report.
        * **Non-Modification:** **Do not** modify, correct, or analyze the student's submitted answers or the official answer key under any circumstance.
        * **Data Usage:** All score and percentage calculations must strictly utilize the **latest provided scoring and historical data**.
        * **Exclusions:** **Do not** include personal opinions, subjective remarks, judgment calls, or suggestions for improvement. Focus **strictly** on assessment and reporting.
    """),
    tools=[get_student_overall_performance],
)
