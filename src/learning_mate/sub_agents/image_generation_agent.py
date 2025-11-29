import requests
from io import BytesIO
from textwrap import dedent

from pydantic import BaseModel, Field

import google.genai.types as types
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.models.google_llm import Gemini
from google.adk.tools.load_artifacts_tool import LoadArtifactsTool

from ..utils import retry_config


# Agent input schema
class Input(BaseModel):
    prompt: str = Field(..., description="The main description of the image to generate.")
    context: str | None = Field(None, description="Optional additional context to enhance the prompt or add detail.")


async def generate_image(
    prompt: str,
    name: str | None = None,
    tool_context: ToolContext | None = None
) -> dict:
    """
    Generate an image using the free Pollinations REST API and save it as an artifact.

    Args:
        prompt (str): Description of the desired image.
        name (str, optional): Optional artifact name.

    Returns:
        dict: {
            "status": "success" or "error",
            "processed_image_artifact": artifact filename,
            "version_number": saved version,
            "error_message": optional error message
        }
    """
    try:
        # REST API URL
        url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"

        # Download the image
        response = requests.get(url)
        response.raise_for_status()

        # Convert to bytes
        image_bytes = BytesIO(response.content).getvalue()

        # Prepare artifact
        artifact_name = name or f"{prompt[:30].replace(' ', '_')}_image.png"
        image_artifact = types.Part(
            inline_data=types.Blob(
                mime_type="image/png",
                data=image_bytes
            )
        )

        # Save using tool_context
        version = await tool_context.save_artifact(
            filename=artifact_name,
            artifact=image_artifact,
        )

        return {
            "status": "success",
            "processed_image_artifact": artifact_name,
            "version_number": version,
        }

    except Exception as e:
        return {
            "status": "error",
            "error_message": str(e)
        }


image_generation_agent = Agent(
    model=Gemini(
        model="gemini-2.5-flash-lite", # Used for speed
        retry_options=retry_config
    ),
    name="image_generation_agent",
    description="An agent that creates and refines visual illustrations to perfectly complement lesson content using contextual cues.",
    input_schema=Input,
    instruction=dedent("""
        # Role: Image Generation Specialist

        ## Objective
        Generate visually rich images that effectively complement the current lesson overview by enhancing the input prompt with contextual and artistic detail.

        ## Instructions
        * Use the input `prompt` and optional `context` to inform and guide the image generation process.
        * If the provided prompt lacks detail, you must enhance it using the context or creative reasoning to ensure a visually rich and detailed result.
        * Use the **`generate_image`** tool to produce the final image based on the enhanced prompt.
        * Use the **`LoadArtifactsTool`** only if the task explicitly requires access to previously saved visual assets.

        ## Constraints
        * **Must** ensure the generated image is highly relevant and complementary to the lesson's key concepts.
        * Avoid generating generic or abstract concepts when a specific, illustrative visual is needed.
    """),
    tools=[generate_image, LoadArtifactsTool],
)
