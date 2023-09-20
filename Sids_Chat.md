# Goal
Create a UI for experimenting with LLM's and their associated plumbing

# Current Target
Provide a UI for the OpenAI API that will replicate the ChatGPT interface, allowing the user to avoid monthly fees for ChatGPT Plus.

## Objectives
    1. Use a single database so as to support moving to a public platform
    2. No security for now, as operating privately only.
    3. User provides own API key
    4. Users share a single MongoDB connection string
    5. User provides a unique userID.  Uniqueness is not monitored, so must be handled manually.
    6. Provide abilities otherwise as provided in the ChatGPT interface.

# Future Feature Thoughts

    Public Facing
    Multiple users with logins and separate work spaces
    Google Search
    Vector DB
    PDF Handling
    Text handling
    ReAct Agent
    Use sidebar controls to set model params
    Llama 2
    Llama Index
    Other Models - Hugging Face interface?
    Prompt Selection
    Bot Personality Selection
    Plugins