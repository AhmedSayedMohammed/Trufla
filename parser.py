import csv
import getopt
import json
import pathlib
import sys
import time
import xmltodict
from os import path

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
    try:
        opt, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print("command not valid")
        sys.exit(2)

    # args[0] is the file format
    # args[1] is the file name
    if len(args) >= 2:
        for index in range(1, len(args)):
            input_file_path = get_input_path(args[0], args[index])
            output_file_path = get_output_path(args[0], args[index])
            if args[0] == 'csv':
                file = FileParser(input_file_path, parse_csv_to_dict)
                file.save_dict_to_mongodb(args[0])
            elif args[0] == 'xml':
                file = FileParser(input_file_path, parse_xml_to_dict)
                file.save_dict_to_mongodb(args[0])

    else:
        print("command not valid")


def get_input_path(file_format, file_name):
    return str(pathlib.Path().resolve()) + "/input/" + file_format + "/" + file_name + "." + file_format


def get_output_path(file_format, file_name):
    return str(pathlib.Path().resolve()) + "/output/" + file_format + "/" + str(time.time()) + "_" + file_name + ".json"


if __name__ == "__main__":
    main(sys.argv[1:])
