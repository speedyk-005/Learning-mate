# Learning Mate Tests

The `test.py` script serves as a crucial **integration test** for the **Learning Mate** system. It executes a predefined sequence of user queries to simulate a complete learning session, ensuring the agent's core functionalities—planning, context management, and state tracking—work correctly in sequence.

This test is designed to run from within the project's development environment.

## ⚠️ Prerequisites and Setup

> [!CAUTION]
> Before running this test, please ensure you have completed the necessary project setup:
>
> * **Installation:** Verify that all Python dependencies are installed. Please check the main project documentation for required packages (e.g., `google-adk`).
>     * [Installation](https://github.com/speedyk-005/Learning-mate#installation)
>
> * **Setup:** Verify that your environment is properly configured, especially your API keys and project paths.
>     * [Setup](https://github.com/speedyk-005/Learning-mate?tab=readme-ov-file#setup)

## 🏃 Running the Test

1.  Navigate to the root directory of the project (`~/pr/learning_mate`).
2.  Activate your virtual environment: `source .venv/bin/activate` (or equivalent).
3.  Execute the test script directly from the project root:

    ```bash
    python tests/test.py
    ```

## 📝 Test Scenario: Quantum Computing Journey

This test simulates a user starting a new subject, managing their study materials, and updating their progress.

### Expected Flow and Success Criteria

The test runs through the following six conversational turns:

| Step | User Query | Expected Agent Action | Success Criteria |
| :--- | :--- | :--- | :--- |
| **1 (Setup)** | `I need to learn the core concepts of quantum computing, starting from the basics.` | The agent initializes the course plan (often a **silent function call**). | **Success:** Agent logs a `function_call` event and establishes the **Quantum Computing** curriculum state. |
| **2 (Planning)** | `Can you break down the first two concepts into small, actionable lessons?` | Agent fetches and delivers the content for the first lesson, respecting the curriculum flow. | **Success:** Agent provides Lesson 1.1 content. |
| **3 (Context Check)** | `Provide me with the content for the first lesson on 'Superposition'.` | Agent checks prerequisites and denies the request. | **Success:** Agent responds by explaining that Unit 1 must be completed first. |
| **4 (Guidance)** | `Based on my progress, what should my personalized plan look like for the rest of the week?` | Agent uses the current state (Lesson 1.1 complete) to generate a customized schedule. | **Success:** Agent provides a detailed weekly study roadmap. |
| **5 (State Change)** | `I've finished the 'Entanglement' lesson. Mark that task as complete.` | Agent successfully calls the internal state-tracking tool. | **Success:** Agent confirms completion and updates the user's progress record. |
| **6 (Next Step)** | `What's the next step in my learning path?` | Agent uses the updated progress to suggest the logical next lesson. | **Success:** Agent suggests **Unit 2, Lesson 2.5: No-Cloning Theorem**. |

> [!NOTE]
> **Output for Step 1:** The `Warning` and `None` output for the first query is **expected** behavior for a well-designed agent that uses a **Tool Call** as its initial response (e.g., calling a `plan_course` tool) instead of returning text directly. This means the agent is successfully executing an internal action, not failing.
