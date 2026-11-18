
from app.ai_engine import ask_jarvis

print("Testing JARVIS AI...")

question = "Hello! Introduce yourself as JARVIS."

answer = ask_jarvis(question)

print("\nJARVIS:")
print(answer)
