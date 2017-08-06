#!/usr/bin/env python3

import argparse
import DriveClient as dc


parser = argparse.ArgumentParser(description='Cross Platform Google Drive Client')

parser.add_argument("--search", dest="search_string", type=str)
parser.add_argument("--clone", dest="clone_id", type=str)
parser.add_argument("--sync", action="store_true")

args = parser.parse_args()


def format_item_pretty(item):
    print('{0}.) {1} ({2}) [{3}]'.format(items.index(item), item['name'], item['id'], item['mimeType']))


if args.search_string:
    client = dc.Client()
    items = client.search(args.search_string)
    if items:
        for item in items:
            format_item_pretty(item)
    else:
        print("Search returned no results")

elif args.clone_id:
    client = dc.Client()
    if client.get_file_metadata(args.clone_id):
        clone_id = args.clone_id
    else:  # file id not found
        items = client.search(args.clone_id)
        if items:
            if len(items) > 1:
                print("You request returned more than one result:")
                for item in items:
                    format_item_pretty(item)
                while True:
                    try:
                        choice = int(input("Please enter the index number of the desired file: "))
                    except ValueError:
                        continue
                    else:
                        if 0 <= choice < len(items):
                            break
                clone_id = items[int(choice)]['id']
            else:
                clone_id = items[0]['id']

    client.clone(clone_id)

elif args.sync:
    client = dc.Client()
    client.sync()