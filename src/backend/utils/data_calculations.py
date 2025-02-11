import statistics

class calculations:
    def __init__(self, std_dev, avg, median, length):
        self.std_dev = std_dev
        self.avg = avg
        self.median = median
        self.length = length

## Calculation functions:

def calc_standard_deviation(data):
    return statistics.stdev(data)

def calc_avg(data):
    return statistics.mean(data)

def calc_median(data):
    return statistics.median(data)

def calc_length(data):
    return len(data)


def calc_pipeline(data):
    std_dev = calc_standard_deviation(data)
    avg = calc_avg(data)
    median = calc_median(data)
    length = calc_length(data)
    return calculations(std_dev, avg, median, length)

