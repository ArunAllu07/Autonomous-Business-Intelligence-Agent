import json
from pathlib import Path
from datetime import datetime


MEMORY_FILE = Path("data/long_term_memory.json")


def load_memories():
    """
    Load all long-term memories from persistent storage.

    Returns:
        list: Stored long-term memory objects.
    """
    if not MEMORY_FILE.exists():
        return []

    try:
        with open(
            MEMORY_FILE,
            "r",
            encoding="utf-8"
        ) as file:
            data = json.load(file)

        if not isinstance(data, list):
            return []

        return data

    except (json.JSONDecodeError, OSError):
        return []


def save_all_memories(memories):
    """
    Persist the complete long-term memory collection.
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
            memories,
            file,
            indent=2,
            ensure_ascii=False
        )


def save_memory(
    category,
    key,
    value
):
    """
    Save or update a structured long-term memory.

    If the same category and key already exist,
    the existing memory is updated instead of
    creating a duplicate.
    """

    memories = load_memories()

    category = str(category).strip()
    key = str(key).strip()
    value = str(value).strip()

    now = datetime.now().isoformat()

    for memory in memories:

        if (
            memory.get("category") == category
            and memory.get("key") == key
        ):
            memory["value"] = value
            memory["updated_at"] = now

            save_all_memories(memories)

            return memory

    new_memory = {
        "category": category,
        "key": key,
        "value": value,
        "created_at": now,
        "updated_at": now
    }

    memories.append(new_memory)

    save_all_memories(memories)

    return new_memory


def search_memories(query):
    """
    Retrieve the most relevant long-term memories
    using simple keyword matching.

    Returns:
        list: Up to 5 relevant memories.
    """

    memories = load_memories()

    query_words = set(
        word.lower()
        for word in str(query).split()
        if word.strip()
    )

    if not query_words:
        return []

    matches = []

    for memory in memories:

        key = str(
            memory.get("key", "")
        ).lower()

        value = str(
            memory.get("value", "")
        ).lower()

        category = str(
            memory.get("category", "")
        ).lower()

        text = f"{category} {key} {value}"

        score = sum(
            word in text
            for word in query_words
        )

        if score > 0:
            matches.append(
                (score, memory)
            )

    matches.sort(
        key=lambda item: item[0],
        reverse=True
    )

    return [
        memory
        for score, memory in matches[:5]
    ]


def delete_memory(category, key):
    """
    Delete a specific long-term memory.

    Returns:
        bool: True if a memory was deleted.
    """

    memories = load_memories()

    filtered_memories = [
        memory
        for memory in memories
        if not (
            memory.get("category") == category
            and memory.get("key") == key
        )
    ]

    if len(filtered_memories) == len(memories):
        return False

    save_all_memories(filtered_memories)

    return True


def clear_memories():
    """
    Delete all long-term memories.
    """
    save_all_memories([])


def get_memory_count():
    """
    Return the number of stored long-term memories.
    """
    return len(load_memories())