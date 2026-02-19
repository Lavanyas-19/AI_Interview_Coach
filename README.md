# AI Interview Coach

AI-powered mock interview coach built with Streamlit and Node.js, generating feedback from your answers using LLMs.

---

##  Features

- Paste a job description and get role-relevant mock questions.
- Answer all questions in a clean Streamlit UI.
- Backend evaluates each answer and returns:
  - Relevance
  - Depth
  - Structure
  - Keyword match
- Generates **AI coach feedback** using a large language model.
- Visualizes your performance with interactive Plotly charts (bar + radar).
- “Start a new interview” button to quickly reset and practice again.

---

##  Tech Stack

- **Frontend:** Python, Streamlit, Plotly
- **Backend:** Node.js, Express
- **AI:** LLM (via Cohere API) for feedback generation
- **Other:** REST API, JSON payloads, `.env` for secrets

---

##  Project Structure

```text
AI_Interview_Coach/
├─ backend/
│  ├─ index.js          # Express server + AI evaluation logic
│  ├─ package.json      # Backend dependencies and scripts
│  └─ .env              # Cohere API key (NOT committed to Git)
└─ frontend/
   └─ app.py            # Streamlit UI + charts

