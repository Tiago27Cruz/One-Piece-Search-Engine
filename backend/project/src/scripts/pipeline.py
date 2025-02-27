import argparse
import sys
import subprocess
import json
from sentence_transformers import SentenceTransformer

def text_to_embedding(text):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    embedding = model.encode(text, convert_to_tensor=False).tolist()
    
    # Convert the embedding to the expected format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"
    return embedding_str


def feedForward(query_file, topk, score, reRankDocs, reRankWeight):
    # Load the query parameters from the JSON file
    try:
        query_json = json.load(open(query_file))
    except FileNotFoundError:
        print(f"Error: Query file {query_file} not found.")
        sys.exit(1)

    for query_name, params in query_json.items():
        params['q'] = params['q'].replace('"', '\\"')
        mode = "rqq"
        if query_name.startswith("m2") or query_name.startswith("def"):
            mode = "par"
        elif query_name.startswith("emb"):
            mode = "emb"
            params['useParams'] = "smth"

        command = (
            f"python query_solr.py --query \"{params['q']}\" --collection {params['collection']} --useParams {params['useParams']} --uri http://localhost:8983/solr --mode {mode} --topk {topk} --score {score} --reRankDocs {reRankDocs} --reRankWeight {reRankWeight} |"
            f"python solr2trec.py > ./results/{query_name}.txt"
        )
        subprocess.run(command, shell=True, check=True)
        
        qrel_str = "-".join(str(qrel_item) for qrel_item in params['qrel'])


        command = (
            f"python qrels2trec.py --qrels {qrel_str} > ./qrels/{query_name}.txt"
        )

        subprocess.run(command, shell=True, check=True)


        
def plot_pr_curve():
    queries = [
        "sh_childhood",
        "luffy_fight",
        "bounty",
        "ancient_weapon"
    ]

    for query in queries:
        command = (
            f"python plot_pr.py --qrels ./qrels/{query}.txt --def_qrels ./qrels/def_{query}.txt --m2_qrels ./qrels/m2_{query}.txt --emb_qrels ./qrels/emb_{query}.txt --output ./diagrams/{query}.png"
        )
        subprocess.run(command, shell=True, check=True)



if __name__ == "__main__":
    # Argument parser to handle the query file as command-line arguments
    parser = argparse.ArgumentParser(
        description="Generate a Precision-Recall curve from Solr results (in TREC format) and qrels."
    )
    parser.add_argument(
        "--query",
        type=str,
        required=True,
        help="Path to the query json file",
    )
    parser.add_argument(
        "--topk",
        type=str,
        required=True,
        default="None",
        help="topk",
    )
    parser.add_argument(
        "--score",
        type=str,
        required=True,
        default="None",
        help="score",
    )
    parser.add_argument(
        "--reRankDocs",
        type=str,
        required=True,
        default="None",
        help="reRankDocs",
    )
    parser.add_argument(
        "--reRankWeight",
        type=str,
        required=True,
        default="None",
        help="reRankWeight",
    )
    parser.add_argument(
        "--gridSearch",
        type=str,
        required=True,
        help="Path to the query json file",
    )
    
    args = parser.parse_args()


    feedForward(args.query, args.topk, args.score, args.reRankDocs, args.reRankWeight)
    if(args.gridSearch == "False"):
        plot_pr_curve()

