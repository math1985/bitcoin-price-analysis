import calendar
import datetime
import sys
import collections

# Every samplingInterval we see if it is worth to trade.
# We look back a tradingInterval, and also keep our bitcoins for a tradingInterval before selling.
def main(tradingInterval, samplingInterval):
    if not tradingInterval % samplingInterval == 0:
        sys.exit('Trading interval must be divisible by the sampling interval');
    if not (endTimestamp - startTimestamp) % tradingInterval == 0:
        sys.exit('The difference between start and end timestamp must be divisible by the trading interval');
    table = parse()
    priceByTimestamp = generatePriceByTimestamp(table, tradingInterval, samplingInterval)
    calculateProfit(priceByTimestamp, tradingInterval, samplingInterval)

# Parse the data file
def parse():
    table = []
    with open("bitstampUSD.csv", "r") as ifile:  # Prices taken from https://api.bitcoincharts.com/v1/csv/
        for line in ifile:
            row = {}
            fields = line.split(',')
            row['timestamp'] = float(fields[0])
            row['price'] = float(fields[1])
            table.append(row)
    return table

# Generate a table (dict) that lists the price for every timestamp between
# startTimestamp and endTimestamp with interval samplingInterval
def generatePriceByTimestamp(table, tradingInterval, samplingInterval):
    priceByTimestamp = collections.OrderedDict()
    timestamp = startTimestamp - tradingInterval
    i = 0
    while timestamp <= endTimestamp:
        while table[i]['timestamp'] < timestamp:
            i += 1
        priceByTimestamp[timestamp] = table[i-1]['price']
        timestamp += samplingInterval
    return priceByTimestamp

# Calculate our profit
def calculateProfit(priceByTimestamp, tradingInterval, samplingInterval):
    totalProfit = 0
    timestamp = startTimestamp
    while timestamp <= endTimestamp - tradingInterval:
        # If the price one tradingInterval ago is smaller than the price now...
        if priceByTimestamp[timestamp - tradingInterval] < priceByTimestamp[timestamp]:
            # ... we buy a bitcoin and sell it after one tradingInterval; the difference in price is our profit
            profit = priceByTimestamp[timestamp + tradingInterval] - priceByTimestamp[timestamp]
            totalProfit += profit
        # Also, for symmetry's sake, if the price one tradingInterval ago is equal to the price now...
        if priceByTimestamp[timestamp - tradingInterval] == priceByTimestamp[timestamp]:
            # ... we buy half a bitcoin and sell it after one tradingInterval; the difference in price is our profit
            profit = .5 * (priceByTimestamp[timestamp + tradingInterval] - priceByTimestamp[timestamp])
            totalProfit += profit
        timestamp += samplingInterval
    # Correct totalProfit for the amount of investments overlapping in time
    totalProfitCorrected = totalProfit * samplingInterval / tradingInterval
    # The result we would have obtained by holding (after the first samplingInterval, i.e. when we started trading)
    profitWhenHoldingInstead = priceByTimestamp[endTimestamp] - priceByTimestamp[startTimestamp]
    differenceFromHolding = totalProfitCorrected - profitWhenHoldingInstead
    print "Final result: " + str(totalProfitCorrected)
    print "Result from holding: " + str(profitWhenHoldingInstead)
    print "Difference: " + str(differenceFromHolding)
    print

second = 1
minute = 60 * second
hour = 60 * minute
day = 24 * hour
year = 365 * day

# We calculate from 1 January 2016 until one year later
startTimestamp = calendar.timegm(datetime.datetime.strptime("2016-01-01", "%Y-%m-%d").timetuple())
endTimestamp = startTimestamp + year

print "Looking back one day:"
main(day, second)

print "Looking back one hour:"
main(hour, second)

print "Looking back ten minutes:"
main(10 * minute, second)

print "Looking back one minute:"
main(minute, second)

print "Looking back ten seconds:"
main(10 * second, second)

print "Looking back one second:"
main(second, second)
