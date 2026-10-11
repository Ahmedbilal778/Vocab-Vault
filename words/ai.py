import json
import urllib.error
import urllib.parse
import urllib.request
from django.conf import settings


def gemini(contents, system="", as_json=False):
    api_key = getattr(settings, "GEMINI_API_KEY", "").strip()
    model = getattr(settings, "GEMINI_MODEL", "gemini-2.5-flash").strip()
    if not api_key:
        raise RuntimeError(
            "Gemini API key is not configured. Create a .env file beside manage.py "
            "with GEMINI_API_KEY=your_actual_key, then restart the Django server."
        )

    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        + urllib.parse.quote(model, safe="")
        + ":generateContent?key="
        + urllib.parse.quote(api_key, safe="")
    )
    body = {"contents": contents}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    if as_json:
        body["generationConfig"] = {"responseMimeType": "application/json"}

    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            payload = json.loads(exc.read().decode("utf-8"))
            detail = payload.get("error", {}).get("message", "")
        except Exception:
            detail = ""
        if exc.code in (400, 401, 403):
            raise RuntimeError(
                "Gemini rejected the request (HTTP %s). Check that the API key is valid, "
                "the Generative Language API is enabled, and the model name is correct. %s"
                % (exc.code, detail[:350])
            ) from None
        if exc.code == 404:
            raise RuntimeError(
                "Gemini model was not found. Check GEMINI_MODEL in .env (try gemini-2.5-flash). "
                + detail[:250]
            ) from None
        if exc.code == 429:
            raise RuntimeError(
                "Gemini quota/rate limit reached. Check API quota/billing or wait and retry. "
                + detail[:250]
            ) from None
        raise RuntimeError("Gemini service error (HTTP %s). %s" % (exc.code, detail[:300])) from None
    except (urllib.error.URLError, TimeoutError) as exc:
        reason = getattr(exc, "reason", "")
        raise RuntimeError("Could not connect to Gemini. Check internet/firewall and try again. " + str(reason)[:180]) from None
    except json.JSONDecodeError:
        raise RuntimeError("Gemini returned an unreadable response. Please retry.") from None

    candidates = data.get("candidates") or []
    if not candidates:
        feedback = data.get("promptFeedback", {}).get("blockReason", "")
        raise RuntimeError("Gemini returned no answer. " + ("Request blocked: " + feedback if feedback else "Try a different message."))
    parts = candidates[0].get("content", {}).get("parts", [])
    answer = "".join(part.get("text", "") for part in parts if isinstance(part, dict))
    if not answer.strip():
        raise RuntimeError("Gemini returned an empty answer. Please send your message again.")
    return answer
