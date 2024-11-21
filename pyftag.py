#!/usr/bin/env python3
import argparse
import os
import sys
from pathlib import Path
import logging
from utils import TaglistParser


def GetTags(path: str) -> set[str]:
    try:
        tags = set(os.getxattr(path, attribute="user.xdg.tags").decode("utf8").split(","))
        if not tags == {""}:
            return tags
        else:
            return set()
    except OSError:
        return set()

def SetTags(add_tags: set[str], remove_tags: set[str], path: str) -> None:
    # Retrieve existing tags
    existing_tags = GetTags(path)
    logging.debug(f"Tags already existing for file: {existing_tags}")
    logging.debug(f"Tags that are to be added: {add_tags}")
    logging.debug(f"Tags that are to be removed: {remove_tags}")

    if remove_tags == {"*"}:
        logging.info(f"Remove all existing tags for file {path}")
        remove_tags = existing_tags
    
    new_tags = (existing_tags - remove_tags).union(add_tags)
    logging.debug(f"Tags that will be written: {new_tags}")
    os.setxattr(path, attribute="user.xdg.tags", value=",".join(new_tags).encode("utf8"))




parser = argparse.ArgumentParser()
parser.add_argument("--add", help="Comma separated list of tags that will be added to the files")
parser.add_argument("--remove", help='Comma separated list of tags that will be removed from the files. A single "*" will remove all existing tags.')
parser.add_argument( '-log',
                     '--loglevel',
                     default='warning',
                     help='Provide logging level. Example --loglevel debug, default=warning' )

group = parser.add_mutually_exclusive_group()
group.add_argument('-i', '--input-file', type=argparse.FileType('r'), default=(None if sys.stdin.isatty() else sys.stdin))
group.add_argument('-f', '--files', nargs=argparse.REMAINDER)

args = parser.parse_args()

logging.basicConfig( level=args.loglevel.upper() )


add_tags = TaglistParser(args.add)
remove_tags = TaglistParser(args.remove)

if tag_overlap := add_tags.intersection(remove_tags):
    raise Exception(f"Tag overlap between 'add' and 'remove': {tag_overlap}")

if args.files:
    filepaths = [Path(filepath) for filepath in args.files if Path(filepath).is_file()]

if args.input_file:
    filepaths = [Path(filepath) for filepath in args.input_file.read().splitlines() if Path(filepath).is_file()]

if not add_tags and not remove_tags:
    # Only show existing tags
    logging.debug("No tags given, just showing currently set tags")

    for file in filepaths:
        logging.info(f"{file}: {', '.join(GetTags(file))}")
    sys.exit(0)


# Setting the new tags
for file in filepaths:
    logging.debug(f"Handling file: {file}")
    SetTags(add_tags, remove_tags, file)
