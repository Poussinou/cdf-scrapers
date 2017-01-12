from collections import OrderedDict
from html.parser import HTMLParser
import argparse
import datetime
import json
import os
import re
import sys
import time
import urllib.request


def strip(data):
    """Helper function for striping whitespace."""
    return data.strip('\u00a0\\n\\t')

class PageParser(HTMLParser):
    """Parser for CDF Lab Machine Usage page."""

    def __init__(self):
        HTMLParser.__init__(self)
        self._inDiv = False
        self._inTable = False
        self._lastStatus = ''
        self._inParagraph = False

        self.timestamp = ''
        self.data = []

    def handle_starttag(self, tag, attrs):
        # Only read contents of div.art-PostContent
        if tag == 'div':
            for name, val in attrs:
                if name == 'class' and val == 'art-PostContent':
                    self._inDiv = True

        if self._inDiv:
            if tag == 'table':
                self._inTable = True

            # Traffic light image in table rows
            if tag == 'img':
                for name, val in attrs:
                    if name == 'title':
                        self._lastStatus = val == 'up'

            # Last updated time
            if tag == 'p':
                self._inParagraph = True


    def handle_data(self, data):
        if not (self._inDiv and strip(data)):
            return

        # Status rows
        if self._lastStatus and self._inTable:
            self.data.append((strip(data), self._lastStatus))

        # "Status last updated Mon Jan  9 10:51:04 EST 2017"
        if self._inParagraph:
            rawTime = re.sub(' +', ' ', data.strip('\u00a0\\nStatus last updated '))
            parsedTime = time.strptime(rawTime, '%a %b %d %H:%M:%S EST %Y')
            self.timestamp = time.strftime('%Y-%m-%d %H:%M:%S EST', parsedTime)

    def handle_endtag(self, tag):
        if self._inDiv:
            if tag == 'table':
                self._inTable = False

            if tag == 'div':
                self._inDiv = False


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(
        description='Scraper for CDF system status data.')
    argparser.add_argument(
        '-o', '--output',
        help='The output path. Defaults to current directory.',
        required=False)
    argparser.add_argument(
        '-f', '--filename',
        help='The output filename. Defaults to "cdfstatus.json".',
        required=False)

    args = argparser.parse_args()
    output = '.'
    filename = 'cdfstatus.json'

    # Get data
    html = str(urllib.request.urlopen(
        'http://www.teach.cs.toronto.edu/resources/cdf_system_status.html').read())
    parser = PageParser()
    parser.feed(html)

    data = OrderedDict([
        ('timestamp', parser.timestamp)
    ])

    for key, val in parser.data:
        data[key] = val

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
