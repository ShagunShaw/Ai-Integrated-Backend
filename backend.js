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
    const response = await axios.post('http://localhost:5000/process-image', {
      image: fileBase64,
      filename: req.file.originalname,
      mimetype: req.file.mimetype
    });


    return res.json(response.data);

  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: 'Failed to process image', details: err.message });
  }
});

app.listen(3000, () => {
  console.log("Node.js backend running on http://localhost:3000");
});