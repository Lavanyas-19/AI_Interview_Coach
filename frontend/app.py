import streamlit as st
import requests
import pandas as pd
import plotly.express as px  # for interactive charts

BACKEND_URL = "http://localhost:3000"

st.title("AI Interview Coach")

st.subheader("Step 1: Paste Job Description")
jd_text = st.text_area("Job Description", height=200, placeholder="Paste the JD here...")

st.subheader("Step 2: Generate mock questions")

# Initialize questions in session state
if "questions" not in st.session_state:
    st.session_state["questions"] = []

# Button 1: generate questions
if st.button("Generate Questions", key="btn_generate"):
    if not jd_text.strip():
        st.warning("Please paste a Job Description first.")
    else:
        questions = [
            "Tell me about yourself.",
            "Walk me through a recent project you worked on.",
            "What are your key strengths relevant to this job?",
            "Describe a challenge you faced and how you solved it.",
            "Why do you want to work in this role?"
        ]
        st.session_state["questions"] = questions
        st.success("Generated 5 mock questions (dummy for now).")

questions = st.session_state["questions"]

# Step 3: answers + submit (inside a form → only one submit button)
if questions:
    st.subheader("Step 3: Type your answers")

    with st.form("answers_form"):
        qa_list = []
        for i, q in enumerate(questions, start=1):
            st.write(f"Q{i}: {q}")
            ans = st.text_area(f"Your answer to Q{i}", key=f"answer_{i}", height=120)
            qa_list.append({"question": q, "answer": ans})

        submit = st.form_submit_button("Submit all answers")

    if submit:
        try:
            with st.spinner("Evaluating your answers..."):
                payload = {
                "jd_text": jd_text,
                "qa_list": qa_list
            }
            response = requests.post(f"{BACKEND_URL}/api/submit-answers", json=payload)
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                st.success(
                    f"Backend evaluated {data.get('total_questions')} answers."
                )

                # Overall summary scores
                if items:
                    total_rel = total_depth = total_struct = total_kw = 0
                    for item in items:
                        scores = item["scores"]
                        total_rel += scores["relevance"]
                        total_depth += scores["depth"]
                        total_struct += scores["structure"]
                        total_kw += scores["keyword_match"]

                    n = len(items)
                    avg_rel = round(total_rel / n, 1)
                    avg_depth = round(total_depth / n, 1)
                    avg_struct = round(total_struct / n, 1)
                    avg_kw = round(total_kw / n, 1)

                    st.markdown("## Overall Interview Summary")
                    st.write(
                        f"- Average Relevance: {avg_rel}/10\n"
                        f"- Average Depth: {avg_depth}/10\n"
                        f"- Average Structure: {avg_struct}/10\n"
                        f"- Average Keyword Match: {avg_kw}/10"
                    )

                    st.info(
                        "Note: Scores are currently basic (all 7/10). "
                        "The detailed evaluation comes from the AI coach comments below."
                    )

                    # Build DataFrame for charts
                    scores_df = pd.DataFrame({
                        "Metric": ["Relevance", "Depth", "Structure", "Keyword Match"],
                        "Score": [avg_rel, avg_depth, avg_struct, avg_kw],
                    })

                    # Bar chart
                    st.markdown("## Score Breakdown (Bar Chart)")
                    bar_fig = px.bar(
                        scores_df,
                        x="Metric",
                        y="Score",
                        range_y=[0, 10],
                        text="Score",
                        color="Metric",
                    )
                    bar_fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
                    st.plotly_chart(bar_fig, use_container_width=True)

                    # Radar chart
                    st.markdown("## Skill Profile (Radar Chart)")
                    radar_fig = px.line_polar(
                        scores_df,
                        r="Score",
                        theta="Metric",
                        line_close=True,
                        range_r=[0, 10],
                    )
                    radar_fig.update_traces(fill="toself")
                    st.plotly_chart(radar_fig, use_container_width=True)

                    # Overall AI coach comments (show once)
                    st.markdown("## AI Coach Overall Comments")
                    overall_comments = items[0]["feedback"][-1]
                    st.write(overall_comments)

                # Detailed per-question feedback
                st.markdown("## Detailed Feedback")
                for item in items:
                    st.markdown(f"### Result for Q{item['question_number']}")
                    st.write(f"**Question:** {item['question']}")
                    st.write(f"**Your answer:** {item['answer']}")
                    scores = item["scores"]
                    st.write(
                        f"Scores → Relevance: {scores['relevance']}/10, "
                        f"Depth: {scores['depth']}/10, "
                        f"Structure: {scores['structure']}/10, "
                        f"Keyword match: {scores['keyword_match']}/10"
                    )
                    st.write("**Feedback:**")
                    # Show only the first (short) feedback line per question
                    if item["feedback"]:
                        st.write(f"- {item['feedback'][0]}")
                    st.markdown("---")
            else:
                st.error(f"Backend error. Status: {response.status_code}")
        except Exception as e:
            st.error(f"Could not reach backend: {e}")

# Reset button
st.markdown("---")
if st.button("Start a new interview", key="btn_reset"):
    st.session_state["questions"] = []
    st.rerun()
