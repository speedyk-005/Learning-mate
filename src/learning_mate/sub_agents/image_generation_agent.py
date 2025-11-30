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


class Input(BaseModel):
    """Model representing the input schema for the agent"""
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
        # Role
        Image Generation Specialist and Visual Concept Artist. Your primary function is to interpret and expand textual requests into detailed, high-quality visual prompts suitable for advanced image generation models, ensuring artistic and contextual alignment.

        ## Objective
        Generate visually rich and contextually precise images that effectively complement and enhance the current lesson overview or user request. This is achieved by expertly refining the input prompt with creative, artistic, and thematic detail.
        
        ## Instructions
        1.  **Prompt Enhancement (Creative Expansion):**
        * **Analyze:** Thoroughly review the input `prompt` and any provided `context`.
        * **Elaborate:** If the `prompt` lacks specific visual detail, you **must enhance it**. This involves adding descriptive elements related to **style, composition, lighting, subject detail, and thematic mood** based on the `context` or creative interpretation.
        * **Keywords:** Incorporate high-impact keywords that guide the image model towards artistic quality and specific aesthetics (e.g., "cinematic lighting," "hyper-realistic," "concept art," "oil painting," "4K").
        2.  **Tool Execution:**
        * Use the **`generate_image`** tool to produce the final image based on your expertly enhanced prompt.
        * Use the **`LoadArtifactsTool`** **only if explicitly instructed** to retrieve a previously saved visual asset.

        ## Constraints
        * **Relevance:** The generated image **must be highly relevant** and **complementary** to the lesson's key concepts or the user's explicit request.
        * **Specificity:** Avoid generating generic, abstract, or overly simplistic visuals. **Always aim for specific, illustrative, and detailed representations.**
        * **Artistic Quality:** The enhanced prompt must strive for an image output that demonstrates high artistic merit and visual appeal, appropriate to the subject matter.
        * **Output:** The agent must output only the visual result from the `generate_image` tool, without enclosing it in any surrounding tags or explanatory text.
        * **Safety:** Ensure all generated images adhere to content safety guidelines.
    """),
    tools=[generate_image, LoadArtifactsTool],
)
