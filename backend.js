import express from "express";
import axios from "axios";
import multer from "multer";

const app = express();
app.use(express.json());
app.use(express.urlencoded({extended: true}))


const storage = multer.memoryStorage();
const upload = multer({ 
  storage: storage,
  fileFilter: (req, file, cb) => {
    // Accept only image files
    if (file.mimetype.startsWith('image/')) {
      cb(null, true);
    } else {
      cb(new Error('Only image files are allowed'), false);
    }
  }
});


app.post("/ask-ai", upload.single('image'), async (req, res) => {
  try {
    if (!req.file) {
      return res.status(400).json({ error: 'No image uploaded' });
    }

    const fileBase64 = req.file.buffer.toString('base64');

    // Calling the python API
    const response = await axios.post('http://localhost:8000/process-image', {
      image: fileBase64,
      filename: req.file.originalname,
      mimetype: req.file.mimetype
    });

    if (response.data.error) {
      return res.status(500).json({ error: 'Error from Python API', details: response.data.error });
    }

    if (response.data.status === "not verified") {
      return res.status(400).json({ error: 'Failed to process image, as the uploaded image is not a certificate' });
    }

    return res.status(200).json(response.data);

  } catch (err) {
    return res.status(500).json({ error: 'Failed to process image in Node.js', details: err.message });
  }
});

app.get("/", (req, res) => res.send("Node.js Backend is running"));

app.listen(3000, () => {
  console.log("Node.js backend running on http://localhost:3000");
});