import json, random, re
from datetime import timedelta
from django import forms
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .models import Word, PracticeLog, Profile
from .ai import gemini

class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ["word","meaning","example","synonyms","antonyms","part_of_speech",
                  "pronunciation","hindi_meaning","own_example","date_learned","difficulty"]
        widgets = {"date_learned": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
                   "example": forms.Textarea(attrs={"rows": 2}), "own_example": forms.Textarea(attrs={"rows": 2})}
    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        for n, f in self.fields.items():
            f.widget.attrs["class"] = "form-select" if n == "difficulty" else "form-control"

def streak(user):
    days = set(PracticeLog.objects.filter(user=user).values_list("date", flat=True))
    d = timezone.localdate()
    if d not in days: d -= timedelta(days=1)
    n = 0
    while d in days: n += 1; d -= timedelta(days=1)
    return n

def stats(user):
    ws = Word.objects.filter(user=user); logs = PracticeLog.objects.filter(user=user)
    total_logs = logs.count()
    acc = round(logs.filter(correct=True).count() * 100 / total_logs) if total_logs else 0
    return {"total": ws.count(), "mastered": ws.filter(box__gte=3).count(),
            "need": ws.filter(next_review__lte=timezone.localdate()).count(),
            "weak": sum(1 for w in ws if w.is_weak), "accuracy": acc, "streak": streak(user)}

def week_data(user):
    today = timezone.localdate(); labels, counts, accs = [], [], []
    for i in range(6, -1, -1):
        d = today - timedelta(days=i); q = PracticeLog.objects.filter(user=user, date=d)
        c = q.count(); labels.append(d.strftime("%a")); counts.append(c)
        accs.append(round(q.filter(correct=True).count() * 100 / c) if c else 0)
    return labels, counts, accs

@login_required
def dashboard(request):
    u = request.user; today = timezone.localdate()
    done = PracticeLog.objects.filter(user=u, date=today).count()
    goal = Profile.objects.get_or_create(user=u)[0].daily_goal
    labels, counts, accs = week_data(u)
    ctx = {"s": stats(u), "today_words": Word.objects.filter(user=u, date_learned=today),
           "wotd": Word.objects.filter(user=u).order_by("?").first(),
           "done": done, "goal": goal, "pct": min(100, done * 100 // goal),
           "week_total": sum(counts), "labels": json.dumps(labels),
           "counts": json.dumps(counts), "accs": json.dumps(accs)}
    return render(request, "words/dashboard.html", ctx)

@login_required
def vocabulary(request):
    q = request.GET.get("q", ""); ws = Word.objects.filter(user=request.user)
    if q: ws = ws.filter(Q(word__icontains=q) | Q(meaning__icontains=q) | Q(hindi_meaning__icontains=q))
    return render(request, "words/vocabulary.html", {"words": ws, "q": q})

@login_required
def add_word(request):
    form = WordForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        w = form.save(commit=False); w.user = request.user; w.save()
        return redirect("vocabulary")
    return render(request, "words/add.html", {"form": form})

@login_required
def delete_word(request, pk):
    if request.method == "POST": get_object_or_404(Word, pk=pk, user=request.user).delete()
    return redirect("vocabulary")

MODES = [("mcq", "Multiple Choice", "What does the word mean?"),
         ("fill", "Fill in the Blank", "Complete the example sentence."),
         ("w2m", "Word → Meaning", "Type the meaning of the word."),
         ("m2w", "Meaning → Word", "Type the word for the meaning.")]

@login_required
def zone(request):
    return render(request, "words/zone.html", {"modes": MODES, "due": False})

@login_required
def revision(request):
    n = Word.objects.filter(user=request.user, next_review__lte=timezone.localdate()).count()
    return render(request, "words/zone.html", {"modes": MODES, "due": True, "due_count": n})

def check(w, mode, a):
    a = a.strip().lower()
    if mode in ("fill", "m2w"): return a == w.word.lower()
    m = w.meaning.lower()
    if mode == "mcq": return a == m
    toks = {t for t in re.findall(r"\w+", m) if len(t) > 3} | {s.strip().lower() for s in w.synonyms.split(",") if s.strip()}
    return a == m or bool(set(re.findall(r"\w+", a)) & toks)

@login_required
def play(request):
    r = request.POST if request.method == "POST" else request.GET
    mode = r.get("mode", "mcq"); due = r.get("due") == "1"; ctx = {"mode": mode, "due": due}
    if request.method == "POST":
        w = get_object_or_404(Word, pk=r["wid"], user=request.user)
        ok = check(w, mode, r.get("answer", "")); w.record(ok)
        ctx.update(result=True, ok=ok, w=w, answer=r.get("answer", ""))
        return render(request, "words/play.html", ctx)
    ws = list(Word.objects.filter(user=request.user))
    if due: ws = [w for w in ws if w.next_review <= timezone.localdate()]
    if mode == "fill": ws = [w for w in ws if re.search(re.escape(w.word), w.example, re.I)]
    if not ws:
        return render(request, "words/play.html", {**ctx, "empty": True})
    w = random.choice(ws); ctx["w"] = w
    if mode == "mcq":
        others = list(Word.objects.filter(user=request.user).exclude(pk=w.pk).values_list("meaning", flat=True))
        opts = random.sample(others, min(3, len(others))) + [w.meaning]; random.shuffle(opts); ctx["options"] = opts
    if mode == "fill":
        ctx["blank"] = re.sub(re.escape(w.word), "______", w.example, flags=re.I)
    return render(request, "words/play.html", ctx)

@login_required
def progress(request):
    labels, counts, accs = week_data(request.user)
    return render(request, "words/progress.html", {"s": stats(request.user), "labels": json.dumps(labels),
        "counts": json.dumps(counts), "accs": json.dumps(accs), "week_total": sum(counts),
        "weak_words": [w for w in Word.objects.filter(user=request.user) if w.is_weak]})


from django.http import JsonResponse
from django.views.decorators.http import require_POST

@login_required
@require_POST
def ai_word(request):
    word = request.POST.get("word", "").strip()
    if not word: return JsonResponse({"error": "Enter a word first."}, status=400)
    keys = "meaning, hindi_meaning, example, synonyms, antonyms, part_of_speech, pronunciation, common_usage, difficulty (easy|medium|hard), conversation_example"
    p = f'Give vocabulary details for the English word "{word}" as JSON with keys: {keys}. synonyms and antonyms are comma-separated strings. hindi_meaning is in Devanagari.'
    if request.POST.get("easier"):
        p += " Use very simple English a beginner understands. The example sentence must use very easy words."
    try:
        data = json.loads(gemini([{"role": "user", "parts": [{"text": p}]}], as_json=True))
        if isinstance(data, list): data = data[0]
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

@login_required
def conversation(request):
    return render(request, "words/conversation.html")

@login_required
@require_POST
def ai_chat(request):
    u = request.user; today = timezone.localdate()
    ws = list(Word.objects.filter(user=u, date_learned=today)) or list(Word.objects.filter(user=u)[:5])
    names = ", ".join(w.word for w in ws) or "none yet"
    system = ("You are a friendly English conversation partner. Keep replies to 1-3 short sentences and ask one question at a time. "
              f"Naturally steer the chat so the learner gets chances to use these words: {names}. "
              "If the learner makes a grammar mistake, add one short gentle correction at the end.")
    try:
        payload = json.loads(request.body or b"{}")
        hist = payload.get("history", [])
        if not isinstance(hist, list):
            return JsonResponse({"error": "Conversation history was invalid. Start a new chat and try again."}, status=400)
        contents = []
        for item in hist[-16:]:
            if not isinstance(item, dict) or item.get("role") not in ("user", "model"):
                continue
            text = str(item.get("text", "")).strip()[:1200]
            if text:
                contents.append({"role": item["role"], "parts": [{"text": text}]})
        if not contents or contents[-1]["role"] != "user":
            return JsonResponse({"error": "Type a message to continue the conversation."}, status=400)
        return JsonResponse({"reply": gemini(contents, system), "words": names})
    except json.JSONDecodeError:
        return JsonResponse({"error": "Message format was invalid. Please try again."}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e) or "AI service error. Please try again."}, status=503)

