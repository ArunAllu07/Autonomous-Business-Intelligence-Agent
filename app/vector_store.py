import chromadb

from app.ingest import load_pdf, chunk_text


# -----------------------------
# Configuration
# -----------------------------

PDF_PATH = "data/ARUN_META_CV.pdf"

CHROMA_PATH = "data/chroma"

COLLECTION_NAME = "aura_cv"

EMBEDDING_MODEL = "all-MiniLM-L6-v2"


# -----------------------------
# Create Vector Store
# -----------------------------

def create_vector_store():
    from sentence_transformers import SentenceTransformer


    print("\n================================")
    print("AURA RAG VECTOR STORE")
    print("================================")

    # --------------------------------
    # 1. Load PDF
    # --------------------------------

    print("\n[1/5] Loading PDF...")

    text = load_pdf(PDF_PATH)

    print(f"Characters extracted: {len(text)}")

    # --------------------------------
    # 2. Create chunks
    # --------------------------------

    print("\n[2/5] Creating chunks...")

    chunks = chunk_text(
    text,
    max_chunk_size=1200
)

    print(f"Chunks created: {len(chunks)}")

    # --------------------------------
    # 3. Load embedding model
    # --------------------------------

    print("\n[3/5] Loading embedding model...")

    embedding_model = SentenceTransformer(
        EMBEDDING_MODEL
    )

    print(
        f"Embedding model loaded: {EMBEDDING_MODEL}"
    )

    # --------------------------------
    # 4. Create embeddings
    # --------------------------------

    print("\n[4/5] Creating embeddings...")

    embeddings = embedding_model.encode(
        chunks,
        show_progress_bar=True
    ).tolist()

    print(
        f"Embeddings created: {len(embeddings)}"
    )

    # --------------------------------
    # 5. Store in ChromaDB
    # --------------------------------

    print("\n[5/5] Storing data in ChromaDB...")

    client = chromadb.PersistentClient(
        path=CHROMA_PATH
    )

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME
    )

    # Remove old data if it exists.
    # This prevents duplicate chunks when
    # rebuilding the vector database.

    existing = collection.get()

    if existing["ids"]:

        collection.delete(
            ids=existing["ids"]
        )

        print("Old vector data cleared.")

    # Create unique IDs
    ids = [
        f"cv_chunk_{i}"
        for i in range(len(chunks))
    ]

    # Metadata for each chunk
    metadatas = [
        {
            "source": "ARUN_META_CV.pdf",
            "chunk_id": i
        }
        for i in range(len(chunks))
    ]

    # Store documents + embeddings + metadata
    collection.add(
        ids=ids,
        documents=chunks,
        embeddings=embeddings,
        metadatas=metadatas
    )

    # --------------------------------
    # Finished
    # --------------------------------

    print("\n================================")
    print("VECTOR STORE CREATED SUCCESSFULLY")
    print("================================")

    print(f"Collection      : {COLLECTION_NAME}")
    print(f"Chunks stored   : {len(chunks)}")
    print(f"Embedding model : {EMBEDDING_MODEL}")
    print(f"Database path   : {CHROMA_PATH}")

    print("\nAURA RAG knowledge base is ready.")


# -----------------------------
# Run
# -----------------------------

if __name__ == "__main__":
    create_vector_store()
