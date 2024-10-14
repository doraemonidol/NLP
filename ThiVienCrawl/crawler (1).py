import requests
from bs4 import BeautifulSoup
# json
# import class to store the content in json format
import json
from time import sleep
from random import randint
from tqdm import tqdm

class Data:
    def __init__(self):
        self.data = {
            "title_cn": "",
            "title_hv": "",
            "title_vi": "",
            "content_cn": "",
            "content_hv": "",
            "content_vi": "",
            "description": "",
            "member_translation": [],
            "url": "",
            "tags": []
        }
        self.mask = {
            "title_cn": False,
            "title_hv": False,
            "title_vi": False,
            "content_cn": False,
            "content_hv": False,
            "content_vi": False,
            "description": False,
            "member_translation": 0,
            "url": False,
            "tags": False
        }

    def set(self, key, value):
        if key == "member_translation":
            self.data[key].append(value)
            self.mask[key] += 1
        elif key == "tags":
            self.data[key].append(value)
            self.mask[key] = True
        else:
            self.data[key] = value
            self.mask[key] = True

    def get(self, key):
        return self.data[key]

class Crawler:
    def __init__(self):
        self.parsed_content = []

    def __fetch__(self):
        r = requests.get(self.url, headers={'User-Agent': 'Mozilla/5.0'})
        r.encoding = 'utf-8'
        html = r.text
        return html

    def to(self, url):
        self.url = url
        self.html = self.__fetch__()
        return self

    def get_random(self):
        pass

    def parse(self):
        soup = BeautifulSoup(self.html, 'html.parser')
        for br in soup.find_all("br"):
             br.insert_after("\n")
        data = Data()
        data.set("tags", soup.find_all("meta", {"name": "keywords"})[0]["content"].split(","))
        data.set("url", self.url)
        full_title = soup.find_all("h1")[0].text
        try:
            extracted_title_vi = full_title.split(" • ")[1]
            data.set("title_vi", extracted_title_vi)
        except:
            pass
        extracted_title_hv = full_title.split(" • ")[0].split(" ")[-1]
        extracted_title_cn = ' '.join(full_title.split(" • ")[0].split(" ")[0:-1])
        data.set("title_cn", extracted_title_cn)
        data.set("title_hv", extracted_title_hv)
        # <p class="HanChinese transcriptable" data-han-lang="hv" lang="zh-Hant">刳血書成欲寄音，<br/>孤飛寒雁塞雲深。<br/>幾家愁對今霄月，<br/>兩處茫然一種心。</p>

        try:
            content_cn = soup.find_all("p", {"lang": "zh-Hant"})[0].text
            data.set("content_cn", content_cn)
        except:
            raise Exception("Not Han Chinese content found")

        # <p class="HanChinese transcriptable" data-han-lang="hv" lang="zh-Hant">刳血書成欲寄音，<br/>孤飛寒雁塞雲深。<br/>幾家愁對今霄月，<br/>兩處茫然一種心。</p><p>&nbsp;</p><h4><strong>Ai phu lỗ</strong></h4><p>Khô huyết thư thành dục ký âm,<br/>Cô phi hàn nhạn tái vân thâm.<br/>Kỷ gia sầu đối kim tiêu nguyệt,<br/>Lưỡng xứ mang nhiên nhất chủng tâm.</p><p>&nbsp;</p>
        #                                 <h4><strong>Dịch nghĩa</strong></h4>
        #                                 <p>Chích máu viết thư muốn gửi lời,<br/>Cánh nhạn lạnh lùng bay xuyên vào đám mây ngoài quan ải.<br/>Bao nhiêu nhà buồn ngắm bóng trăng đêm nay?<br/>Đôi nơi xa cách nhưng tấm lòng nhớ thương vẫn chỉ là một.</p>
        # content_cn = 刳血書成欲寄音，<br/>孤飛寒雁塞雲深。<br/>幾家愁對今霄月，<br/>兩處茫然一種心。
        # content_hv = Khô huyết thư thành dục ký âm,<br/>Cô phi hàn nhạn tái vân thâm.<br/>Kỷ gia sầu đối kim tiêu nguyệt,<br/>Lưỡng xứ mang nhiên nhất chủng tâm.
        # content_vi = Chích máu viết thư muốn gửi lời,<br/>Cánh nhạn lạnh lùng bay xuyên vào đám mây ngoài quan ải.<br/>Bao nhiêu nhà buồn ngắm bóng trăng đêm nay?<br/>Đôi nơi xa cách nhưng tấm lòng nhớ thương vẫn chỉ là một.
        # The content_vi might be optional, based on <h4><strong>Dịch nghĩa</strong></h4> appearance
        
        content_hv = soup.find_all("p", {"lang": "zh-Hant"})[0].find_next_sibling("p").find_next_sibling("p").text
        data.set("content_hv", content_hv)

        try:
            # From soup.find_all("p", {"lang": "zh-Hant"})[0]
            # Find <h4><strong>Dịch nghĩa</strong></h4>
            # Then find the next <p> tag
            # Then get the text
            content_vi = soup.find_all("p", {"lang": "zh-Hant"})[0].find_next_sibling("h4").find_next_sibling("h4").find_next_sibling("p").text
            data.set("content_vi", content_vi)
        except:
            pass

        try:
            # From soup.find_all("p", {"lang": "zh-Hant"})[0]
            # Find <h4><strong>Dịch nghĩa</strong></h4>
            # Then find the next <p> tag
            # Then get the text
            description = soup.find_all("div", {"class": "poem-content"})[0].find_next_sibling("div").text
            # print(description)
            data.set("description", description)
        except:
            pass

        # There might be multiple member translations
        # Each of them has:
        # <h4 class="post-title"><a id="REPLY78708"></a>Bản dịch của <a href="/translator/Ho%C3%A0ng+%C4%90%C3%ACnh+Thi">Hoàng Đình Thi</a></h4><p class="post-info small">Gửi bởi <a href="/Ho%C3%A0ng-%C4%90%C3%ACnh-Thi/member-GI9qZKC9bqDPcxa9lttDlA" >Hoàng Đình Thi</a> ngày 12/01/2022 16:32<br/>Đã sửa 2 lần, lần cuối bởi <a href="/Ho%C3%A0ng-%C4%90%C3%ACnh-Thi/member-GI9qZKC9bqDPcxa9lttDlA" >Hoàng Đình Thi</a> ngày 29/11/2022 05:06</p></div>
        #                 </div><div class="post-content"><p>Chích máu đề thư muốn gửi lời,<br/>Nhạn bay lẻ bóng chốn biên khơi.<br/>Bao nhà sầu não nhìn trăng lạnh,<br/>Một giọt lệ rơi, hai phuơng trời.</p>

        all_member_translations_place = soup.find_all("div", {"class": "post-content"})
        for member_translation_place in all_member_translations_place:
            member_translation = member_translation_place.find_all("p")[0].text
            if member_translation.count("\n") != content_cn.count("\n"):
                continue
            data.set("member_translation", member_translation)

        self.parsed_content.append(data)
        return self

    def save(self, file_name):
        # Save the parsed content to a file with json format with utf-8 encoding
        that_ngon_tu_tuyet = []
        ngu_ngon_tu_tuyet = []
        that_ngon_bat_cu = []
        ngu_ngon_bat_cu = []
        others = []
        for data in self.parsed_content:
            if "thất ngôn tứ tuyệt" in [tag.lower() for tag in data.get("tags")[0]]:
                that_ngon_tu_tuyet.append(data.data)
            elif "ngũ ngôn tứ tuyệt" in [tag.lower() for tag in data.get("tags")[0]]:
                ngu_ngon_tu_tuyet.append(data.data)
            elif "thất ngôn bát cú" in [tag.lower() for tag in data.get("tags")[0]]:
                that_ngon_bat_cu.append(data.data)
            elif "ngũ ngôn bát cú" in [tag.lower() for tag in data.get("tags")[0]]:
                ngu_ngon_bat_cu.append(data.data)
            else:
                others.append(data.data)
        with open(file_name, "w", encoding="utf-8") as f:
            json.dump({
                "thất ngôn tứ tuyệt": that_ngon_tu_tuyet,
                "ngũ ngôn tứ tuyệt": ngu_ngon_tu_tuyet,
                "thất ngôn bát cú": that_ngon_bat_cu,
                "ngũ ngôn bát cú": ngu_ngon_bat_cu,
                "others": others
            }, f, ensure_ascii=False)
        return self

# link = "https://www.thivien.net/V%C6%B0%C6%A1ng-An-Th%E1%BA%A1ch/Ho%C3%A0i-Chung-s%C6%A1n/poem-EJVsHAfe5zRvjli0I3auRw"
# c = Crawler()
# c.to(link).parse()
# c.save("/Users/hoangtheanh/Documents/thivien-crawler/data/test.json")

def automatic_crawl(links, file_name):
    c = Crawler()
    i = 1
    try:
        for _ in range(5000):
            while i <= len(links):
                print(i)
                try:
                    link = "https://www.thivien.net" + links[i - 1]
                    print(link)
                    c.to(link).parse()
                    # sleep(randint(1, 3))
                    i += 1
                except Exception as e:
                    if "Not Han Chinese content found" in str(e):
                        i += 1
                        continue
                    else:
                        sleep(4)
                        break
        c.save(file_name)
    except:
        c.save(file_name)

with open("3.txt", "r", encoding='utf-8') as f:
    list_of_poems = f.readlines()
    links = [poem.split("\t")[-1].strip() for poem in list_of_poems]

print(links)

automatic_crawl(links, "thivien_2.json")


