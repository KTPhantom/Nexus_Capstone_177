"""Quick model availability test - checks which model responds right now."""
import sys, os, time
sys.stdout.reconfigure(encoding='utf-8')
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

candidates = [
    "gemini-3.1-flash-lite",
    "gemma-4-26b-a4b-it",
    "gemma-4-31b-it",
    "gemini-3.5-flash-lite",
]

for model in candidates:
    try:
        t0 = time.time()
        r = client.models.generate_content(
            model=model,
            contents='Reply with exactly: {"ok": true}',
            config={"response_mime_type": "application/json"},
        )
        print(f"  OK  {model}  ({(time.time()-t0)*1000:.0f}ms): {r.text.strip()[:60]}")
        # Use first working model
        print(f"\nBEST_MODEL={model}")
        break
    except Exception as e:
        short = str(e)[:80]
        print(f"  FAIL {model}: {short}")
