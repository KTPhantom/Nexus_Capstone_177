import os, time, sys
from google import genai
from google.genai import types

sys.stdout.reconfigure(encoding='utf-8')

api_key = os.environ.get("GEMINI_API_KEY", "")
print(f"API key set: {bool(api_key)}", flush=True)

client = genai.Client(api_key=api_key)

test_models = [
    'gemini-2.5-flash',
    'gemma-4-26b-a4b-it',
    'gemini-2.5-flash-lite',
    'gemini-3-flash-preview',
    'gemma-4-31b-it',
]

print("Testing available models from user quota table...", flush=True)
for m in test_models:
    print(f"Testing {m}...", end="", flush=True)
    try:
        t0 = time.time()
        r = client.models.generate_content(
            model=m,
            contents='Return a JSON object with key "status" and value "ok".',
            config=types.GenerateContentConfig(
                response_mime_type='application/json'
            )
        )
        print(f" SUCCESS in {(time.time()-t0)*1000:.0f}ms: {r.text.strip()}", flush=True)
    except Exception as e:
        print(f" FAIL: {str(e)[:120]}", flush=True)
