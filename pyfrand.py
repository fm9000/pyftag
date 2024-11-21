#!/usr/bin/env python3
from pathlib import Path
import random
import argparse
import logging
import sys

parser = argparse.ArgumentParser()

parser.add_argument('-n', '--newcount', default=5)      # option that takes a value
parser.add_argument('-b', '--buffer', default=2)      # option that takes a value
parser.add_argument('--path', type=Path, default=Path().cwd())
parser.add_argument( '-log',
                     '--loglevel',
                     default='warning',
                     help='Provide logging level. Example --loglevel debug, default=warning' )
parser.add_argument('--unrandom', action="store_true")      # option that takes a value

args = parser.parse_args()
logging.basicConfig( level=args.loglevel.upper() )

newcount = int(args.newcount)
buffer = int(args.buffer)

    

alle_dateien = list(args.path.glob("*"))

if args.unrandom:
    logging.debug("Unrandom requested")

    dict_names = {}
    try:
        for PO in alle_dateien:
            random_name = PO.name
            number, old_name = PO.name.split("_", 1)

            dict_names[PO] = (number, old_name)

        [int(tup[0]) for tup in dict_names.values()]
    except ValueError as e:
        logging.error("Not all files have the random number prefix!")
        sys.exit()
    
    for PO, tup in dict_names.items():
        PO.rename(tup[1])
    sys.exit()

alle_dateien.sort(key = lambda po: po.stat().st_mtime, reverse=True)

neu = alle_dateien[:newcount]
alt = alle_dateien[newcount:]

logging.debug(f"Length of new files: {len(neu)}")
logging.debug(f"Length of old files: {len(alt)}")
random.shuffle(neu)
random.shuffle(alt)

sequenz = alt[:buffer] + neu + alt[buffer:]

n_fill = len(str(len(alle_dateien)))
logging.debug(f"Length zfill: {n_fill}")

for i, PO in enumerate(sequenz):
    new_name = f"{str(i).zfill(n_fill)}_{PO.name}"
    logging.debug(f"{PO.name} --> {new_name}")
    PO.rename(new_name)
