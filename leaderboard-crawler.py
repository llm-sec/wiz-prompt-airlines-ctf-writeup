import json
from dataclasses import dataclass

import requests  # pip install requests
import urllib3
from bs4 import BeautifulSoup  # pip install beautifulsoup4

"""

此脚本用于把 https://promptairlines.com/leaderboard 爬下来

"""

urllib3.disable_warnings()


@dataclass
class Person:
    """
    结构化一点，更容易看明白数据结构
    """

    def __init__(self):
        super().__init__()

        # 人名
        self.name = ''
        # 所在国家或地区，是对应的大写代码
        self.country = ''
        # 主页的链接，这个是注册的时候自己填写的
        self.profile_url = ''
        # 得分，满分50分，10分上榜
        self.score = 0


def run_crawler(output_json_line_file_path: str):
    """
    抓取整个列表
    :param output_json_line_file_path: 抓取结果保存到的文件位置
    :return:
    """
    page_no = 1
    while True:

        person_list = crawl_by_page_no(page_no)
        if not len(person_list):
            break

        with open(output_json_line_file_path, 'a') as f:
            for person in person_list:
                line = json.dumps(person.__dict__, ensure_ascii=False) + '\n'
                f.write(line)
                print(line)

        page_no += 1
        print(f'pageNo {page_no} done.')

    print('all done')


def crawl_by_page_no(page_no: int) -> list[Person]:
    """
    解析一页人的信息
    :param page_no:
    :return:
    """
    url = f'https://promptairlines.com/leaderboard?page={page_no}'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
    }
    r = requests.get(url, headers=headers, allow_redirects=False, verify=False)
    doc = BeautifulSoup(r.text, 'html.parser')
    person_elt_list = doc.select('table.min-w-full > tbody > tr')
    person_list = []
    for person_elt in person_elt_list:
        person = parse_person_information(person_elt)
        person_list.append(person)
    return person_list


def parse_person_information(person_elt) -> Person:
    """
    解析单个人的信息
    :param person_elt:
    :return:
    """
    person = Person()

    # 国家和名字
    person.name = person_elt.select('td:nth-of-type(1)')[0].text.strip()
    person.country = person_elt.select('td:nth-of-type(1) img')[0]['alt'].strip().replace(' flag', '')

    # 主页链接
    person.profile_url = person_elt.select('td:nth-of-type(2)')[0].text.strip()

    # 得分
    person.score = int(person_elt.select('td:nth-of-type(3)')[0].text.strip())

    return person


if __name__ == '__main__':
    run_crawler('person.jsonl')
