from collections import OrderedDict
from lxml import html
import argparse
import datetime
import json
import os
import re
import requests
import sys
import time


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
    page = requests.get('http://www.teach.cs.toronto.edu/resources/cdf_system_status.html')
    tree = html.fromstring(page.content)

    # "Status last updated Mon Jan  9 10:51:04 EST 2017"
    raw_time = str(tree.xpath('//div[@class="art-PostContent"]/p/text()')[0]).strip('\u00a0\\nStatus last updated ')
    raw_time = re.sub(' +', ' ', raw_time)
    parsed_time = time.strptime(raw_time, '%a %b %d %H:%M:%S EST %Y')
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S EST', parsed_time)

    # Table cells
    status_imgs = tree.xpath('//div[@class="art-PostContent"]/table/tr/td/img/@title')
    status_names = tree.xpath('//div[@class="art-PostContent"]/table/tr/td/text()')

    data = OrderedDict([
        ('timestamp', timestamp)
    ])

    for row in range(len(status_imgs)):
        data[status_names[row]] = status_imgs[row]

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
