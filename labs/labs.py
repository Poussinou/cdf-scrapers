from collections import OrderedDict
from html.parser import HTMLParser
import argparse
import datetime
import json
import os
import sys
import time
import urllib.request


class PageParser(HTMLParser):
    """Parser for CDF Lab Machine Usage page."""

    # Flag for whether an element should be parsed
    read_data = False

    # A data row contains 6 cells
    row_cell = 0

    # List of lab rooms/data
    data = []

    # Timestamp
    timestamp = ''

    def handle_starttag(self, tag, attrs):
        # Only read <td> tags
        if (tag == 'td'):
            self.read_data = True

    def handle_data(self, data):
        if (self.read_data):
            if self.row_cell == 0:
                if (data != 'NX'):
                    data = 'BA ' + data

                self.data.append(OrderedDict([
                    ('name', data)
                ]))

            elif self.row_cell == 1:
                self.data[-1]['available'] = int(data)

            elif self.row_cell == 2:
                self.data[-1]['busy'] = int(data)

            elif self.row_cell == 3:
                self.data[-1]['total'] = int(data)

            elif self.row_cell == 4:
                self.data[-1]['percent'] = float(data)

            elif self.row_cell == 5:
                if (self.timestamp == ''):
                    # Attempt to compensate for changing timezones,
                    # possibly due to daylight savings
                    raw_time = data.strip('\u00a0\\n')
                    if 'EST' in raw_time:
                        timestamp = time.strptime(, '%a %b %d %H:%M:%S EST %Y')
                    elif 'EDT' in raw_time:
                        timestamp = time.strptime(, '%a %b %d %H:%M:%S EDT %Y')

                    if timestamp:
                        self.timestamp = time.strftime(
                            '%Y-%m-%d %H:%M:%S EST', timestamp)

                self.row_cell = -1

            self.row_cell += 1
            self.read_data = False

if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Scraper for CDF lab data.')
    argparser.add_argument(
        '-o', '--output',
        help='The output path. Defaults to current directory.',
        required=False)
    argparser.add_argument(
        '-f', '--filename',
        help='The output filename. Defaults to "cdflabs.json".',
        required=False)

    args = argparser.parse_args()
    output = '.'
    filename = 'cdflabs.json'

    # Get data
    html = str(urllib.request.urlopen(
        'http://www.teach.cs.toronto.edu/usage/usage.html').read())
    parser = PageParser()
    parser.feed(html)

    data = OrderedDict([
        ('timestamp', parser.timestamp),
        ('labs', parser.data)
    ])

    # Output
    if args.output:
        if not os.path.exists(args.output):
            os.makedirs(args.output)

        output = args.output

    if args.filename:
        filename = args.filename

    if args.output or args.filename:
        with open('%s/%s' % (output, filename), 'w+') as outfile:
            json.dump(data, outfile)
    else:
        print(json.dumps(data))
