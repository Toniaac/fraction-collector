from fraction_collector_v2 import FractionCollector

#Initialize the FractionCollector with default parameters
collector = FractionCollector()

#Collect a fraction
for i in range (0, 48):
    collector.collect_fraction(location='well_plate_location', location_index=i)