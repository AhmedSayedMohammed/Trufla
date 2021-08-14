import csv
import getopt
import json
import pathlib
import sys
import time
import xmltodict
from os import path
import requests
from db_connection import get_trufla_db

trufla_db = get_trufla_db()


# implemented strategy design pattern
class FileParser:
    data_dict = None

    def __init__(self, input_path, parse_method=None):
        self.input_path = input_path
        self.data_dict = parse_method(input_path)

    def save_dict_as_json_file(self, json_destination_path):
        json_data = json.dumps(self.data_dict)
        with open(json_destination_path, "w") as json_file:
            json_file.write(json_data)
            json_file.close()
            print("file saved")

    def save_dict_to_mongodb(self, collection_name):
        trufla_db.get_collection(collection_name).insert_one(self.data_dict)
        print('file saved to mongodb')

    def decode_vin_vehicle(self, json_destination_path):
        try:
            vehicles = self.data_dict['Insurance']['Transaction']['Customer']['Units']['Auto']['Vehicle']
        except Exception as e:
            print('key error')
            return False
        new_vehicles = []
        # check if vehicles is one object or array of objects
        if isinstance(vehicles, dict):
            new_vehicles = combine_vehicles_keys(vehicles)
        else:
            for vehicle in vehicles:
                new_vehicle = combine_vehicles_keys(vehicle)
                new_vehicles.append(new_vehicle)

        self.data_dict['Insurance']['Transaction']['Customer']['Units']['Auto']['Vehicle'] = new_vehicles
        self.save_dict_as_json_file(json_destination_path)


def parse_xml_to_dict(xml_source_path):
    if not path.exists(xml_source_path):
        print("file doesn't exist")
        return False
    with open(xml_source_path) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        xml_file.close()
        return data_dict


def parse_csv_to_dict(csv_source_path):
    if not path.exists(csv_source_path):
        print("file doesn't exist")
        return False
    with open(csv_source_path) as csv_file:
        dict_reader = csv.DictReader(csv_file)
        ordered_dict_from_csv = list(dict_reader)[0]
        data_dict = dict(ordered_dict_from_csv)
        csv_file.close()
        return data_dict


def main(argv):
    # reading commands
    try:

        opt, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print("command not valid")
        sys.exit(2)

    # args[0] is the file format
    # args[1] is the file name
    # length has to be greater than two to start checking the command
    if len(args) >= 2:
        # loop will start from second position, the first one is file format
        for index in range(1, len(args)):
            file_name = args[index]
            file_format = args[0]
            input_file_path = get_input_path(file_format, file_name)
            # output_file_path = get_output_path(file_format, file_name)
            if file_format == 'csv':
                file = FileParser(input_file_path, parse_csv_to_dict)
                file.save_dict_to_mongodb(file_format)
            elif file_format == 'xml':
                file = FileParser(input_file_path, parse_xml_to_dict)
                # file.save_dict_to_mongodb(file_format)
                enriched_file_name = file_name + "_enriched"
                output_file_path = get_output_path(file_format, enriched_file_name)
                file.decode_vin_vehicle(output_file_path)

    else:
        print("command not valid")


def get_input_path(file_format, file_name):
    return str(pathlib.Path().resolve()) + "/input/" + file_format + "/" + file_name + "." + file_format


def get_output_path(file_format, file_name):
    return str(pathlib.Path().resolve()) + "/output/" + file_format + "/" + str(time.time()) + "_" + file_name + ".json"


def combine_vehicles_keys(vehicle):
    vehicle_vin_number = vehicle['VinNumber']
    model_year = vehicle['ModelYear']
    # call api
    response = requests.get(
        "https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvaluesextended/" + vehicle_vin_number + "?format=json&modelyear=" + model_year + "")
    json_result = response.json()
    # the new vehicle contain both old keys and new keys
    new_vehicle = {
        "@id": vehicle['@id'],
        "Make": vehicle['Make'],
        "VinNumber": vehicle['VinNumber'],
        "ModelYear": vehicle['ModelYear'],
        # the api returns the result in array so i have to take first index (0)
        "model": json_result['Results'][0]['Model'],
        "manufacturer": json_result['Results'][0]['Manufacturer'],
        "plant_country": json_result['Results'][0]['PlantCountry'],
        "vehicle_type": json_result['Results'][0]['VehicleType']
    }
    return new_vehicle


if __name__ == "__main__":
    main(sys.argv[1:])
