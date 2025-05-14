import multiprocessing

def search_keyword(q_in, q_out):
    dataset = q_in.get()
    keyword = q_in.get()

    matches = [line for line in dataset if keyword.lower() in line.lower()]
    q_out.put(matches)

if __name__ == "__main__":
    dataset = [
        "Python is a great programming language.",
        "Multiprocessing can speed up tasks significantly.",
        "Shared memory allows efficient data sharing.",
        "Pipes and queues help in inter-process communication.",
        "This is a text processing example using multiprocessing.",
    ]

    q_in = multiprocessing.Queue()
    q_out = multiprocessing.Queue()

    keyword = "multiprocessing"

    p = multiprocessing.Process(target=search_keyword, args=(q_in, q_out))
    p.start()

    q_in.put(dataset)
    q_in.put(keyword)

    result = q_out.get()
    print("Matches:", result)

    p.join()