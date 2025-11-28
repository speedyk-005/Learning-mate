# 📚 Learning Mate

<p align="center">
  <img src="https://github.com/speedyk-005/Learning-mate/blob/main/logo.png?raw=true" alt="Learning-mate Logo" width="300"/>
</p>

<p align="center">
  Your smart learning companion, crafting courses and guiding your progress.
</p>


---

## Why I Built It

Learning Mate was created to allow learners to experience a fully automated learning workflow. The way the agent suggests courses, manages them, displays illustrations, guides you through tests, and calculates your overall performance is astonishing. I believe you’ll love it.

Currently, Learning Mate uses the Gemini model, but support for other providers may be added in the future.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/speedyk-005/Learning-mate.git
cd Learning-mate
```

2. Make sure you have Python 3.11+ and install dependencies:

```bash
pip install "google-adk>=1.15.0"
```

3. Ensure `npx` is installed for MCP tools.

4. Make the helper script executable:

```bash
chmod +x start_agent.sh
```

---

## Setup

### API Keys

Learning Mate requires the following keys:

* **Google API Key**: Used for accessing Gemini LLM for generating responses.
* **Tavily API Key (`TAVILY_API_KEY`)**: Required for web search functionality through the MCP tool.

Set them in your environment:

```bash
export GOOGLE_API_KEY="your_google_key_here"
export TAVILY_API_KEY="your_tavily_key_here"
```

---

## Running Learning Mate

A helper script is provided to simplify running the web environment with persistent storage:

```bash
./start_agent.sh
```

This script:

* Creates the necessary directories for sessions and artifacts.
* Configures persistent storage:

  * Sessions are stored in `.adk/sessions.sqlite` (SQLite database).
  * Artifacts (images, files) are stored in `.adk/artifacts`.
* Launches the ADK web server.
* Waits until the server is ready, then automatically opens the browser to:
  `http://127.0.0.1:8000/dev-ui/?app=learning_mate`.

**Advantages compared to manually calling `adk web`:**

* Avoids temporary storage (default `adk web` without flags stores sessions and artifacts in memory, lost on exit).
* Ensures directories and URIs are correctly configured.
* Automatically opens the browser when ready.

**Alternative commands (if you want to run manually):**

* CLI mode:

```bash
adk run src/learning_mate
```

* Web mode (temporary storage):

```bash
adk web "src"
```

---

## Directory Structure

```
.
├── LICENSE
├── README.md
├── src
│   └── learning_mate
│       ├── agent.py
│       ├── __init__.py
│       ├── tools  (Agents used as tools)
│       │   ├── evaluate_student.py
│       │   ├── generate_image.py
│       │   ├── generate_quiz.py
│       │   ├── plan_course.py
│       │   └── web_search.py
│       └── utils.py
└── start_agent.sh
```

---

## License

MIT License – see [LICENSE](LICENSE)
