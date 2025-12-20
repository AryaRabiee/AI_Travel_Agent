import faiss
import json
import numpy as np


with open("llm/cities_embeddings_new.json" , "r" , encoding='utf-8') as f:
    data = json.load(f)

embedding = np.array([item["embedding"] for item in data] , dtype="float32")
metadata = [{"city" :item["city"] , "text":item["text"]} for item in data]

# faiss.normalize_L2(embedding)
# d = embedding.shape[1]
# index = faiss.IndexFlatIP(d)     Level0
# index.add(embedding)

# print("Number of V is " , index.ntotal)
# faiss.write_index(index , "cities.index")



# d = embedding.shape[1]
# quantizer = faiss.IndexFlatIP(d)
# index = faiss.IndexIVFFlat(
#     quantizer,
#     d,
#     3,
#     faiss.METRIC_INNER_PRODUCT        Level1
# )
# index.train(embedding)
# index.add(embedding)
# print("Number of V is " , index.ntotal)



faiss.normalize_L2(embedding)
d = embedding.shape[1]

index = faiss.IndexHNSWFlat(
    d,
    32
)
index.metric_type = faiss.METRIC_INNER_PRODUCT
index.add(embedding)
index.hnsw.efSearch = 50
print("Number of V is " , index.ntotal)
