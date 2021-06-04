import requests
import csv
import json
import numpy as np


def result_is_present(target_title, results):

    for result in results:
        if result["title"] in target_title:
            return True
    return False


"""
        "target": [
            "\"Concessions hydro\u00e9lectriques - Domaines conc\u00e9d\u00e9s - en Provence Alpes C\u00f4te d'Azur\"",
            "https://trouver.datasud.fr/dataset/synce44da5b-fr-120066022-jdd-58fa0f8a-fa62-4e33-a840-c4b701a19929"
        ],
        "query_baseline": "barrages",
        "results_baseline": [
        "expanded_keywords_word2vec": "hydro\u00e9lectrique digues hydro\u00e9lectriques crue barrage",
        "results_word2vec": [
"""
with open("results.json") as json_file:
    data = json.load(json_file)

print(len(data))

score_baseline = 0
score_word2vec = 0
score_fasttext = 0

unique_baseline = 0
unique_word2vec = 0
unique_fasttext = 0

none = 0

matrix = np.zeros((3, 3))

globale = 0

for result in data:

    flag_baseline = False
    flag_word2vec = False
    flag_fasttext = False

    if result_is_present(result["target"][0], result["results_baseline"][0:200]):
        score_baseline += 1
        flag_baseline = True
        matrix[0][0] += 1

    if result_is_present(result["target"][0], result["results_word2vec"][0:200]):
        score_word2vec += 1
        flag_word2vec = True
        if flag_baseline:
            matrix[0][1] += 1
            matrix[1][0] += 1
        matrix[1][1] += 1

    if result_is_present(result["target"][0], result["results_fasttext"][0:200]):
        score_fasttext += 1
        flag_fasttext = True
        if flag_baseline:
            matrix[0][2] += 1
            matrix[2][0] += 1
            if flag_word2vec:
                globale += 1
        elif flag_word2vec:
            matrix[1][2] += 1
            matrix[2][1] += 1
        else:
            unique_fasttext += 1
        matrix[2][2] += 1
    else:
        if flag_word2vec and not flag_baseline:
            unique_word2vec += 1
        elif not flag_word2vec and flag_baseline:
            unique_baseline += 1
        else:
            none += 1


print("baseline", score_baseline)
print("word2vec", score_word2vec)
print("fasttext", score_fasttext)
print()
print("baseline", unique_baseline)
print("word2vec", unique_word2vec)
print("fasttext", unique_fasttext)
print()
print("matrix\n", matrix)
print()
print("full", globale)
print("none", none)

