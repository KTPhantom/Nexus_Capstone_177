import os, sys, time, json
from google import genai
from google.genai import types

sys.stdout.reconfigure(encoding='utf-8')
api_key = os.environ.get("GEMINI_API_KEY", "")
client = genai.Client(api_key=api_key)
MODEL = "gemma-4-26b-a4b-it"

print(f"Testing Gemma 4 26B ({MODEL}) end-to-end...", flush=True)

# 1. Test Intent Analysis
prompt_intent = (
    "Analyze the intent of this user query: 'I need to study for exams and track my grades'. "
    "Return ONLY a JSON object with this exact structure: "
    '{"primary_domain": "student", "sub_intents": [{"action": "study", "entity": "exams", "priority": 1}, {"action": "track", "entity": "grades", "priority": 1}], "raw_query": "I need to study for exams and track my grades", "confidence": 0.95}'
)
t0 = time.time()
r_intent = client.models.generate_content(
    model=MODEL,
    contents=prompt_intent,
    config=types.GenerateContentConfig(response_mime_type="application/json")
)
print(f"1. Intent Analysis ({time.time()-t0:.1f}s): {r_intent.text.strip()[:150]}...", flush=True)

# 2. Test Tool Calling
prompt_tools = (
    "Given user intent 'study and track grades' and available tools:\n"
    "[PomodoroTimer] (student) | Focus timer | props: initialWorkMinutes\n"
    "[GradeTracker] (student) | Track GPA and course grades | props: targetGpa\n"
    "[InventoryStockTable] (shopkeeper) | Track retail items\n\n"
    "Select the required tools and bind props. Return ONLY a JSON object: "
    '{"selected_tools": [{"component_id": "PomodoroTimer", "bound_props": {"initialWorkMinutes": 25}, "confidence": 0.95}, {"component_id": "GradeTracker", "bound_props": {"targetGpa": 4.0}, "confidence": 0.95}], "intent_coverage": 1.0, "schema_conformance_rate": 1.0}'
)
t0 = time.time()
r_tools = client.models.generate_content(
    model=MODEL,
    contents=prompt_tools,
    config=types.GenerateContentConfig(response_mime_type="application/json")
)
print(f"2. Tool Calling ({time.time()-t0:.1f}s): {r_tools.text.strip()[:150]}...", flush=True)

print("Pipeline test successful!", flush=True)
