
import sqlite3
from pathlib import Path


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

PROJECT_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_DIR / "data"

DATABASE_PATH = DATA_DIR / "jarvis_memory.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    connection.execute("PRAGMA foreign_keys = ON")

    return connection


# ==========================================
# INITIALIZE DATABASE
# ==========================================

def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    # Conversations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS conversations (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            title TEXT NOT NULL,

            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP

        )
    """)

    # Messages table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            conversation_id INTEGER NOT NULL,

            role TEXT NOT NULL,

            content TEXT NOT NULL,

            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY (conversation_id)
                REFERENCES conversations(id)
                ON DELETE CASCADE

        )
    """)

    # Personal memory table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS personal_memory (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            category TEXT NOT NULL,

            fact TEXT NOT NULL,

            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,

            UNIQUE(category, fact)

        )
    """)

    connection.commit()

    connection.close()


# ==========================================
# CONVERSATION FUNCTIONS
# ==========================================

def create_conversation(title="New Conversation"):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO conversations (title) VALUES (?)",
        (title,)
    )

    conversation_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return conversation_id


def get_conversations():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM conversations
        ORDER BY updated_at DESC, id DESC
    """)

    conversations = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return conversations


def update_conversation_title(conversation_id, title):

    connection = get_connection()

    connection.execute("""
        UPDATE conversations
        SET title = ?,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (title, conversation_id))

    connection.commit()

    connection.close()


def delete_conversation(conversation_id):

    connection = get_connection()

    connection.execute(
        "DELETE FROM conversations WHERE id = ?",
        (conversation_id,)
    )

    connection.commit()

    connection.close()


# ==========================================
# MESSAGE FUNCTIONS
# ==========================================

def save_message(conversation_id, role, content):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO messages (
            conversation_id,
            role,
            content
        )
        VALUES (?, ?, ?)
    """, (conversation_id, role, content))

    message_id = cursor.lastrowid

    connection.execute("""
        UPDATE conversations
        SET updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    """, (conversation_id,))

    connection.commit()

    connection.close()

    return message_id


def get_messages(conversation_id, limit=None):

    connection = get_connection()

    cursor = connection.cursor()

    if limit is not None:

        cursor.execute("""
            SELECT *
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id DESC
            LIMIT ?
        """, (conversation_id, limit))

        rows = list(reversed(cursor.fetchall()))

    else:

        cursor.execute("""
            SELECT *
            FROM messages
            WHERE conversation_id = ?
            ORDER BY id ASC
        """, (conversation_id,))

        rows = cursor.fetchall()

    messages = [
        dict(row)
        for row in rows
    ]

    connection.close()

    return messages


# ==========================================
# PERSONAL MEMORY FUNCTIONS
# ==========================================

def save_personal_memory(category, fact):

    category = category.strip().lower()

    fact = fact.strip()

    if not category or not fact:
        return None

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO personal_memory (
            category,
            fact
        )
        VALUES (?, ?)
    """, (category, fact))

    memory_id = cursor.lastrowid

    connection.commit()

    connection.close()

    return memory_id


def get_personal_memories():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM personal_memory
        ORDER BY id DESC
    """)

    memories = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return memories


def search_personal_memories(keyword):

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM personal_memory
        WHERE fact LIKE ?
        OR category LIKE ?
        ORDER BY id DESC
    """, (
        f"%{keyword}%",
        f"%{keyword}%"
    ))

    memories = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return memories


def update_personal_memory(memory_id, category, fact):

    category = category.strip().lower()

    fact = fact.strip()

    if not category or not fact:
        return False

    connection = get_connection()

    try:

        cursor = connection.cursor()

        cursor.execute("""
            UPDATE personal_memory
            SET category = ?,
                fact = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            category,
            fact,
            memory_id
        ))

        connection.commit()

        return cursor.rowcount > 0

    except sqlite3.IntegrityError:

        return False

    finally:

        connection.close()


def delete_personal_memory(memory_id):

    connection = get_connection()

    connection.execute(
        "DELETE FROM personal_memory WHERE id = ?",
        (memory_id,)
    )

    connection.commit()

    connection.close()


# ==========================================
# INITIALIZE DATABASE AUTOMATICALLY
# ==========================================

initialize_database()
