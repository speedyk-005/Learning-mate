import sys
import asyncio
from pathlib import Path

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

# Set up sys.path to ensure 'learning_mate' package is found when running from 'tests/'
current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root / "src"))

from learning_mate.agent import root_agent


async def main():
    """Runs the Learning Mate agent with a sample query sequence."""
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="app", user_id="test_user", session_id="test_session"
    )
    runner = Runner(
        agent=root_agent, app_name="app", session_service=session_service
    )

    queries = [
        "I need to learn the core concepts of quantum computing, starting from the basics.",
        "Can you break down the first two concepts into small, actionable lessons?",
        "Provide me with the content for the first lesson on 'Superposition'.",
        "Based on my progress, what should my personalized plan look like for the rest of the week?",
        "I've finished the 'Entanglement' lesson. Mark that task as complete.",
        "What's the next step in my learning path?",
    ]

    for query in queries:
        print(f">>> {query}")
        async for event in runner.run_async(
            user_id="test_user",
            session_id="test_session",
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=query)]
            ),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print(event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
