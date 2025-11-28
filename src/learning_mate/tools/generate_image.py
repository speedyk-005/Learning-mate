import requests
from io import BytesIO
from textwrap import dedent

from pydantic import BaseModel, Field

import google.genai.types as types
from google.adk.agents import Agent
from google.adk.tools import AgentTool
from google.adk.tools.tool_context import ToolContext
from google.adk.models.google_llm import Gemini
from google.adk.tools.load_artifacts_tool import LoadArtifactsTool

from ..utils import retry_config


class GenerateImageInput(BaseModel):
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


illustrator_agent = AgentTool(
    Agent(
        model=Gemini(
            model="gemini-2.5-flash",
            retry_options=retry_config
        ),
        name="illustrator",
        description="An agent specialized in creating visual illustrations for lesson content.",
        input_schema=GenerateImageInput,
        instruction=dedent("""
            You are an Illustrator Agent. Your task is to generate images that complement the
            current lesson overview. Use the input `prompt` and optional `context` to inform
            your image generation. If the prompt lacks detail, enhance it by using the context
            or your own reasoning to produce a visually rich result.

            Guidelines:

            - Choose an appropriate image model for the style and complexity needed.
            - Use `generate_image` to produce the image based on the enhanced prompt.
            - Use `LoadArtifactsTool` only if you need access to previously saved artifacts.
        """),
        tools=[generate_image, LoadArtifactsTool],
    )
)
