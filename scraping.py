# coding:utf-8


import os
import re
import requests
from bs4 import BeautifulSoup

import dutil


image_dir = "./blog_images"
blog_data_dir = "./blog_data"


class Blog:
    """
    欅坂のブログは、
    一つのarticleがあるBlogと、
    複数のarticleがあるPageで構成されている
    """
    def __init__(self):
        self.url        = None
        self.created_at = None
        self.title      = None
        self.author     = None
        self.text       = None
        self.images     = []   #複数ある場合もある
        self.article    = None # 一応純粋なarticleも保存しとく

    def set_url(self, url):
        self.url = url
    
    def _get_article(self):
        # TODO: 例外処理する
        r = requests.get(self.url)
        soup = BeautifulSoup(r.content, 'html.parser')
        self.article = soup.find('article')
    
    def set_data(self, article):
        """
        page経由で取得の時にarticleからsetできるように設計
        """
        innerHead = article.find("div", {"class": "innerHead"})
        title = innerHead.find("h3").text.strip()
        author = innerHead.find("p", {"class": "name"}).text
        author = "".join(author.split())
        created_at = article.find("div", {"class": "box-bottom"}).text.strip()
        created_at = "T".join(created_at.split(" "))
        created_at = "-".join(created_at.split("/"))
        pattarn = '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}'
        created_at = re.match(pattarn , created_at).group()
        text = article.find("div", {"class": "box-article"}).text
        images = article.find_all("img")

        try:
            images = [i["src"] for i in images]
        except KeyError:
            images = []
        
        self.created_at = created_at
        self.title      = title
        self.author     = author
        self.text       = text
        self.images     = images


    def set_data_from_url(self, url):
        self.set_url(url)
        self._get_article()
        self.set_data(self.article)


class Page(Blog):
    def __init__(self, page_url):
        self.page_url = page_url
        self.all_data = []
        self.set_data_from_url()

    def __len__(self):
        return len(self.all_data)
    
    def set_data_from_url(self):
        r = requests.get(self.page_url)
        soup = BeautifulSoup(r.content, 'html.parser')
        articles = soup.find_all('article')
        for article in articles:
            b = Blog()
            b.set_data(article)
            self.all_data.append(b)

    def save_image(self, image_dir):
        for b in self.all_data:
            imgs = b.images
            name = b.author
            created_at = b.created_at
            DIR = image_dir + "/" + name
            if not os.path.exists(DIR):
                os.makedirs(DIR)
            if imgs != []:
                for idx, i in enumerate(imgs):
                    ext = i.split(".")[-1]
                    filename = "{}/{}_{}.{}".format(DIR, created_at, str(idx), ext)
                    img = dutil.download_image(i)
                    if img != None:
                        dutil.save_image(filename, img)


def get_member_list():
    """ メンバーのリストを取得する
    """
    url = "https://www.keyakizaka46.com/s/k46o/search/artist?ima=0000"
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    box_member = soup.find_all("div", {'class': 'box-member'})
    box_member = box_member[-1].find_all("li")
    
    member_dict = {}
    for i in box_member:
        href = i.find("a").get("href")
        id_ = href.split("/")[-1].rstrip("?ima=0000")
        img_url = i.find("img")["src"]
        author = i.find("p", {"class": "name"}).text.strip()
        birth = i.find("p", {"class": "birth"}).text.strip()
        member_dict[author] = [id_, href, img_url, birth]
    return member_dict

def test_get_blog():
    b = Blog()
    #b.set_data_from_url("http://www.keyakizaka46.com/s/k46o/diary/detail/15824?ima=0000&cd=member")
    b.set_data_from_url("http://www.keyakizaka46.com/s/k46o/diary/detail/15557?ima=0000&cd=member")
    print("url:"       , b.url)
    print("created_at:", b.created_at)
    print("title:"     , b.title     )
    print("author:"    , b.author    )
    print("text:"      , b.text      )
    print("images:"    , b.images    )

def test_get_page():
    page_number = 1
    p = Page("http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&page=1&cd=member&ct=03")
    print("url:"       , p.all_data[page_number].url)
    print("created_at:", p.all_data[page_number].created_at)
    print("title:"     , p.all_data[page_number].title     )
    print("author:"    , p.all_data[page_number].author    )
    #print("text:"      , p.all_data[page_number].text      )
    print("images:"    , p.all_data[page_number].images    )
    print("len:"       , len(p))
    
    # 写真の保存
    #p.save_image()

def search_blog2save(name, start_page_num=0, max_page_num=10):
    members = get_member_list()
    for i in range(start_page_num, max_page_num):
        print("...{}".format(max_page_num - i))
        url = "http://www.keyakizaka46.com/s/k46o/diary/member/list?ima=0000&page={}&cd=member&ct={}".format(i, members[name][0])
        p = Page(url)
        if len(p) == 0:
            continue
        
        # 写真を保存する
        p.save_image(image_dir)
        path = p.page_url.split("/")[-1]
        dutil.save_pickle(p, path, blog_data_dir)


if __name__ == "__main__":
    m = get_member_list()
    for i in m.keys(): # メンバーの名前のリスト
        print(i)
        search_blog2save(i)
