
from app.memory import (
    remember_fact,
    get_all_personal_facts,
    update_personal_fact,
    find_personal_facts,
    forget_personal_fact
)


print("\n========== SAVING MEMORY ==========")

remember_fact(
    "learning",
    "Python"
)


print("\n========== ALL MEMORIES ==========")

memories = get_all_personal_facts()

for memory in memories:
    print(memory)


print("\n========== SEARCHING MEMORY ==========")

results = find_personal_facts("Python")

for memory in results:
    print(memory)


print("\n========== UPDATING MEMORY ==========")

if results:

    memory_id = results[0]["id"]

    success = update_personal_fact(
        memory_id,
        "learning",
        "Python and Artificial Intelligence"
    )

    print("Update successful:", success)


print("\n========== UPDATED MEMORIES ==========")

for memory in get_all_personal_facts():
    print(memory)


print("\n========== TEST COMPLETED ==========")
