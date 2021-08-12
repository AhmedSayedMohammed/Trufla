import csv
import getopt
import json
import pathlib
import sys
import time
import xmltodict
import os.path
from os import path


class FileParser:
    input_path = None
    output_path = None
    file_format = None

    def __init__(self, input_path, output_path, file_format):
        self.input_path = input_path
        self.output_path = output_path
        self.file_format = file_format
        if file_format == 'csv':
            parse_csv_to_json(input_path, output_path)
        elif file_format == 'xml':
            parse_xml_to_json(input_path, output_path)


def parse_xml_to_json(xml_source_path, json_destination_path):
    if not path.exists(xml_source_path):
        print("file doesn't exist")
        return False
    with open(xml_source_path) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        xml_file.close()
        parse_dict_to_json(data_dict, json_destination_path)


def parse_csv_to_json(csv_source_path, json_destination_path):
    if not path.exists(csv_source_path):
        print("file doesn't exist")
        return False
    with open(csv_source_path) as csv_file:
        dict_reader = csv.DictReader(csv_file)
        ordered_dict_from_csv = list(dict_reader)[0]
        dict_from_csv = dict(ordered_dict_from_csv)
        csv_file.close()
        parse_dict_to_json(dict_from_csv, json_destination_path)


def parse_dict_to_json(dict_to_parse, json_destination_path):
    json_data = json.dumps(dict_to_parse)
    with open(json_destination_path, "w") as json_file:
        json_file.write(json_data)
        json_file.close()
        print("file saved")


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
            FileParser(input_file_path, output_file_path, args[0])
    else:
        print("command not valid")


def get_input_path(file_format, file_name):
    return str(pathlib.Path().resolve()) + "/input/" + file_format + "/" + file_name + "." + file_format


def get_output_path(file_format, file_name):
    return str(pathlib.Path().resolve()) + "/output/" + file_format + "/" + str(time.time()) + "_" + file_name + ".json"


if __name__ == "__main__":
    main(sys.argv[1:])
