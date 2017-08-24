from bs4 import BeautifulSoup
import requests
# import re
from urllib3.util import url
import os
import re
import pathlib
from datetime import datetime
import time


def iter_found_items(items):
    return [item.text for item in items]

# re.compile('[.*?]')
PATH = os.path.realpath(__file__)
RUN_COUNT = 10000
URL = f'https://en.wikipedia.org/wiki/Special:Random'
outs = []
pattern = r'(\[\d+\])'
pattern_compiled = re.compile(pattern)


def get_dt():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class WikipediaEntry:
    def __init__(self, _id, hit_url):
        self.id = _id
        self.url, self.content = WikipediaEntry.get_req(hit_url)
        self.file_name = url.parse_url(self.url).request_uri.replace('/wiki/', '')
        self.title = self.file_name.replace('_', ' ')
        self.file_path = self.get_file_path()
        self.url_string = f'{url.parse_url(self.url)}'
        self.soup = self.soupenate()
        self.texts = iter_found_items(self.soup.find_all('p'))
        self.__dolog__()

    def get_file_path(self):
        path = pathlib.Path(PATH)
        path = path.parent
        if not path.exists():
            path.mkdir()

        path = pathlib.Path(os.path.join(str(path), 'wikipedia'))

        if not path.exists():
            path.mkdir()

        file_name = self.file_name.replace('\\', '_')
        return os.path.join(str(path), f'{file_name}.txt')

    def write_file(self):
        if len(self.texts) > 0:
            pathlib_path = pathlib.Path(self.file_path)
            if not pathlib_path.is_file():
                joined = '\n'.join(self.texts)
                while joined.__contains__('\n\n'):
                    joined = joined.replace('\n\n', '\n')
                if joined.endswith('\n'):
                    joined = joined[:-2]
                if len(joined) > 0:
                    matched = pattern_compiled.findall(joined)
                    if len(matched) > 0:
                        joined = pattern_compiled.sub('', joined)
                    joined = f'{self.url_string}\n{get_dt()}\n{joined}'
                    pathlib_path.write_text(joined, 'utf-8')

    def soupenate(self):
        return BeautifulSoup(self.content, 'lxml')

    def __dolog__(self):
        print(f'Run Number: {self.id}\nTitle: {self.title}\nURL: {self.url_string}\nItems: {len(self.texts)}\n\n')

    @staticmethod
    def get_req(string: str):
        """
        Return res from url string.
        :param string:
        :return:
        """
        res = requests.get(string)
        return res.url, res.content

for i in range(RUN_COUNT):
    time.sleep(0.001)
    if i % 100 == 0:
        print(f'At i: {i}')
    outs.append(WikipediaEntry(i, URL))

print(f'Total: {len(outs)}')

counter = 0
for out in outs:
    out.write_file()
    time.sleep(0.001)
    if counter % 100 == 0:
        print(f'At i: {counter}')
    counter += 0
