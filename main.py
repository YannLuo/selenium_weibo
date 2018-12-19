from selenium import webdriver
import time
from bs4 import BeautifulSoup
from config import user
import bs4
from selenium.webdriver.common.action_chains import ActionChains
from tqdm import tqdm
from selenium.webdriver.chrome.options import Options
import re
import json
import matplotlib.pyplot as plt


# driver = webdriver.Chrome()
TALL_TPL = re.compile('(?<!\d)1\d{2}(?!\d)')



def login():
    btn = driver.find_element_by_xpath('//*[@id="pl_common_top"]/div/div/div[3]/div[2]/ul/li[3]/a')
    btn.click()
    ipt = driver.find_element_by_name('username')
    ipt.send_keys(user["username"])
    ipt = driver.find_element_by_name('password')
    ipt.send_keys(user["password"])
    btn = driver.find_element_by_css_selector('a.W_btn_a.btn_34px')
    btn.click()


def load_one_page():
    for _ in range(4):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
        time.sleep(3)
    mores = driver.find_elements_by_css_selector('div.WB_text.W_f14>a.WB_text_opt')
    for more in mores:
        ActionChains(driver).move_to_element(more).click().perform()
        time.sleep(0.5)


def goto_next_page():
    btn = driver.find_element_by_css_selector('a.page.next.S_txt1.S_line1')
    btn.click()


def process():
    tall_data = []
    for i in tqdm(range(1, 11)):
        with open('contents/weibo_%d.html' % (i), mode='r', encoding='utf-8') as rf:
            source = rf.read()
        soup = BeautifulSoup(source, "html.parser")
        results = soup.find_all('div', class_='WB_feed_detail clearfix')
        for result in results:
            detail = result.find('div', class_='WB_detail')
            content = result.find('div', class_='WB_text W_f14', attrs={"node-type":"feed_list_content_full"})
            if not content:
                content = result.find('div', class_='WB_text W_f14')
            l = [c.string.strip() for c in content.contents if isinstance(c, bs4.element.NavigableString) and c.string.strip()]
            text = ''.join(l)
            tall_data.append(TALL_TPL.findall(text))
    with open('data.json', mode='w', encoding='utf-8') as wf:
        json.dump(tall_data, wf, indent=4)


def analyze():
    with open('data.json', mode='r', encoding='utf-8') as rf:
        tall_data = json.load(rf)
    tall_data = list(filter(lambda x: x, tall_data))
    tall_data = [[int(t) for t in td] for td in tall_data]
    tall_data = [max(td) for td in tall_data]
    tall_data = list(filter(lambda x: x>165, tall_data))
    print(tall_data)


def main():
    driver.implicitly_wait(30)
    driver.maximize_window()
    URL = 'https://weibo.com/u/6307150091?topnav=1&wvr=6&topsug=1'
    driver.get(URL)
    login()
    btn = driver.find_element_by_xpath('//*[@id="Pl_Official_ProfileFeedNav__19"]/div[2]/div[1]/div/ul/li[1]/a')
    btn.click()
    for i in tqdm(range(1, 11)):
        load_one_page()
        source = driver.page_source
        with open('contents/weibo_%d.html' % (i, ), mode='w', encoding='utf-8') as wf:
            wf.write(source)
        goto_next_page()
    process()
    analyze()


if __name__ == '__main__':
    main()