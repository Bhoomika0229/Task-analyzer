🌟 Smart Task Analyzer

A simple and smart task-management web application built using Django, HTML/CSS, and JavaScript.
Users can add tasks, view them, and generate suggested tasks on a separate results page.

🚀 Features
✔ Add New Tasks

Title

Due Date

Estimated Hours

Importance (1–10)

✔ View Current Task List

All added tasks are displayed in an organized list.

✔ Task Suggestion Engine

Click "Suggest Tasks" → Navigate to a new page showing recommended tasks.

✔ Two-Page UI

Page 1: Add tasks

Page 2: View suggested tasks

✔ Static Files Integrated

CSS and JS are loaded through Django’s {% static %} tags.

🛠 Tech Stack
Component	Technology
Backend	Django 5
Frontend	HTML, CSS, JavaScript
Storage	LocalStorage (Frontend), Django (extendable)
Deployment	Railway / Render (optional)
📂 Project Structure
project-root/
│
├── backend/                  # Django backend (settings, urls, views)
│── frontend/
│     ├── index.html          # Add tasks page
│     ├── suggestions.html    # Suggested tasks page
│     └── static/
│           ├── styles.css
│           └── script.js
│
└── README.md

⚙️ Setup Instructions
1️⃣ Clone the Repository
git clone https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
cd YOUR_REPO_NAME

2️⃣ Create Virtual Environment
python -m venv myenv
myenv\Scripts\activate   # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

4️⃣ Run Server
python manage.py runserver

5️⃣ Open in Browser
http://127.0.0.1:8000/

📘 Author
Created by: Bhoomika K R
😊 Always learning. Always building.

⭐ Feedback & Contributions

Contributions are welcome!
If you find a bug or want an enhancement, open an issue or PR.
