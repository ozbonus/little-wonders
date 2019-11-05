# This script will process an entire directory of HTML files in the format you
# can find at these three locations:
# https://tigerweb.geo.census.gov/tigerwebmain/Files/acs19/tigerweb_acs19_roads_pri_us.html
# https://tigerweb.geo.census.gov/tigerwebmain/TIGERweb_roads_sec.html
# https://tigerweb.geo.census.gov/tigerwebmain/TIGERweb_roads_loc.html
# The processing will place CSV files with the same base names as the HTML
# files in the same directory.


import pdb
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from concurrent.futures import ProcessPoolExecutor
import csv


PARSER = argparse.ArgumentParser()
PARSER.add_argument('-d', '--directory', required=True)
PARSER.add_argument('-p', '--processes', default=None)


def get_files(path):
    return path.glob('*.html')


def html_csv(in_file):

    header = ['MTFCC', 'OID', 'RTTYP', 'PREDIR', 'PREDIRABRV', 'PREQUAL',
            'PREQUALABRV', 'PRETYP', 'PRETYPEABRV', 'SUFDIR', 'SUFDIRABRV',
            'SUFQUAL', 'SUFQUALABRV', 'SUFTYP', 'SUFTYPEABRV', 'BASENAME',
            'NAME']

    out_file = in_file.absolute().with_suffix('.csv')

    with open(in_file, 'r') as html:
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find(text='MTFCC').find_parent('table')
        
        with open(out_file, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',')
            writer.writerow(header)
            for tr in table.find_all('tr')[1:]:
                row = [cell.get_text(strip=True) for cell in tr.find_all('td')]
                writer.writerow(row)


def main():

    args = PARSER.parse_args()
    path = Path(args.directory)
    files = get_files(path)

    with ProcessPoolExecutor(max_workers=args.processes) as executor:
        executor.map(html_csv, files)


if __name__ == '__main__':

    main()