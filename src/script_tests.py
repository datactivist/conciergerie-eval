import requests
import csv
import json


datasud_API = "https://trouver.datasud.fr/api/3/action/package_search?"
query_expansion_API = "http://127.0.0.1:8001/"


def get_5_most_expand(expand_keywords):

    exp_terms = set([])

    index = 0
    while len(exp_terms) < 5:

        for og_key in expand_keywords:

            if og_key["referentiel"]["tags"] is not None:
                if index < len(og_key["referentiel"]["tags"]):
                    if len(exp_terms) < 5:
                        exp_terms.add(og_key["referentiel"]["tags"][index])

            for sense in og_key["tree"]:
                if index < len(sense["similar_senses"]):
                    if len(exp_terms) < 5:
                        exp_terms.add(sense["similar_senses"][index][0]["sense"])
        index += 1

    return " ".join(exp_terms)


def query_expansion_word2vec(request):

    search_expand_url = query_expansion_API + "query_expand"
    body = {"keywords": request, "max_width": 3, "referentiel": {"name": "datasud"}}
    expand_keywords = get_5_most_expand(
        requests.post(search_expand_url, json=body).json()
    )
    return expand_keywords


def query_expansion_fasttext(request):

    search_expand_url = query_expansion_API + "query_expand"
    body = {
        "keywords": request,
        "max_width": 3,
        "referentiel": {"name": "datasud"},
        "embeddings_type": "fasttext",
        "embeddings_name": "cc.fr.300.magnitude",
    }
    expand_keywords = get_5_most_expand(
        requests.post(search_expand_url, json=body).json()
    )
    return expand_keywords


def query_expansion_wordnet(request):

    search_expand_url = query_expansion_API + "query_expand"
    body = {
        "keywords": request,
        "max_width": 3,
        "referentiel": {"name": "datasud"},
        "embeddings_type": "wordnet",
    }
    expand_keywords = get_5_most_expand(
        requests.post(search_expand_url, json=body).json()
    )
    print(expand_keywords)
    return expand_keywords


def request_Datasud(request, expand_keywords):

    query_params = {
        "q": "||".join(request.split(" ") + expand_keywords.split(" ")),
        "rows": 300,
    }
    print("Je recherche: ", query_params)
    results = requests.post(datasud_API, params=query_params).json()
    print(len(results))
    with open("data.json", "w") as outfile:
        json.dump(results, outfile)
    return results["result"]["results"]


def result_is_present(target_title, results):

    for result in results:
        if result["title"] in target_title:
            return True
    return False


def clear_results_metadata(results):

    cleared_results = []

    for result in results:
        cleared_results.append({"id": result["id"], "title": result["title"]})

    return cleared_results


with open("../data/processed/datasud_sl.csv", newline="") as csvfile:

    spamreader = csv.reader(csvfile, delimiter=",", quotechar="|")

    index = 0

    with open("../results.json") as json_file:
        save_experiment = json.load(json_file)

    for row in spamreader:
        if index > 45:

            print(row)
            results_baseline = request_Datasud(row[2], "")

            expand_keywords_word2vec = query_expansion_word2vec(row[2])
            try:
                results_query_expansion_word2vec = request_Datasud(
                    row[2], expand_keywords_word2vec
                )
            except:
                results_query_expansion_word2vec = []

            expand_keywords_fasttext = (
                query_expansion_fasttext(row[2]).replace(".", "").replace("à", "a")
            )
            try:
                results_query_expansion_fasttext = request_Datasud(
                    row[2], expand_keywords_fasttext
                )
            except:
                results_query_expansion_fasttext = []
            """
            expand_keywords_wordnet = query_expansion_wordnet(row[2])
            results_query_expansion_wordnet = request_Datasud(
                row[2], expand_keywords_wordnet
            )
            """

            index += 1

            save_experiment.append(
                {
                    "target": (row[0], row[1]),
                    "query_baseline": row[2],
                    "results_baseline": clear_results_metadata(results_baseline),
                    "expanded_keywords_word2vec": expand_keywords_word2vec,
                    "results_word2vec": clear_results_metadata(
                        results_query_expansion_word2vec
                    ),
                    "expanded_keywords_fasttext": expand_keywords_fasttext,
                    "results_fasttext": clear_results_metadata(
                        results_query_expansion_fasttext
                    ),
                }
            )
            print()

            with open("../results.json", "w") as outfile:
                json.dump(save_experiment, outfile)

        else:
            index += 1

    with open("../results.json", "w") as outfile:
        json.dump(save_experiment, outfile)

