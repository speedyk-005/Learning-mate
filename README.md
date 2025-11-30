# 📚 Learning Mate

<p align="center">
  <img src="https://github.com/speedyk-005/Learning-mate/blob/main/images/logo.png?raw=true" alt="Learning-mate Logo" width="300"/>
</p>

<p align="center">
  Your smart learning companion, crafting courses and guiding your progress.
</p>

---

## Why I Built It

Modern learners jump between tutorials, courses, apps, and videos, yet few systems manage the entire learning process in a structured and adaptive way. Learners often assemble their own workflow: one place to learn, another to practice, another to track progress, with none of it adjusting to their goals or performance.

Learning Mate was created to unify that workflow.

It automates the full learning pipeline: planning a learning path, generating complete courses through a dedicated teaching agent, guiding the learner through lessons, quizzes, and illustrations, and evaluating performance with structured feedback. The system handles organization and coordination so the learner can focus on understanding the material.

Learning Mate provides a personalized, organized, and intelligent learning experience with zero manual setup.

> [!NOTE]
> Learning Mate currently uses the Gemini model, with planned support for additional AI providers.

---

## Features

* **Automated & Interactive Course Creation**
  Generates full courses, including structured lessons, quizzes, illustrations, and exercises, through a teaching agent.

* **Personalized Course Suggestions**
  Recommends learning paths based on user goals, interests, and initial questions.

* **Adaptive Learning Flow**
  Guides learners step-by-step, evaluates answers, and adjusts difficulty accordingly.

* **Built-in Assessment Engine**
  Generates quizzes, checks responses, scores performance, and tracks mastery.

* **Visual Explanations**
  Produces illustrations to simplify and clarify concepts.

* **Web-Powered Insights**
  Integrates web search to ensure current and reliable information.

* **Persistent Session Management**
  Saves history, artifacts, and progress for consistent long-term use.

* **Modular Multi-Agent Architecture**
  Separates responsibilities across planning, generation, search, evaluation, and imagery agents.

---

## System Architecture Flow

The system operates under a clear hierarchical structure anchored by the **`smart_friend_agent`** (the primary user interface). This root agent delegates complex instructional tasks to the **`teacher_agent`**. The `teacher_agent` serves as the core educational workflow manager, **maintaining direct access to all the same core utilities as the root agent** (including `web_search_agent`, `image_generation_agent`, and `load_memory`). Furthermore, the `teacher_agent` orchestrates the sequential phases of learning by delegating specialized functions to the **`course_planning_agent`**, **`quiz_generation_agent`**, and **`answer_evaluation_agent`**.

---

## Diagram

<p align="left">
  <img src="https://github.com/speedyk-005/Learning-mate/blob/main/images/diagram.png?raw=true" width="600"/>
</p>

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/speedyk-005/Learning-mate.git
cd Learning-mate
```

2. Install dependencies (Python 3.11+ required):

```bash
pip install "google-adk>=1.15.0"
```

3. Ensure `npx` is installed for MCP tools.
   Guide: [https://gist.github.com/cwsmith-160/e9c8ca80f23027f0495775aed77ec780#file-node_npx_install-md](https://gist.github.com/cwsmith-160/e9c8ca80f23027f0495775aed77ec780#file-node_npx_install-md)

4. Make the helper script executable:

```bash
chmod +x start_agent.sh
```

---

## Setup

### API Keys

Learning Mate requires:

* **Google API Key** – for Gemini LLM
  **Get yours:** [https://aistudio.google.com/app/api-keys](https://aistudio.google.com/app/api-keys)

* **Tavily API Key** – for web search via MCP
  **Get yours:** [https://app.tavily.com/home](https://app.tavily.com/home)

You can set them in your .env file (modify and rename .env.example file to .env) or set them directly in your shell. For example:

```bash
export GOOGLE_API_KEY="your_google_key_here"
export TAVILY_API_KEY="your_tavily_key_here"
```

---

## Running Learning Mate

Use the helper script:

```bash
./start_agent.sh
```

This script:

* Creates directories for sessions and artifacts.
* Configures storage:

  * `.adk/sessions.sqlite` — session history
  * `.adk/artifacts/` — generated images and files
* Starts the ADK web server.
* Opens the development UI at:
  `http://127.0.0.1:8000/dev-ui/?app=learning_mate`

### Alternative Commands

CLI mode:

```bash
adk run src/learning_mate
```

Web mode (temporary storage):

```bash
adk web "src"
```
---

## Screenshots

### CLI (Screenshot 0)

<p align="left">
  <img src="https://github.com/speedyk-005/Learning-mate/blob/main/images/Screenshot_0.png?raw=true" width="600"/>
</p>

---

### Web ui (Screenshot 1-4)

<details>
  <summary>Click to see</summary>

  <img src="https://github.com/speedyk-005/Learning-mate/blob/main/images/Screenshot_1.png?raw=true" width="600"/>

  <img src="https://github.com/speedyk-005/Learning-mate/blob/main/images/Screenshot_2.png?raw=true" width="600"/>

  <img src="https://github.com/speedyk-005/Learning-mate/blob/main/images/Screenshot_3.png?raw=true" width="600"/>

  <img src="https://github.com/speedyk-005/Learning-mate/blob/main/images/Screenshot_4.png?raw=true" width="600"/>

</details>

---

## Directory Structure

```
.
├── images
│   ├── diagram.png
│   ├── logo.png
│   ├── Screenshot_0.png
│   ├── Screenshot_1.png
│   ├── Screenshot_2.png
│   ├── Screenshot_3.png
│   └── Screenshot_4.png
├── LICENSE
├── README.md
├── src
│   └── learning_mate
│       ├── agent.py
│       ├── __init__.py
│       ├── __pycache__/
│       ├── sub_agents
│       │   ├── answer_evaluation_agent.py
│       │   ├── course_planning_agent.py
│       │   ├── image_generation_agent.py
│       │   ├── quiz_generation_agent.py
│       │   └── web_search_agent.py
│       └── utils.py
├── .adk/ (Created automatically the first time you run ./start_agent)
└── start_agent.sh
```

---

## License

MIT License — see `LICENSE`.
