import requests
import json

url = "https://api.jina.ai/v1/embeddings"
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer jina_7fedde13af3440c88d1cad18c001c003y14JgGjTbn-LcR3M2h2rOcLT82sI"
}
data = {
    "model": "jina-embeddings-v3",
    "task": "text-matching",
    "input": ["هوش مصنوعی میتواند دنیا را دگرگون کند",
            "میخوام به شهر بزرگ سفر کنم"
            "میخوام به یه شهر تاریخی سفر کنم",
            ]
}

response = requests.post(url, headers=headers, data=json.dumps(data))

print(response.json())






# input=["هوش مصنوعی میتواند دنیا را دگرگون کند",
#            "میخوام به شهر بزرگ سفر کنم",
#            "میخوام به یه شهر تاریخی سفر کنم"
#            ],