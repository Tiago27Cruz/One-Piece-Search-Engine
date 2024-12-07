from django.http import JsonResponse
import requests
from sentence_transformers import SentenceTransformer

def text_to_embedding(text):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode(text, convert_to_tensor=False).tolist()
    
    # Convert the embedding to the expected format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"
    return embedding_str

def episode(request, episode_id):
    print(f"GET request for Episode {episode_id}")
    try:
        solr_params = {
            "q.op": "AND",
            "defType": "edismax",
            "q": "*:*",
            "fq": f"Episode: {episode_id}",
            "wt": "json"
        }

        uri = "http://localhost:8983/solr/episodes/select"
        response = requests.post(uri, params=solr_params, headers={"Content-Type": "application/x-www-form-urlencoded"})
        return JsonResponse(response.json()['response']['docs'], safe=False)
    except requests.RequestException as e:
        print(f"Error querying Solr: {e}")
        return JsonResponse({"error": "Error querying Solr"}, status=500)


def search(request):
    query = request.GET.get("query", '')
    print(f"GET request for search: {query}")
    embedding = text_to_embedding(query)
    try:
        solr_data = {
            "q": f"{{!knn f=vector topK=10}}{embedding}",
            "fl": "score, *",
            "wt": "json"
        }
        solr_params = {
            "q": query,
            "useParams": "params",
            "wt": "json"
        }

        uri = "http://localhost:8983/solr/episodes/select"
        response_embeddings = requests.post(uri, data=solr_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        response_params = requests.post(uri, params=solr_params, headers={"Content-Type": "application/x-www-form-urlencoded"})
    except requests.RequestException as e:
        print(f"Error querying Solr: {e}")


    # Process the query and generate results
    return JsonResponse(response_embeddings.json()['response']['docs'], safe=False)