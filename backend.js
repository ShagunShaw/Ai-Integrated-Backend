import express from "express";
import axios from "axios";

const app = express();
app.use(express.json());

// Route to handle frontend requests
app.post("/ask-ai", async (req, res) => {
  try {
      const { query } = req.body;

    // Forward request to Flask service
    const flaskResponse = await axios.post("http://localhost:5000/ask", {
      query: query,
    });
    
    res.json({
      aiResponse: flaskResponse.data.response,
    });
  } catch (error) {
    console.error("Error:", error.message);
    res.status(500).json({ error: "Something went wrong: ", error });
  }
});

app.listen(3000, () => {
  console.log("Node.js backend running on http://localhost:3000");
});