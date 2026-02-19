import 'dotenv/config';
import express from "express";
import cors from "cors";
import { CohereClientV2 } from "cohere-ai";

console.log(">>> USING COHERE FOR /api/submit-answers (TEXT FEEDBACK) <<<");

const cohere = new CohereClientV2({
  token: process.env.COHERE_API_KEY,
});

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

// Root route
app.get("/", (req, res) => {
  res.json({ message: "AI Interview Coach backend is running" });
});

// Main route: Cohere gives text feedback; backend wraps it
app.post("/api/submit-answers", async (req, res) => {
  const { jd_text, qa_list } = req.body;

  console.log("Received JD length:", jd_text ? jd_text.length : 0);
  console.log("Received QA count:", Array.isArray(qa_list) ? qa_list.length : 0);
  console.log("DEBUG body:", JSON.stringify(req.body, null, 2));

  try {
    const message =
      "You are an interview coach. Read the job description and the candidate's answers. " +
      "For each answer, give short feedback in 1-2 sentences. " +
      "Do NOT return JSON, just plain text paragraphs.\n\n" +
      "Job description:\n" +
      (jd_text || "") +
      "\n\nQuestions and answers:\n" +
      JSON.stringify(qa_list || [], null, 2);

    const response = await cohere.chat({
      model: "command-a-03-2025",
      messages: [
        {
          role: "user",
          content: message,
        },
      ],
      temperature: 0.3,
    });

    const aiText = response?.message?.content?.[0]?.text ?? "";
    console.log("COHERE RAW TEXT:", aiText);

    // Simple mapping: give same dummy scores, attach AI text as feedback note
    const items = (qa_list || []).map((item, index) => ({
      question_number: index + 1,
      question: item.question,
      answer: item.answer,
      scores: {
        relevance: 7,
        depth: 7,
        structure: 7,
        keyword_match: 7,
      },
      feedback: [
        "Automatic scores are basic (not detailed yet).",
        "AI coach overall comments: " + aiText,
      ],
    }));

    const result = {
      status: "ok",
      total_questions: items.length,
      items,
      message: "AI feedback text from Cohere attached to each answer.",
    };

    console.log("DEBUG result:", JSON.stringify(result, null, 2));
    res.json(result);
  } catch (err) {
    console.error("Cohere error in /api/submit-answers:", err);

    const evaluated = (qa_list || []).map((item, index) => ({
      question_number: index + 1,
      question: item.question,
      answer: item.answer,
      scores: {
        relevance: 7,
        depth: 7,
        structure: 7,
        keyword_match: 7,
      },
      feedback: [
  "Scores are auto-generated at a baseline level; focus mainly on the AI coach comments.",
  "Overall AI coach comments on your interview:",
  aiText,
],

    }));

    return res.status(200).json({
      status: "fallback",
      total_questions: evaluated.length,
      items: evaluated,
      message: "Cohere error; using fallback scoring.",
    });
  }
});

// Route list for debugging
app.get("/debug-routes", (req, res) => {
  const routes = app._router.stack
    .filter(r => r.route)
    .map(r => ({
      path: r.route.path,
      methods: Object.keys(r.route.methods),
    }));
  res.json(routes);
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
