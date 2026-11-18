
import re

from app.database import (
    initialize_database,

    create_conversation,
    get_conversations,
    update_conversation_title,
    delete_conversation,

    save_message,
    get_messages,

    save_personal_memory,
    get_personal_memories,
    search_personal_memories,
    update_personal_memory,
    delete_personal_memory
)


# ==========================================
# INITIALIZE DATABASE
# ==========================================

initialize_database()


# ==========================================
# CONVERSATION MANAGEMENT
# ==========================================

def start_new_conversation(title="New Conversation"):

    return create_conversation(title)


def get_all_conversations():

    return get_conversations()


def update_chat_title(conversation_id, title):

    update_conversation_title(
        conversation_id,
        title
    )


def remove_conversation(conversation_id):

    delete_conversation(conversation_id)


# ==========================================
# MESSAGE MANAGEMENT
# ==========================================

def store_message(conversation_id, role, content):

    return save_message(
        conversation_id,
        role,
        content
    )


def get_conversation_history(conversation_id, limit=12):

    return get_messages(
        conversation_id,
        limit
    )


def build_conversation_context(conversation_id, limit=12):

    messages = get_conversation_history(
        conversation_id,
        limit
    )

    if not messages:
        return ""

    context = []

    for message in messages:

        role = message["role"].upper()

        content = message["content"]

        context.append(
            f"{role}: {content}"
        )

    return "\n".join(context)


# ==========================================
# PERSONAL MEMORY MANAGEMENT
# ==========================================

def remember_fact(category, fact):

    return save_personal_memory(
        category,
        fact
    )


def get_all_personal_facts():

    return get_personal_memories()


def find_personal_facts(keyword):

    return search_personal_memories(keyword)


def update_personal_fact(memory_id, category, fact):

    return update_personal_memory(
        memory_id,
        category,
        fact
    )


def forget_personal_fact(memory_id):

    delete_personal_memory(memory_id)


# ==========================================
# BUILD PERSONAL MEMORY CONTEXT
# ==========================================

def build_personal_memory_context():

    memories = get_all_personal_facts()

    if not memories:
        return ""

    context = []

    for memory in memories:

        category = memory["category"]

        fact = memory["fact"]

        context.append(
            f"- {category}: {fact}"
        )

    return "\n".join(context)


# ==========================================
# AUTOMATIC PERSONAL MEMORY DETECTION
# ==========================================

def detect_personal_memory(message):

    patterns = [

        (r"my name is\s+(.+)", "personal_information"),

        (r"i am learning\s+(.+)", "learning"),

        (r"i(?:'m| am) learning\s+(.+)", "learning"),

        (r"i prefer\s+(.+)", "preference"),

        (r"i like\s+(.+)", "interest"),

        (r"i love\s+(.+)", "interest"),

        (r"remember that\s+(.+)", "general")

    ]

    saved_facts = []

    cleaned_message = message.strip()

    for pattern, category in patterns:

        match = re.search(
            pattern,
            cleaned_message,
            re.IGNORECASE
        )

        if match:

            fact = match.group(1).strip()

            fact = fact.rstrip(" .!?")

            if fact:

                remember_fact(
                    category,
                    fact
                )

                saved_facts.append(fact)

                break

    return saved_facts
