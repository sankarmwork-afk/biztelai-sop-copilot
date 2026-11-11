from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction


BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION_NAME = "manufacturing_sops"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def get_collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    embedding_function = SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )

    return client.get_collection(
        name=COLLECTION_NAME,
        embedding_function=embedding_function,
    )


def search_documents(question, top_k=8):
    collection = get_collection()

    results = collection.query(
        query_texts=[question],
        n_results=min(top_k, collection.count()),
        include=["documents", "metadatas", "distances"],
    )

    matches = []

    for index, document in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][index]

        matches.append({
            "text": document,
            "source": metadata.get("source", "Unknown"),
            "document_number": metadata.get("document_number", "Unknown"),
            "page": metadata.get("page", "Unknown"),
            "revision": metadata.get("revision", "Unknown"),
            "distance": results["distances"][0][index],
        })

    return matches


if __name__ == "__main__":
    print("Manufacturing SOP Semantic Search")
    print("Type a question, or type 'exit' to stop.\n")

    while True:
        question = input("Your question: ").strip()

        if question.lower() in {"exit", "quit"}:
            print("Search stopped.")
            break

        if len(question) < 3:
            print("Please enter a question with at least 3 characters.\n")
            continue

        results = search_documents(question)

        if not results:
            print("No matching passages were found.\n")
            continue

        for result in results:
            print("\n--------------------")
            print("Source:", result["source"])
            print("Document:", result["document_number"])
            print("Page:", result["page"])
            print("Revision:", result["revision"])
            print("Distance:", round(result["distance"], 4))
            print("Content:")
            print(result["text"])

        print()