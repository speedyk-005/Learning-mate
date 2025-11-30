import ast
from google.genai import types

# Retry configuration for Google GenAI API
retry_config = types.HttpRetryOptions(
    attempts=5,           # Maximum retry attempts
    exp_base=7,           # Delay multiplier for exponential backoff
    initial_delay=1,      # Initial delay in seconds
    http_status_codes=[429, 500, 503, 504],  # Retry on these HTTP status codes
)


def extract_genai_error_message(error: Exception) -> str:
    """
    Extracts a human-readable error message from a Google GenAI API exception.

    Args:
        error (Exception): The caught exception from any GenAI API call.

    Returns:
        str: Parsed error message if possible, else the raw exception string.
    """
    raw_msg = str(error)
    try:
        # GenAI errors often have a leading code followed by a dict-like structure
        dict_part = raw_msg.split(". ", 1)[1]  # skip leading code/message
        error_json = ast.literal_eval(dict_part)
        return error_json.get("error", {}).get("message", raw_msg)
    except Exception:
        # Fallback to raw string if parsing fails
        return raw_msg
