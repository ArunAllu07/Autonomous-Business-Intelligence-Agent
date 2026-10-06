import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "data/chroma"
COLLECTION_NAME = "aura_cv"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)

collection = client.get_collection(
    name=COLLECTION_NAME
)

embedding_model = SentenceTransformer(
    EMBEDDING_MODEL
)


def retrieve(
    query: str,
    top_k: int = 5
):

    query_embedding = embedding_model.encode(
        [query]
    ).tolist()

    results = collection.query(
        query_embeddings=query_embedding,
        n_results=top_k,
        include=[
            "documents",
            "metadatas",
            "distances"
        ]
    )

    documents = results.get(
        "documents",
        [[]]
    )[0]

    metadatas = results.get(
        "metadatas",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    return documents, metadatas, distances


def main():

    print("\n================================")
    print("AURA RAG RETRIEVER")
    print("================================")

    question = input(
        "\nAsk something about the CV: "
    )

    documents, metadatas, distances = retrieve(
        question,
        top_k=5
    )

    print(
        "\n========== RETRIEVED CHUNKS ==========\n"
    )

    for i, (document, metadata, distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1
    ):

        print(f"--- RESULT {i} ---")

        print(
            f"Distance: {distance:.4f}"
        )

        print(
            f"Metadata: {metadata}"
        )

        print("\nContent:")

        print(document)

        print("\n" + "-" * 60)

    print(
        "\n========== END ==========\n"
    )


if __name__ == "__main__":
    main()