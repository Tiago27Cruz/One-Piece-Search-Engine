from django.http import JsonResponse
import requests
import pandas as pd
from sentence_transformers import SentenceTransformer

def get_unique_values(request):
    try:
        # Read the CSV file
        df = pd.read_csv('./project/data/data.csv')

        # Extract unique values for arcs and sagas
        unique_arcs = df['Arc'].dropna().unique().tolist()
        unique_sagas = df['Saga'].dropna().unique().tolist()

        # Return the unique values as a JSON response
        return JsonResponse({'arcs': unique_arcs, 'sagas': unique_sagas})
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return JsonResponse({'error': str(e)}, status=500)

def text_to_embedding(text):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode(text, convert_to_tensor=False).tolist()
    
    # Convert the embedding to the expected format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"
    return embedding_str

def build_filter_query(filters):
    fq_list = []
    for field, values in filters.items():
        
        field_filter = " OR ".join([f'{field}:"{value}"' for value in values])
        fq_list.append(f"({field_filter})")
    
    combined_fq = " AND ".join(fq_list)
    return combined_fq

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

        url = "http://localhost:8983/solr/episodes/select"
        response = requests.post(url=url, params=solr_params, headers={"Content-Type": "application/x-www-form-urlencoded"})
        return JsonResponse(response.json()['response']['docs'], safe=False)
    except requests.RequestException as e:
        print(f"Error querying Solr: {e}")
        return JsonResponse({"error": "Error querying Solr"}, status=500)


def search(request):
    query = request.GET.get("query", '')
    arcs = request.GET.get("arcs", '')
    sagas = request.GET.get("sagas", '')
    filter_query = build_filter_query({"Arc": arcs.split(','), "Saga": sagas.split(',')})
    print("Filter query:", filter_query)
    print(f"GET request for search: {query}, arcs: {arcs}, sagas: {sagas}")
    embedding = text_to_embedding(query)
    try:
        solr_data = {
            "q": f"{{!knn f=vector topK=10}}{embedding}",
            "fl": "score, *",
            "wt": "json",
            "fq": filter_query
        }
        solr_params = {
            "q": query,
            "useParams": "params",
            "wt": "json"
        }

        url = "http://localhost:8983/solr/episodes/select"
        response_embeddings = requests.post(url=url, data=solr_data, headers={"Content-Type": "application/x-www-form-urlencoded"})
        response_params = requests.post(url=url, params=solr_params, headers={"Content-Type": "application/x-www-form-urlencoded"})
    except requests.RequestException as e:
        print(f"Error querying Solr: {e}")


    # Process the query and generate results
    return JsonResponse(response_embeddings.json()['response']['docs'], safe=False)