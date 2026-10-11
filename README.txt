VocabVault — Personal Vocabulary & English Practice

SETUP
1. Open a terminal in this folder.
2. Create and activate a virtual environment (recommended).
3. Install Django: pip install django
4. Create database tables: python manage.py makemigrations words
5. Run migrations: python manage.py migrate
6. Create an admin user if needed: python manage.py createsuperuser
7. Start the server: python manage.py runserver
8. Open http://127.0.0.1:8000/

GEMINI AI CONVERSATION + WORD ASSISTANT
1. Create a Gemini API key in Google AI Studio: https://aistudio.google.com/app/apikey
2. In the same PowerShell terminal where you run Django, set:
   $env:GEMINI_API_KEY="paste_your_real_key_here"
3. Optional model override:
   $env:GEMINI_MODEL="gemini-2.5-flash"
4. Start/restart Django in that same terminal:
   python manage.py runserver
5. Open AI Conversation from the sidebar. AI Word Assistant on Add New Word
   uses the same API key.

The key is not included in this ZIP. Keep it private and never commit it to GitHub.
If you deploy later, add GEMINI_API_KEY in your hosting provider's environment
variables instead of placing it in source code.

UI UPDATE
The shared layout and dashboard have been redesigned with a responsive editorial-style
interface, teal / warm ivory / amber accents, a persistent Light/Dark mode toggle,
responsive navigation, searchable vocabulary shortcut, refreshed stats, quick actions,
word of the day, and progress charts. Existing Django routes and template context names
are retained so the existing app features continue to connect to the redesigned UI.

Speaking practice uses browser speech features and works best in Chrome or Edge.