@login_required
def speaking(request):
    ws = [w for w in Word.objects.filter(user=request.user) if w.own_example or w.example]
    w = random.choice(ws) if ws else None
    sentence = (w.own_example or w.example) if w else ""
    return render(request, "words/speaking.html", {"w": w, "sentence": json.dumps(sentence)})

@login_required
def achievements(request):
    u = request.user; s = stats(u); n = PracticeLog.objects.filter(user=u).count()
    defs = [("First Word", "Add your first word", "bi-flower1", s["total"] >= 1),
            ("Ten Words", "Learn 10 words", "bi-journal-check", s["total"] >= 10),
            ("Fifty Words", "Learn 50 words", "bi-collection", s["total"] >= 50),
            ("Hundred Words", "Learn 100 words", "bi-award", s["total"] >= 100),
            ("Ten Mastered", "Master 10 words", "bi-trophy", s["mastered"] >= 10),
            ("100 Answers", "Answer 100 practice questions", "bi-lightning-charge", n >= 100),
            ("Sharp Mind", "80%+ accuracy over 20+ answers", "bi-bullseye", n >= 20 and s["accuracy"] >= 80),
            ("7-Day Streak", "Practice 7 days in a row", "bi-fire", s["streak"] >= 7),
            ("30-Day Streak", "Practice 30 days in a row", "bi-fire", s["streak"] >= 30)]
    return render(request, "words/achievements.html", {"defs": defs})

@login_required
def settings_page(request):
    p = Profile.objects.get_or_create(user=request.user)[0]
    if request.method == "POST":
        try: p.daily_goal = max(1, min(200, int(request.POST.get("daily_goal", 10))))
        except ValueError: pass
        p.save(); return redirect("settings")
    return render(request, "words/settings.html", {"p": p})
