import csv
import json

class Country():
    def __init__(self, name, lat, lon):
        self.name = name
        self.lat = lat
        self.lon = lon

    def __str__(self):
        return "%s (%s, %s)" % (self.name, self.lat, self.lon)

def read_json(path):
    countries = []

    with open(path) as data_file:    
        data = json.load(data_file)

        for c in data:
            country = Country(c['name'], c['location']['lat'], c['location']['lng'])
            countries.append(country)

    return countries

def read_csv(path):
    countries = []

    with open(path, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            country = Country(row[0], float(row[1]), float(row[2]))
            countries.append(country)

    return countries

