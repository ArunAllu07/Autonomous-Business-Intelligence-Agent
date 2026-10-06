import json
from pathlib import Path
from datetime import datetime


MEMORY_FILE = Path("data/memory.json")


def load_memory():
    """
    Load all stored memories from the JSON file.

    Returns:
        list: Stored memory objects.
    """
    if not MEMORY_FILE.exists():
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        return data

    except (json.JSONDecodeError, OSError):
        return []


def save_memory(memory):
    """
    Save the complete memory list to disk.

    Args:
        memory (list): Memory objects to persist.
    """
    MEMORY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(
        MEMORY_FILE,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            memory,
            file,
            indent=2,
            ensure_ascii=False
        )


def add_memory(role, content, memory_type="conversation"):
    """
    Add a new memory to persistent storage.

    Args:
        role (str): Source of the memory, e.g. user or assistant.
        content (str): Memory content.
        memory_type (str): Type of memory being stored.

    Returns:
        dict: The newly created memory.
    """
    memory = load_memory()

    new_memory = {
        "role": role,
        "content": content,
        "type": memory_type,
        "timestamp": datetime.now().isoformat()
    }

    memory.append(new_memory)

    save_memory(memory)

    return new_memory


def clear_memory():
    """
    Delete all stored memories.
    """
    save_memory([])


def get_memory_count():
    """
    Return the number of stored memories.

    Returns:
        int: Number of memories.
    """
    return len(load_memory())