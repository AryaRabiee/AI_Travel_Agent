import faiss
import json
import numpy as np


with open("llm/cities_embeddings_city_info.json" , "r" , encoding='utf-8') as f:
    data = json.load(f)

embedding = np.array([item["embedding"] for item in data] , dtype="float32")
metadata = [{"city" :item["city"] , "text":item["text"]} for item in data]

faiss.normalize_L2(embedding)
d = embedding.shape[1]
index = faiss.IndexFlatIP(d)
index.add(embedding)

faiss.write_index(index , "cities_flat_info.index")

