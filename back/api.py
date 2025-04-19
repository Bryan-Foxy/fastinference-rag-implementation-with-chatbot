from retrieval import DB
from generation import RAG
from ingestion import Ingestion
from flask import Flask, request, jsonify

app = Flask(__name__)
rag_instance = None

@app.route("/ingest", methods=["POST"])
def ingest_file():
    global rag_instance

    data = request.get_json()
    path = data.get("path")

    if not path:
        return jsonify({"error": "Missing document path."}), 400

    ingest = Ingestion(input_data=path)
    documents = ingest.load_data()
    db = DB(documents)
    rag_instance = RAG(db, k=2)

    return jsonify({"message": f"Document loaded from {path}", "num_docs": len(documents)})

@app.route("/ask", methods=["POST"])
def ask_question():
    global rag_instance

    if rag_instance is None:
        return jsonify({"error": "No document has been ingested yet."}), 400

    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "Missing query."}), 400

    answer, top_docs, distances = rag_instance.generate_answer(query)
    if hasattr(answer, "choices"):
        answer = answer.choices[0].message["content"]

    return jsonify({
        "query": query,
        "answer": str(answer),
        "top_docs": top_docs,
        "distances": str(distances)
    })

if __name__ == "__main__":
    app.run(debug=True)