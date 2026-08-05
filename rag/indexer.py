import os
import chromadb
from sentence_transformers import SentenceTransformer

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

client = chromadb.PersistentClient(path="./chroma_db")

try:
    client.delete_collection("coding_agent")
except:
    pass

collection = client.get_or_create_collection("coding_agent")


def build_index(project_path="."):

    print("📚 Building Project Index...")

    count = 0

    for root, dirs, files in os.walk(project_path):

        dirs[:] = [
            d for d in dirs
            if d not in [".venv", "__pycache__", ".git", "chroma_db"]
        ]

        for file in files:

            if file.endswith(".py"):

                path = os.path.join(root, file)

                try:
                    with open(path, "r", encoding="utf-8") as f:
                        code = f.read()

                    embedding = model.encode(code).tolist()

                    collection.add(
                        ids=[path],
                        documents=[code],
                        embeddings=[embedding],
                        metadatas=[{"file": path}],
                    )

                    count += 1

                except Exception as e:
                    print(f"Skipped {path}: {e}")

    print(f"\n✅ Indexed {count} Python files.")