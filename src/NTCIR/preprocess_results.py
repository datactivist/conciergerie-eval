import json
import sys, getopt
import csv


def main(argv):
    input_file = ""

    try:
        opts, args = getopt.getopt(argv, "hi:", ["help", "ifile="])
    except getopt.GetoptError:
        print("usage: results_feedbacks_to_ntcir.py -i <input_file>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(
                "Preprocess the feedbacks return by the API database to match the NTCIR format\n\
                -h: show this panel\n\
                -i: intput file\n\
                usage: results_feedbacks_to_ntcir.py -i <input_file>"
            )
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg

    try:
        with open(input_file) as json_file:
            expansion_feedbacks = json.load(json_file)
    except:
        print(
            "Input file not found, use the search reranking API to get it\n\
            usage: results_feedbacks_to_ntcir.py -i <input_file>"
        )
        sys.exit()

    id = 0
    with open("results_topics.tsv", "wt") as topics:
        with open("results_qrels.tsv", "wt") as qrels:
            topics_writer = csv.writer(topics, delimiter=";")
            qrels_writer = csv.writer(qrels, delimiter=";")
            topics_writer.writerow(["ID", "Query"])
            qrels_writer.writerow(["ID", "Result", "Feedback"])

            for search in expansion_feedbacks:
                topics_writer.writerow([id, search["user_search"]])
                for feedback in search["feedbacks"]:
                    qrels_writer.writerow(
                        [id, feedback["result"]["url"], feedback["feedback"]]
                    )
                id += 1


if __name__ == "__main__":
    main(sys.argv[1:])
