import getopt
import json
import pathlib
import sys
import time
import xmltodict


def parse_xml_to_json(xml_source_path, json_destination_path):
    with open(xml_source_path) as xml_file:
        data_dict = xmltodict.parse(xml_file.read())
        xml_file.close()
        json_data = json.dumps(data_dict)

        with open(json_destination_path, "w") as json_file:
            json_file.write(json_data)
            json_file.close()


def main(argv):
    try:
        opt, args = getopt.getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except getopt.GetoptError:
        print("command not valid")
        sys.exit(2)
    if len(args) == 2 and args[0] == 'xml':
        # files have to be in the project folders
        input_file_path = str(pathlib.Path().resolve()) + "/input/xml/" + args[1] + ".xml"
        output_file_path = str(pathlib.Path().resolve()) + "/output/xml/" + str(time.time())+"_" + args[1] + ".json"
        parse_xml_to_json(input_file_path, output_file_path)
    else:
        print("command not valid")


if __name__ == "__main__":
    main(sys.argv[1:])
