VOCABVAULT GEMINI AI SETUP (Windows / VS Code)

1. Get an API key from https://aistudio.google.com/app/apikey
2. In the same folder as manage.py, copy .env.example to a new file named .env
3. Open .env and set:
   GEMINI_API_KEY=your_actual_key_here
   GEMINI_MODEL=gemini-2.5-flash
   Do not include quotes. Do not share this file or commit it to GitHub.
4. Stop Django using Ctrl+C, then restart: python manage.py runserver
5. Sign in, open AI Conversation and send a message.

If it fails, the page now shows a more specific API error. Common meanings:
- API key not configured: .env is missing, wrongly named (.env.txt), or in the wrong folder.
- HTTP 400/403: key/API access/model request needs checking.
- HTTP 404: model name is unavailable; try gemini-2.5-flash.
- HTTP 429: API quota/rate limit reached.
- Connection error: check internet/firewall.

If Windows hides extensions, ensure the file is named exactly .env, not .env.txt.
