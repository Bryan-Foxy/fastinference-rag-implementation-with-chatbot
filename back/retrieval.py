import faiss
import numpy as np 
from sentence_transformers import SentenceTransformer

class DB:
    def __init__(self, documents, model_name="all-MiniLM-L6-v2"):
        self.documents = documents  
        self.model = SentenceTransformer(model_name)
        
    def embed_documents(self):
        """ Encodes documents with the specified pattern and builds a Faiss index from the embeddings """
        embeddings = self.model.encode(
            [doc.page_content for doc in self.documents],
            show_progress_bar=True
        )
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embeddings, dtype=np.float32))
        print("[INFO] Faiss index created with dimension:", dimension)
        return index