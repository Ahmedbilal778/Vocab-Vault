# 📚 Vocab Vault — My Personal Vocabulary Learning Project

## 💡 Why I Built This Project

I built Vocab Vault for my personal use while practicing Django and working on my English vocabulary.

I was facing difficulties with vocabulary learning and wanted a simple platform where I could learn new words, practice English conversations, improve my speaking skills, and track my progress in one place.

Instead of relying only on existing applications, I decided to build my own solution from scratch as a personal learning project. During development, I also explored AI integration to make vocabulary learning and conversation practice more interactive.

This project helped me combine my personal learning needs with hands-on software development practice.

## ✨ What I Built

- **Vocabulary Management:** Add and manage words while learning their meanings.
- **AI Word Assistant:** Get AI-powered help with vocabulary learning.
- **AI Conversation Practice:** Practice English conversations with AI.
- **Speaking Practice:** Explore browser-based speech features.
- **Interactive Learning:** Practice vocabulary through learning activities.
- **Progress Tracking:** Keep track of learning progress and achievements.
- **User Authentication:** Access the application through user accounts.
- **Learning Dashboard:** Organize vocabulary and learning activities in one place.

## 🛠️ Technologies I Used

- Python
- Django
- HTML, CSS, JavaScript
- SQLite
- Google Gemini API
- Git and GitHub

## 🚀 Running the Project Locally

### 1. Clone the Repository

```bash
git clone https://github.com/Ahmedbilal778/Vocab-Vault.git
cd Vocab-Vault
```

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

Install Django and any additional packages required by the project.

```powershell
python -m pip install django
```

### 4. Configure AI Integration

Create a local `.env` file using `.env.example` as a reference, or configure the environment variables in PowerShell:

```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
$env:GEMINI_MODEL="gemini-2.5-flash"
```

Use your own API key for AI features. Never upload your real API key to GitHub.

### 5. Set Up the Database

```powershell
python manage.py migrate
```

### 6. Run the Application

```powershell
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## 📖 What I Learned

While building Vocab Vault, I practiced:

- Developing a web application using Django.
- Working with models, views, templates, and database migrations.
- Integrating AI-powered functionality.
- Exploring browser-based speech features.
- Setting up a local development environment.
- Using Git and GitHub to manage project code.

## 🎯 Project Purpose

Vocab Vault started as a personal solution to a learning problem and became a practical way for me to improve my development skills while building something useful for myself.

## 👨‍💻 Developer

**Ahmed Bilal**

[GitHub](https://github.com/Ahmedbilal778) : [https://github.com/Ahmedbilal778]

---

*Built for personal learning, daily practice, and continuous improvement.*
