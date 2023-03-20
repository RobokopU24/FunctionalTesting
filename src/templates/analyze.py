import jsonlines
from collections import defaultdict
from datetime import timedelta
from matplotlib import pyplot as plt

def readfile(fname):
    results = {}
    with jsonlines.open(fname,"r") as inf:
        for line in inf:
            input = line["input"]
            if input not in results:
                results[input] = {"times": [], "counts": [], "statuses": []}
            delta = timedelta(seconds = line["delta_seconds"],
                              microseconds=line["delta_microseconds"])
            results[input]["times"].append(delta)
            results[input]["counts"].append(line["Num Responses"])
            results[input]["statuses"].append(line["status_code"])
    return results

def analyze_status(results):
    ncalls = 0
    status_count = defaultdict(int)
    for result in results:
        for s in result["statuses"]:
            ncalls += 1
            status_count[s] += 1
    print(f"Number of calls: {ncalls}")
    for status,count in status_count.items():
        print(f" status:{status}, counts:{count}, percent: {count/ncalls}")

def plot_times(results):
    x = [ r["counts"][0] for r in results ]
    y = [ r["times"][0].total_seconds() for r in results ]
    plt.loglog(x,y,'o')
    plt.xlabel("Num Results")
    plt.ylabel("Time (s)")
    plt.show()

def go():
    results = readfile("../outdir/output.jsonl")
    analyze_status(results.values())
    plot_times(results.values())

if __name__ == "__main__":
    go()