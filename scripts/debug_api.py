"""Debug script to test Gemma 4 API connectivity and run one real benchmark scenario."""
import sys, os, json, time, glob
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

api_key = os.environ.get("GEMINI_API_KEY", "")
print(f"API key present: {bool(api_key)} ({api_key[:8]}...)")

from google import genai
client = genai.Client(api_key=api_key)

# ── Step 1: Basic connectivity ──────────────────────────────────────────────
print("\n=== Step 1: API connectivity ===")
try:
    t0 = time.time()
    r = client.models.generate_content(
        model='gemma-4-31b-it',
        contents='What is 2+2? Reply with only a number.',
    )
    print(f"  Response ({(time.time()-t0)*1000:.0f}ms): {r.text.strip()[:100]}")
except Exception as e:
    print(f"  FAILED: {e}")
    sys.exit(1)

# ── Step 2: JSON mode ───────────────────────────────────────────────────────
print("\n=== Step 2: JSON response mode ===")
try:
    t0 = time.time()
    r = client.models.generate_content(
        model='gemma-4-31b-it',
        contents='Pick one tool. Return JSON: {"tools": ["PomodoroTimer"]}',
        config={'response_mime_type': 'application/json'}
    )
    print(f"  Response ({(time.time()-t0)*1000:.0f}ms): {r.text.strip()[:200]}")
except Exception as e:
    print(f"  FAILED: {e}")

# ── Step 3: Naive System 1 (truncated prompt) ───────────────────────────────
print("\n=== Step 3: Naive System 1 on STU-01 ===")
raw_files = glob.glob("registry/**/*.tsx", recursive=True)
all_raw_code = "\n\n".join(open(f, "r", encoding="utf-8").read() for f in raw_files)
prompt1 = (
    "You are a workspace configurator. Here are all available React components "
    f"(full source code):\n\n{all_raw_code}\n\n"
    "User query: I need a study timer and grade tracker\n\n"
    'Which components should be included? Return ONLY valid JSON: {"tools": ["ComponentName1"]}'
)
print(f"  Prompt length: {len(prompt1)} chars / ~{len(prompt1.split())} words")
try:
    t0 = time.time()
    r = client.models.generate_content(
        model='gemma-4-31b-it',
        contents=prompt1,
        config={'response_mime_type': 'application/json'}
    )
    print(f"  Response ({(time.time()-t0)*1000:.0f}ms): {r.text.strip()[:300]}")
    parsed = json.loads(r.text)
    print(f"  Parsed tools: {parsed.get('tools', [])}")
except Exception as e:
    print(f"  FAILED: {e}")

print("\n=== All steps done ===")
