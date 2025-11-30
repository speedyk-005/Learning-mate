import requests
from io import BytesIO
from textwrap import dedent
from difflib import SequenceMatcher

from pydantic import BaseModel, Field

from google.genai import Client
import google.genai.types as types
from google.adk.agents import Agent
from google.adk.tools.tool_context import ToolContext
from google.adk.models.google_llm import Gemini
from google.adk.tools.load_artifacts_tool import LoadArtifactsTool

from ..utils import retry_config, extract_genai_error_message


class Input(BaseModel):
    """Model representing the input schema for the agent"""
    prompt: str = Field(..., description="The main description of the image to generate.")
    context: str | None = Field(None, description="Optional additional context to enhance the prompt or add detail.")


async def generate_image(
    prompt: str,
    name: str | None = None,
    tool_context: ToolContext = None,
) -> dict:
    """Generate an image using Google Imagen API with Pollinations fallback for free users.

    Args:
        prompt (str): Description of the desired image.
        name (str, optional): Optional artifact filename prefix.

    Returns:
        dict: {
            "status": "success" or "error",
            "processed_image_artifact": artifact filename,
            "version": saved version,
            "error_message": optional error message
        }
    """
    GOOGLE_FREE_USER_MSG = "Imagen API is only accessible to billed users at this time."

    try:
        # Attempt Google Imagen generation first
        client = Client()
        response = client.models.generate_images(
            model="imagen-4.0-generate-001",
            prompt=prompt,
            config=types.GenerateImagesConfig(number_of_images=1)
        )
        image_bytes = BytesIO(response.generated_images[0].image.image_bytes).getvalue()

    except Exception as e:
        genai_error_msg = extract_genai_error_message(e)
        similarity = SequenceMatcher(None, genai_error_msg, GOOGLE_FREE_USER_MSG).ratio()

        if similarity >= 0.8:
            # Pollinations fallback
            try:
                url = f"https://image.pollinations.ai/prompt/{requests.utils.quote(prompt)}"
                response = requests.get(url)
                response.raise_for_status()
                image_bytes = BytesIO(response.content).getvalue()

            except Exception as pollination_error:
                return {
                    "status": "error",
                    "errr_message": (
                        f"Google Imagen is not available for free users. "
                        f"Pollinations attempt encountered an error: {pollination_error}"
                    )
                }
        else:
            return {
                "status": "error",
                "error_message": f" error 404 {genai_error_msg}"
            }

    # Create artifact object from generated image data
    artifact_name = name or "_".join(prompt.split()[:7]) + ".png"
    image_artifact = types.Part(
        inline_data=types.Blob(
            mime_type="image/png",
            data=image_bytes
        )
    )

    # Save artifact using tool context
    version = await tool_context.save_artifact(
        filename=artifact_name,
        artifact=image_artifact,
    )

    return {
        "status": "success",
        "processed_image_artifact": artifact_name,
        "version": version,
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
    """),
    tools=[generate_image, LoadArtifactsTool],
)
