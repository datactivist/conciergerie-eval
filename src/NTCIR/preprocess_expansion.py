import json
import sys, getopt
import csv


def main(argv):
    input_file = ""
    expansion_flag = ""

    try:
        opts, args = getopt.getopt(argv, "hei:", ["help", "ifile=", "expansion"])
    except getopt.GetoptError:
        print("usage: preprocess_expansion.py -i <input_file>")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(
                "Preprocess the feedbacks return by the API database to match the NTCIR format\n\
                -h: show this panel\n\
                -i: intput file\n\
                -e: add query expansion to the query\n\
                usage: preprocess_expansion.py -i <input_file> [--expansion]"
            )
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-e", "--expansion"):
            expansion_flag = True

    try:
        with open(input_file) as json_file:
            expansion_feedbacks = json.load(json_file)
    except:
        print(
            "Input file not found, use the query expansion API to get it\n\
            usage: preprocess_expansion.py -i <input_file>"
        )
        sys.exit()

    id = 0
    with open("expansion_topics.tsv", "wt") as topics:
        with open("expansion_qrels.tsv", "wt") as qrels:
            topics_writer = csv.writer(topics, delimiter=";")
            qrels_writer = csv.writer(qrels, delimiter=";")
            topics_writer.writerow(["ID", "Query"])
            qrels_writer.writerow(["ID", "Proposed", "Feedback"])

            for search in expansion_feedbacks:
                if expansion_flag:
                    user_search = search["user_search"]
                    for feedback in search["feedbacks"]:
                        qrels_writer.writerow(
                            [id, feedback["proposed_keyword"], feedback["feedback"]]
                        )
                        if feedback["feedback"] == 1:
                            user_search += " | " + feedback["proposed_keyword"]
                    topics_writer.writerow([id, user_search])
                else:
                    topics_writer.writerow([id, search["user_search"]])
                    for feedback in search["feedbacks"]:
                        qrels_writer.writerow(
                            [id, feedback["proposed_keyword"], feedback["feedback"]]
                        )
                id += 1


if __name__ == "__main__":
    main(sys.argv[1:])
