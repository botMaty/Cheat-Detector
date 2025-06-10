<h1>🕵️ Cheat Detector</h1>

<p>
  A simple yet effective Flask-based plagiarism detection tool that uses <strong>TF-IDF</strong> and <strong>Cosine Similarity</strong> to compare student answers and identify potential cheating.
</p>

<h2>📌 Overview</h2>
<p>This project allows you to:</p>
<ul>
  <li>Upload student answer sheets (as a JSON file)</li>
  <li>Automatically compute similarity between each pair of answers</li>
  <li>Detect pairs with high similarity, indicating potential cheating</li>
</ul>
<p>Built with:
  <ul>
    <li>Python 3.x</li>
    <li>Flask</li>
    <li>scikit-learn</li>
  </ul>
</p>

<hr>

<h2>🚀 Features</h2>
<ul>
  <li>Lightweight and fast local web app</li>
  <li>Uses <strong>TF-IDF Vectorization</strong> and <strong>Cosine Similarity</strong></li>
  <li>Visual display of most similar pairs</li>
  <li>Easy to use: no database or heavy setup required</li>
</ul>

<hr>

<h2>📁 File Structure</h2>
<pre>
Cheat-Detector/
│
├── app.py                # Main Flask application
├── detect.py             # Core detection logic using TF-IDF and cosine similarity
├── templates/
│   └── index.html        # Web interface (upload form + results)
├── static/
│   └── styles.css        # Custom CSS (optional)
├── students.json         # Sample student data
├── README.md             # Project documentation
└── requirements.txt      # Dependencies
</pre>

<hr>

<h2>🛠️ Installation</h2>

<ol>
  <li><strong>Clone the repository</strong>
    <pre><code>git clone https://github.com/botMaty/Cheat-Detector.git
cd Cheat-Detector</code></pre>
  </li>

  <li><strong>Create a virtual environment (optional but recommended)</strong>
    <pre><code>python -m venv venv
source venv/bin/activate  # On Windows use venv\Scripts\activate</code></pre>
  </li>

  <li><strong>Install dependencies</strong>
    <pre><code>pip install -r requirements.txt</code></pre>
  </li>

  <li><strong>Run the Flask app</strong>
    <pre><code>python app.py</code></pre>
  </li>

  <li><strong>Open your browser</strong> and go to <a href="http://127.0.0.1:5000">http://127.0.0.1:5000</a>
  </li>
</ol>

<hr>

<h2>📄 JSON Input Format</h2>
<p>The input JSON file should follow this structure:</p>
<pre><code>[
  {
    "id": "Student1",
    "answer": "This is the answer of student 1"
  },
  {
    "id": "Student2",
    "answer": "This is a slightly different answer from student 2"
  }
]</code></pre>
<p>Upload this file via the web interface to run the detection.</p>

<hr>

<h2>📊 How It Works</h2>
<ul>
  <li><strong>TF-IDF Vectorizer:</strong> Converts student answers into numerical vectors, weighing terms based on frequency and uniqueness.</li>
  <li><strong>Cosine Similarity:</strong> Measures how close the answers are in vector space.</li>
  <li>The app returns a sorted list of answer pairs with their similarity scores (from 0 to 1).</li>
</ul>

<hr>

<h2>✅ Example</h2>
<p>Given the following two answers:</p>
<pre><code>
Answer 1: "Machine learning is a subfield of AI."
Answer 2: "AI includes machine learning."
</code></pre>
<p>The system will compute a high similarity score due to overlapping terms.</p>

<hr>

<h2>📌 To-Do / Improvements</h2>
<ul>
  <li>Add threshold filtering (e.g., only show similarity &gt; 0.7)</li>
  <li>Export results as CSV</li>
  <li>Add support for more file types (CSV, TXT)</li>
  <li>Highlight plagiarized sections</li>
</ul>

<hr>

<h2>🤝 Contributing</h2>
<p>Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.</p>

<hr>

<h2>📜 License</h2>
<p>This project is licensed under the <strong>MIT License</strong>. See the <a href="LICENSE">LICENSE</a> file for details.</p>

<hr>

<h2>✨ Acknowledgements</h2>
<p>Thanks to the open-source community for providing great libraries like Flask and scikit-learn that make projects like this possible.</p>

<hr>

<h2>👨‍💻 Authors</h2>
<ul>
  <li><a href="https://github.com/botMaty">@botMaty</a></li>
  <li><a href="https://github.com/iam4m1n">@iam4m1n</a></li>
</ul>

<hr>

<h2>📬 Contact</h2>
<p>Made with ❤️ by <a href="https://github.com/botMaty">@botMaty</a> and <a href="https://github.com/iam4m1n">@iam4m1n</a></p>
