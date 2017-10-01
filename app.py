"""
This bot listens to port 5002 for incoming connections from Facebook. It takes
in any messages that the bot receives and echos it back.
"""
from flask import Flask, request
from pymessenger.bot import Bot
from pymessenger import Element
import random
import requests
from bs4 import BeautifulSoup
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from imgurpython import ImgurClient
import configparser
import apiai
import json
import time
import os
import shutil
import jieba

jieba.load_userdict('userdict_disease.txt')
jieba.load_userdict('userdict_normal.txt')

app = Flask(__name__,static_url_path = "/images" , static_folder = "./images/")

config = configparser.ConfigParser()
config.read("config.ini")
ACCESS_TOKEN = config['fb-bot']['ACCESS_TOKEN']
VERIFY_TOKEN = config['fb-bot']['VERIFY_TOKEN']
client_id = config['imgur_api']['Client_ID']
client_secret = config['imgur_api']['Client_Secret']
album_id = config['imgur_api']['Album_ID']
heroku_url = config['heroku']['heroku_url']
CLIENT_ACCESS_TOKEN = config['apiai']['CLIENT_ACCESS_TOKEN']
skype_url = config['skype']['skype_url']

bot = Bot(ACCESS_TOKEN)
imgurclient = ImgurClient(client_id, client_secret)
ai = apiai.ApiAI(CLIENT_ACCESS_TOKEN)

# 停用詞
with open('stopwords.txt', 'r', encoding='utf-8') as f:
    stop_list = f.read().split()
with open('stopwords_add.txt', 'r', encoding='utf-8') as f:
    stop_list += f.read().split()
stop_list.sort(key=len, reverse=True)

# 常用句
read_more = '詳細閱讀'
please_choose = '請選擇'

# 圖片 facebook 專用
normal_1_p = 'https://i.imgur.com/gAzpgJJ.jpg'
normal_2_p = 'https://i.imgur.com/06ZhL7K.jpg'
normal_3_p = 'https://i.imgur.com/5ImqZzS.jpg'
normal_4_p = 'https://i.imgur.com/5jSrqPk.jpg'
normal_5_p = 'https://i.imgur.com/n304KCx.jpg'

shop_1_p = 'https://i.imgur.com/B6PSBol.jpg'
shop_2_p = 'https://i.imgur.com/t0c4Pvw.jpg'
shop_3_p = 'https://i.imgur.com/0i7WQA4.jpg'
shop_4_p = 'https://i.imgur.com/DiQatsa.jpg'
shop_5_p = 'https://i.imgur.com/HmxyYNR.jpg'

health_1_p = 'https://i.imgur.com/zIBeJP8.jpg'
health_2_p = 'https://i.imgur.com/ZdBQwWX.jpg'
health_3_p = 'https://i.imgur.com/g0osqkm.jpg'
health_4_p = 'https://i.imgur.com/wJCdGdb.jpg'
health_5_p = 'https://i.imgur.com/E3Su0iH.jpg'

# 一般客服
normal_service = '一般客服'
normal_1 = 'HOA功能介紹'
normal_1_1 = '什麼是HOA'
normal_1_1_a = 'HOA是一個結合醫療服務與商品購物的平台，可進行線上掛號、看診、購物、及提醒用藥與看診時間。'
normal_1_2 = '如何變成HOA的會員'
normal_1_2_a = '登入HOA時，邀請您綁定您的手機號碼，即可成為一般會員。 即能使用健康購商城，閱讀衛教文章功能。'
normal_1_3 = 'HOA有哪些功能'
normal_1_3_a = 'HOA依您的資料設定而可使用不同的功能，若綁定您的手機號碼與病歷資料，即可享有APP預約掛號、線上購物、觀看衛教文章等多項服務。'

normal_2 = '病歷與門診問題'
normal_2_1 = '如何進行初診掛號'
normal_2_1_a = '初診患者請先填寫「初診病患基本資料」，辦理初診掛號流程。'
normal_2_2 = '如何掛號'
normal_2_2_1 = '請問您有在中國醫看過診嗎?'
normal_2_2_1_1 = '我有在中國醫看過診'
normal_2_2_1_1_a = '點選APP首頁的門診掛號，即可開始選擇看診分院、科別、時間與醫師。'
normal_2_2_1_2 = '我沒有在中國醫看過診'
normal_2_2_1_2_a = '初診請點選APP首頁的門診掛後號，上方會有初診掛號的選項，填寫好基本資料後，即可進行線上掛號囉。'
normal_2_3 = '如何選擇看診醫院'
normal_2_3_a = '您可在APP開啟定位，APP將提供您最接近的分院地址。'

normal_3 = 'My care使用問題'
normal_3_1 = '什麼是My care'
normal_3_1_a = 'Mycare是提供專人掛號、尊榮優診、住院照護、健康諮詢等高品質的醫療服務，與專業團隊「中國醫藥大學附設教學醫院」健康管理師的協助，替會員做好全方位的健康管理。'
normal_3_2 = '如何成為Mycare會員'
normal_3_2_a = '月付$599，即可享有My care會員專有的多項服務。'
normal_3_3 = '使用Mycare有什麼好處'
normal_3_3_a = '提供MyCare會員優質、快速、便利、人性化的高品質服務，讓會員無論是門診、住院、日常保健都享有「顧問式的健康管理服務」。'

normal_4 = '網站瀏覽問題'
normal_4_1 = '中亞健康網是什麼'
normal_4_1_a = '中亞健康網是個資料豐富的醫療資訊的圖書館，供一般民眾遇到身體上的疑難雜症時，可以得到正確的健康概念、用藥資訊以及疾病照護就診的資訊。'
normal_4_2 = '如何快速搜尋文章'
normal_4_2_a = '於中亞健康網首頁左上角的關鍵字搜尋格，輸入欲查詢之資料，即可得到相關資訊。'
normal_4_3 = '如何轉發喜歡的文章'
normal_4_3_a = '在衛教文章內右上角有FB分享選項，點選即可分享好文章!'

normal_5 = 'APP 操作問題'
normal_5_1 = '要如何綁定病歷'
normal_5_1_a = '登入HOA APP首頁後，點選左上角選單，內有"病歷一覽"選項，點選後可進行病歷綁定流程'
normal_5_2 = '如何線上預約健檢'
normal_5_2_a = '由中國醫的Call center進行資料輸入與掛號'
normal_5_3 = '要怎麼掛號'
normal_5_3_a = '登入HOA APP首頁後，即可看到"門診掛號"選項，可開啟定位，APP會顯示最近院所之距離，或您可選擇常去的院所，選擇院所與欲掛號科別後，輸入預約日期與醫師，即可點選未額滿之診間掛號。'

# 購物客服
shop_service = '購物客服'
shop_1 = '收貨與發票收據開立問題'
shop_1_1 = '能更改訂單的收貨地址嗎'
shop_1_1_a = '完成訂貨付款後，商品尚未出貨之前，您最多可更改一次地址。如果貨物已經寄送出去，恕無法為您提供更改地址的服務。請至訂單查詢進行編輯'
shop_1_2 = '是否能捐贈發票'
shop_1_2_a = '(尚未確認)'
shop_1_3 = '是否可修改發票內容'
shop_1_3_a = '發票內容無法修正，請您於購買時，再次確認您的發票訊息是否正確。'

shop_2 = '商品分類問題'
shop_2_1 = 'HOA有哪些分類的商品'
shop_2_1_a = 'HOA商城提供精準、方便以及專業的服務，是商城的特色。目前區分：腸胃道保健品、護肝產品、護眼產品、調節血壓血脂產品的組合內容。'
shop_2_2 = '有特殊的分類商品嗎'
shop_2_2_a = '(尚未確認)'
shop_2_3 = '哪可以找到特價中的商品'
shop_2_3_a = '健康購商城的活動專區可看到當前有折價的商品。'

shop_3 = '商品挑選問題'
shop_3_1 = '如何選購商品'
shop_3_1_a = '若您綁定的您的健康檢查資料，系統會更精準的推薦您可以使用的產品。另外也提供簡單的購物服務，幫您把產品組合包裝，讓您購物更簡單輕鬆，不必費時挑選。若是在購物過程中有疑問，還可透過HOA快問快答系統，詢問我們專業的營養師團隊，也會提供給您專業的建議參考。'
shop_3_2 = '我想選購的商品沒貨了'
shop_3_2_a = '點擊上方的次功能列，“我的最愛”裏頭有您設定追蹤所有商品品項，商品到貨會第一時間通知您'
shop_3_3 = '挑好的商品跑到哪裡'
shop_3_3_a = '您挑好的商品都跑到購物車去了，所以你只要點上半部購物車就可以看到您挑選好的商品。'

shop_4 = '付款與發貨問題'
shop_4_1 = '能不能貨到付款'
shop_4_1_a = 'HOA健康網支持超商取貨，目前不提供貨到付款，敬請見諒!'
shop_4_2 = '商品付款有哪些方式'
shop_4_2_a = 'HOA健康購商品付款方式，目前支持歐付寶金流支付、信用卡、信用卡分期付款、ATM轉帳、超商代收等方式，您可以選擇適合您的方式進行付款。'
shop_4_3 = '是否可使用行動支付付費'
shop_4_3_a = 'HOA健康購也支持APPLE pay、LinePay, Samsung Pay, Android Pay等付款方式，您可以多加利用。'

shop_5 = '商品的退貨換貨疑問'
shop_5_1 = '有哪些商品不得退換貨'
shop_5_1_a = '1.易於腐敗、保存期限較短或解約時即將逾期。\n2.依消費者要求所為之客製化給付。\n3.經消費者拆封使用之產品或已拆封之個人衛生用品。\n4.農產品以及生鮮食品。\n依HOA退款與退貨政策進行處理。'
shop_5_2 = '有瑕疵的商品該如何換貨'
shop_5_2_a = 'HOA健康購沒提供換貨服務，若您是因為產品有瑕疵，需要將整組商品退回，客服將會為您重新寄送一組新的產品給您。由於是組合的產品，所以無法進行單一物品的換貨，敬請見諒!'
shop_5_3 = '不滿意的商品該如何退貨'
shop_5_3_a = '退貨時請在訂單/交易紀錄選擇該商品，然後點擊“我要退貨”依操作指示進行即可。我們將於收到退回的商品的7-14個工作天之內，為您完成退款手續。客服會在退款完成時，通知您。'

# 健康顧問
health_service = '健康顧問'
health_1 = '常見慢性疾病'
health_1_1 = '心臟血管相關慢性疾病'
health_1_2 = '泌尿系統相關慢性疾病'
health_1_3 = '消化系統相關慢性疾病'

health_2 = '新生兒照護諮詢'
health_2_1 = '小孩腸胃有異常'
health_2_2 = '小孩皮膚有異常'
health_2_3 = '小孩發燒怎麼辦'

health_3 = '整合多重用藥'
health_3_1 = '什麼是整合多重用藥'
health_3_2 = '要如何整合多重用藥'
health_3_3 = '怎麼看多科整合門診'

health_4 = '居家照護諮詢'
health_4_1 = '我有慢性疾病的親友'
health_4_2 = '我有重大疾病的親友'
health_4_3 = '我有年長的親友'

health_5 = '疫苗注射諮詢'
health_5_1 = '年長者疫苗注射?'
health_5_2 = '成人疫苗注射'
health_5_3 = '兒童疫苗注射'

service_list = [normal_1, normal_2, normal_3, normal_4, normal_5, shop_1, shop_2, shop_3, shop_4, shop_5]


@app.route("/", methods=['GET', 'POST'])
def callback():
    if request.method == 'GET':
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        else:
            return 'Invalid verification token'

    if request.method == 'POST':
        output = request.get_json()
        for event in output['entry']:
            if 'messaging' in event:
                messaging = event['messaging']
                for x in messaging:
                    if x.get('message'):
                        recipient_id = x['sender']['id']
                        if x['message'].get('text'):
                            message = x['message']['text']
                            handle_message(recipient_id,message)
                    else:
                        pass
            elif 'standby' in event:
                standby = event['standby']
                for x in standby:
                    if x.get('postback'):
                        recipient_id = x['sender']['id']
                        if x['postback'].get('title'):
                            message = x['postback']['title']
                            handle_message(recipient_id, message)
                    else:
                        pass
            else:
                pass
        return "Success"

# 開始-圖文表單
def start_generic(recipient_id):
    elements = [
        Element(
            title="請選擇服務",
            image_url="https://i.imgur.com/gAzpgJJ.jpg",
            buttons=[
                {
                    "type": "postback",
                    "title": "一般客服",
                    "payload": "一般客服"
                },
                {
                    "type": "postback",
                    "title": "購物客服",
                    "payload": "購物客服"
                },
                {
                    "type": "postback",
                    "title": "健康顧問",
                    "payload": "健康顧問"
                }
            ]
        ),
        Element(
            title="請選擇服務",
            image_url="https://i.imgur.com/Th3RfHs.jpg",
            buttons=[
                {
                    "type": "postback",
                    "title": "醫療新聞",
                    "payload": "醫療新聞"
                },
                {
                    "type": "postback",
                    "title": '網路購物',
                    "payload": "網路購物"
                }
            ]
        )
    ]
    bot.send_generic_message(recipient_id, elements)
    return 0

# 詢問滿意度
def askSatisfaction(recipient_id):
    text = "請問您滿意這次的服務嗎?"
    buttons = [
        {
            "type": "postback",
            "title": "滿意",
            "payload": "滿意"
        },
        {
            "type": "postback",
            "title": "了解更多",
            "payload": "了解更多"
        }
    ]
    bot.send_button_message(recipient_id, text, buttons)
    return 0

# 蘋果健康新聞爬蟲
def apple_health():
    domain = 'http://www.appledaily.com.tw'
    url = 'http://www.appledaily.com.tw/appledaily/bloglist/headline/30342175'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    article_seq = []
    news_list = soup.select('ul.auallt > li.fillup')
    for news in news_list:
        time = (news.select_one('time').text)
        article = news.select_one('a')
        title = article.text + " " + time
        url = domain + article['href']
        match = re.match(r'(.*)/.*', url)
        url_re = match.group(1)
        article_seq.append({
            'title': title,
            'url': url_re
        })

    content = ''
    article_sample = random.sample(article_seq, 5)
    for index, article in enumerate(article_sample, 0):
        data = '{}\n{}\n\n'.format(article.get('title', None),article.get('url', None))
        content += data
    return content

# yahoo健康新聞爬蟲
def yahoo_health():
    driver = webdriver.PhantomJS('vendor/phantomjs/bin/phantomjs')
    url = 'https://tw.news.yahoo.com/health'
    domain = 'https://tw.news.yahoo.com'
    driver.get(url)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    article_seq = []
    news_list = soup.select("div[class='Cf']")
    for news in news_list:
        title = ''
        subtitle = ''
        news_url = ''
        img_url = ''

        img_0 = news.select("div[class='H(0) Ov(h) Bdrs(2px)']")
        # 為了一致性，只抓取有附圖片的新聞
        if img_0:
            # 文章連結網址
            url_0 = news.select_one("h3[class='Mb(5px)']")
            url_1 = url_0.select_one("a")
            news_url = domain + url_1['href']

            # 副標題
            subtitle_0 = news.select("div[class='C(#959595) Fz(13px) C($c-fuji-grey-f)! D(ib) Mb(6px)']")
            for subtitle_part in subtitle_0:
                subtitle += subtitle_part.text

            # 標題
            for img_1 in img_0:
                img = img_1.select_one('img')
                title = img['alt']
                img_src = img['src']

                # 圖片連結
                if img_src != 'https://s.yimg.com/g/images/spaceball.gif':
                    img_url = img_src
                else:
                    style = img['style']
                    match = re.match(r'background-image:url\((.*)\);', style)
                    img_url = match.group(1)
        # 避免抓到空欄位
        if title != '':
            article_seq.append({
                'title': title,
                'subtitle': subtitle,
                'news_url': news_url,
                'img_url': img_url
            })
    driver.quit()
    article_sample = random.sample(article_seq, 5)
    return article_sample

# 早安健康網爬蟲
def everyday():
    url = 'https://www.everydayhealth.com.tw/latest/1'
    domain = 'https://www.everydayhealth.com.tw'
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    article_seq = []
    article_container = soup.select_one('div[class="latest-articles-container"]')
    article_list = article_container.select_one('div[class="article-list clear"]')
    news_list = article_list.select('div[class="list"]')
    for news in news_list:
        date = news.select_one('span[class="date"]').text
        author = news.select_one('a[class="author"]').text
        subtitle = date + "|" + author
        img = news.select_one('img')
        title = img['alt']
        img_url = img['src']
        news_url = domain + news.select_one('a[class="list-img"]')['href']
        article_seq.append({
            'title': title,
            'subtitle': subtitle,
            'news_url': news_url,
            'img_url': img_url
        })
    article_sample = random.sample(article_seq, 5)
    return article_sample

# 新聞表單
def news_generic(recipient_id, article_sample):
    elements = [
        Element(
            title=article_sample[0].get('title'),
            subtitle=article_sample[0].get('subtitle'),
            image_url=article_sample[0].get('img_url'),
            buttons=[
                {
                    "type": "web_url",
                    "url": article_sample[0].get('news_url'),
                    "title": read_more
                }
            ]
        ),
        Element(
            title=article_sample[1].get('title'),
            subtitle=article_sample[1].get('subtitle'),
            image_url=article_sample[1].get('img_url'),
            buttons=[
                {
                    "type": "web_url",
                    "url": article_sample[1].get('news_url'),
                    "title": read_more
                }
            ]
        ),
        Element(
            title=article_sample[2].get('title'),
            subtitle=article_sample[2].get('subtitle'),
            image_url=article_sample[2].get('img_url'),
            buttons=[
                {
                    "type": "web_url",
                    "url": article_sample[2].get('news_url'),
                    "title": read_more
                }
            ]
        ),
        Element(
            title=article_sample[3].get('title'),
            subtitle=article_sample[3].get('subtitle'),
            image_url=article_sample[3].get('img_url'),
            buttons=[
                {
                    "type": "web_url",
                    "url": article_sample[3].get('news_url'),
                    "title": read_more
                }
            ]
        ),
        Element(
            title=article_sample[4].get('title'),
            subtitle=article_sample[4].get('subtitle'),
            image_url=article_sample[4].get('img_url'),
            buttons=[
                {
                    "type": "web_url",
                    "url": article_sample[4].get('news_url'),
                    "title": read_more
                }
            ]
        )
    ]
    bot.send_generic_message(recipient_id, elements)
    return 0

# 計算維他命每錠的單價
def cp_value(title,price):
    string = ['顆','錠','粒','s','S']
    findall = re.findall(r'((\d*\s*[顆|錠|粒|s|S]*\+)*\s*?\d+\s*)[顆|錠|粒|s|S]',title)
    if findall:
        number_0 = findall[0][0]
        number_1 = number_0
        for s in string:
            number_1 = number_1.replace(s,"")
        number_1 = number_1.split("+")
        number = 0
        for index, num in enumerate(number_1):
            number += int(num)
        findall_m = re.findall(r'[X|x|*|共]\s*(\d+)', title)
        if findall_m:
            number_m = int(findall_m[0])
            total = number * number_m
            return str(round(price/total,1))
        else:
            return str(round(price/number,1))
    else:
        return '?'

# PChome維他命爬蟲,id=商品類別id
def pchome_vitamin(id):
    driver = webdriver.PhantomJS("vendor/phantomjs/bin/phantomjs")
    url = 'http://24h.pchome.com.tw/store/' + id + '?style=2'
    driver.get(url)
    article_seq = []

    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "col3f"))
    )
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    product_list = soup.select('dl[class="col3f"]')
    for product in product_list:
        img_url = 'https:' + product.select_one('img')['src']
        title = product.select_one('h5.nick > a').text
        price_0 = product.select_one('span.price > span.value').text
        if price_0 != '':
            price = int(price_0)
            product_url = 'http:' + product.select_one('a[class="prod_img"]')['href']
            cpvalue = cp_value(title, price)
            if cpvalue != '?':
                cp = '價格: ' + str(price) + '元 '+'(每錠單價: ' + cpvalue + ' 元)'
                article_seq.append({
                    'title': title,
                    'price': price,
                    'img_url': img_url,
                    'product_url': product_url,
                    'cp': cp
                })

    driver.quit()
    article_sample = random.sample(article_seq, 5)
    return article_sample

# Yahoo維他命爬蟲,url=商品類別網址
def yahoo_vitamin(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    article_seq = []
    product_content = soup.select_one('ul[class="Grid Mstart-12 Pt-14"]')
    product_list = product_content.select('li')
    for product in product_list:
        a = product.select_one('a["class=D-tbc Ta-c Va-m js-pid Bgc-w"]')
        product_url = a['href']
        img = a.select_one('img')
        img_url = img['src']
        title = img['title']
        price_0 = product.select_one('div[class="price-sec Mx-12 Mt-4"]')
        price_1 = price_0.select_one('span').text.replace('$','').replace(',','')
        price = int(price_1)
        cpvalue = cp_value(title,price)
        if cpvalue != '?':
            cp = '價格: ' + str(price) + '元 '+'(每錠單價: ' + cpvalue + ' 元)'
            article_seq.append({
                'title': title,
                'price': price,
                'img_url': img_url,
                'product_url': product_url,
                'cp': cp
            })
    article_sample = random.sample(article_seq, 5)
    return article_sample

# 商品表單
def product_generic(recipient_id, article_sample):
    elements = [
        Element(
            title=article_sample[0].get('title'),
            subtitle=article_sample[0].get('cp'),
            image_url=article_sample[0].get('img_url'),
            buttons=[
                {
                    "type": "web_url",
                    "url": article_sample[0].get('product_url'),
                    "title": "購買頁面"
                }
            ]
        ),
        Element(
            title=article_sample[1].get('title'),
            subtitle=article_sample[1].get('cp'),
            image_url=article_sample[1].get('img_url'),
            buttons=[
                {
                    "type": "web_url",
                    "url": article_sample[1].get('product_url'),
                    "title": "購買頁面"
                }
            ]
        ),
        Element(
            title=article_sample[2].get('title'),
            subtitle=article_sample[2].get('cp'),
            image_url=article_sample[2].get('img_url'),
            buttons=[
                {
                    "type": "web_url",
                    "url": article_sample[2].get('product_url'),
                    "title": "購買頁面"
                }
            ]
        ),
        Element(
            title=article_sample[3].get('title'),
            subtitle=article_sample[3].get('cp'),
            image_url=article_sample[3].get('img_url'),
            buttons=[
                {
                    "type": "web_url",
                    "url": article_sample[3].get('product_url'),
                    "title": "購買頁面"
                }
            ]
        ),
        Element(
            title=article_sample[4].get('title'),
            subtitle=article_sample[4].get('cp'),
            image_url=article_sample[4].get('img_url'),
            buttons=[
                {
                    "type": "web_url",
                    "url": article_sample[4].get('product_url'),
                    "title": "購買頁面"
                }
            ]
        )
    ]
    bot.send_generic_message(recipient_id, elements)
    return 0

# 中亞健康網爬蟲
def hoa_crawler(search,token):
    domain = 'http://www.ca2-health.com'
    url = 'http://www.ca2-health.com/FrontEnd/Search?s=' + search
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    article_seq = []
    counter = 0
    for li in soup.select('li["style"="display: block;"]'):
        if counter < 5:
            a = li.select_one('a["class"="article-image"]')
            art_url = domain + a['href']
            img = a.select_one('img')
            img_url = domain + img['src']
            title = img['title']
            subtitle = li.select_one('p["itemprop"="description"]').text.strip()[0:59]
            if subtitle == "":
                subtitle = "內文預覽"

            upload = imgurclient.upload_from_url(img_url, config=None, anon=True)

            article_seq.append(
                {
                    'title': title,
                    'subtitle': subtitle,
                    'art_url': art_url,
                    'img_url': upload['link']
                }
            )
        else:
            break
        counter += 1
    return article_seq

# 中亞健康網表單
def hoa_elements(article_seq):
    elements = []
    for article in article_seq:
        elements.append(
            Element(
                title=article.get('title'),
                subtitle=article.get('subtitle'),
                image_url=article.get('img_url'),
                buttons=[
                    {
                        "type": "web_url",
                        "url": article.get('art_url'),
                        "title": read_more
                    }
                ]
            )
        )
    return elements


def handle_message(recipient_id,message):
    print("recipient_id", recipient_id)
    print("message", message)

    # normal
    if message == normal_service:
        elements = [
            Element(
                title=normal_1,
                image_url=normal_1_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": normal_1_1,
                        "payload": normal_1_1
                    },
                    {
                        "type": "postback",
                        "title": normal_1_2,
                        "payload": normal_1_2
                    },
                    {
                        "type": "postback",
                        "title": normal_1_3,
                        "payload": normal_1_3
                    }
                ]
            ),
            Element(
                title=normal_2,
                image_url=normal_2_p,
                buttons=[
                    {
                        "type": "postback",
                        "title": normal_2_1,
                        "payload": normal_2_1
                    },
                    {
                        "type": "postback",
                        "title": normal_2_2,
                        "payload": normal_2_2
                    },
                    {
                        "type": "postback",
                        "title": normal_2_3,
                        "payload": normal_2_3
                    }
                ]
            ),
            Element(
                title=normal_3,
                image_url=normal_3_p,
                buttons=[
                    {
                        "type": "postback",
                        "title": normal_3_1,
                        "payload": normal_3_1
                    },
                    {
                        "type": "postback",
                        "title": normal_3_2,
                        "payload": normal_3_2
                    },
                    {
                        "type": "postback",
                        "title": normal_3_3,
                        "payload": normal_3_3
                    }
                ]
            ),
            Element(
                title=normal_4,
                image_url=normal_4_p,
                buttons=[
                    {
                        "type": "postback",
                        "title": normal_4_1,
                        "payload": normal_4_1
                    },
                    {
                        "type": "postback",
                        "title": normal_4_2,
                        "payload": normal_4_2
                    },
                    {
                        "type": "postback",
                        "title": normal_4_3,
                        "payload": normal_4_3
                    }
                ]
            ),
            Element(
                title=normal_5,
                image_url=normal_5_p,
                buttons=[
                    {
                        "type": "postback",
                        "title": normal_5_1,
                        "payload": normal_5_1
                    },
                    {
                        "type": "postback",
                        "title": normal_5_2,
                        "payload": normal_5_2
                    },
                    {
                        "type": "postback",
                        "title": normal_5_3,
                        "payload": normal_5_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0
    if message == normal_1_1:
        text = normal_1_1_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_1_2:
        text = normal_1_2_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_1_3:
        text = normal_1_3_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_2_1:
        text = normal_2_1_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_2_2:
        text = normal_2_2_1
        buttons = [
            {
                "type": "postback",
                "title": normal_2_2_1_1,
                "payload": normal_2_2_1_1
            },
            {
                "type": "postback",
                "title": normal_2_2_1_2,
                "payload": normal_2_2_1_2
            }
        ]
        bot.send_button_message(recipient_id, text, buttons)
        return 0
    if message == normal_2_2_1_1:
        text = normal_2_2_1_1_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_2_2_1_2:
        text = normal_2_2_1_2_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_2_3:
        text = normal_2_3_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_3_1:
        text = normal_3_1_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_3_2:
        text = normal_3_2_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_3_3:
        text = normal_3_3_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_4_1:
        text = normal_4_1_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_4_2:
        text = normal_4_2_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_4_3:
        text = normal_4_3_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_5_1:
        text = normal_5_1_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_5_2:
        text = normal_5_2_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == normal_5_3:
        text = normal_5_3_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0

    # normal 對於 api.ai 回傳使用的表單
    if message == normal_1:
        elements = [
            Element(
                title=normal_1,
                image_url=normal_1_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": normal_1_1,
                        "payload": normal_1_1
                    },
                    {
                        "type": "postback",
                        "title": normal_1_2,
                        "payload": normal_1_2
                    },
                    {
                        "type": "postback",
                        "title": normal_1_3,
                        "payload": normal_1_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0
    if message == normal_2:
        elements = [
            Element(
                title=normal_2,
                image_url=normal_2_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": normal_2_1,
                        "payload": normal_2_1
                    },
                    {
                        "type": "postback",
                        "title": normal_2_2,
                        "payload": normal_2_2
                    },
                    {
                        "type": "postback",
                        "title": normal_2_3,
                        "payload": normal_2_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0
    if message == normal_3:
        elements = [
            Element(
                title=normal_3,
                image_url=normal_3_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": normal_3_1,
                        "payload": normal_3_1
                    },
                    {
                        "type": "postback",
                        "title": normal_3_2,
                        "payload": normal_3_2
                    },
                    {
                        "type": "postback",
                        "title": normal_3_3,
                        "payload": normal_3_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0
    if message == normal_4:
        elements = [
            Element(
                title=normal_4,
                image_url=normal_4_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": normal_4_1,
                        "payload": normal_4_1
                    },
                    {
                        "type": "postback",
                        "title": normal_4_2,
                        "payload": normal_4_2
                    },
                    {
                        "type": "postback",
                        "title": normal_4_3,
                        "payload": normal_4_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0
    if message == normal_5:
        elements = [
            Element(
                title=normal_5,
                image_url=normal_5_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": normal_5_1,
                        "payload": normal_5_1
                    },
                    {
                        "type": "postback",
                        "title": normal_5_2,
                        "payload": normal_5_2
                    },
                    {
                        "type": "postback",
                        "title": normal_5_3,
                        "payload": normal_5_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0

    # shop
    if message == shop_service:
        elements = [
            Element(
                title=shop_1,
                image_url=shop_1_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": shop_1_1,
                        "payload": shop_1_1
                    },
                    {
                        "type": "postback",
                        "title": shop_1_2,
                        "payload": shop_1_2
                    },
                    {
                        "type": "postback",
                        "title": shop_1_3,
                        "payload": shop_1_3
                    }
                ]
            ),
            Element(
                title=shop_2,
                image_url=shop_2_p,
                buttons=[
                    {
                        "type": "postback",
                        "title": shop_2_1,
                        "payload": shop_2_1
                    },
                    {
                        "type": "postback",
                        "title": shop_2_2,
                        "payload": shop_2_2
                    },
                    {
                        "type": "postback",
                        "title": shop_2_3,
                        "payload": shop_2_3
                    }
                ]
            ),
            Element(
                title=shop_3,
                image_url=shop_3_p,
                buttons=[
                    {
                        "type": "postback",
                        "title": shop_3_1,
                        "payload": shop_3_1
                    },
                    {
                        "type": "postback",
                        "title": shop_3_2,
                        "payload": shop_3_2
                    },
                    {
                        "type": "postback",
                        "title": shop_3_3,
                        "payload": shop_3_3
                    }
                ]
            ),
            Element(
                title=shop_4,
                image_url=shop_4_p,
                buttons=[
                    {
                        "type": "postback",
                        "title": shop_4_1,
                        "payload": shop_4_1
                    },
                    {
                        "type": "postback",
                        "title": shop_4_2,
                        "payload": shop_4_2
                    },
                    {
                        "type": "postback",
                        "title": shop_4_3,
                        "payload": shop_4_3
                    }
                ]
            ),
            Element(
                title=shop_5,
                image_url=shop_5_p,
                buttons=[
                    {
                        "type": "postback",
                        "title": shop_5_1,
                        "payload": shop_5_1
                    },
                    {
                        "type": "postback",
                        "title": shop_5_2,
                        "payload": shop_5_2
                    },
                    {
                        "type": "postback",
                        "title": shop_5_3,
                        "payload": shop_5_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0
    if message == shop_1_1:
        text = shop_1_1_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_1_2:
        text = shop_1_2_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_1_3:
        text = shop_1_3_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_2_1:
        text = shop_2_1_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_2_2:
        text = shop_2_2_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_2_3:
        text = shop_2_3_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_3_1:
        text = shop_3_1_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_3_2:
        text = shop_3_2_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_3_3:
        text = shop_3_3_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_4_1:
        text = shop_4_1_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_4_2:
        text = shop_4_2_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_4_3:
        text = shop_4_3_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_5_1:
        text = shop_5_1_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_5_2:
        text = shop_5_2_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0
    if message == shop_5_3:
        text = shop_5_3_a
        bot.send_text_message(recipient_id, text)
        askSatisfaction(recipient_id)
        return 0

    # shop 對於 api.ai 回傳使用的表單
    if message == shop_1:
        elements = [
            Element(
                title=shop_1,
                image_url=shop_1_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": shop_1_1,
                        "payload": shop_1_1
                    },
                    {
                        "type": "postback",
                        "title": shop_1_2,
                        "payload": shop_1_2
                    },
                    {
                        "type": "postback",
                        "title": shop_1_3,
                        "payload": shop_1_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0
    if message == shop_2:
        elements = [
            Element(
                title=shop_2,
                image_url=shop_2_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": shop_2_1,
                        "payload": shop_2_1
                    },
                    {
                        "type": "postback",
                        "title": shop_2_2,
                        "payload": shop_2_2
                    },
                    {
                        "type": "postback",
                        "title": shop_2_3,
                        "payload": shop_2_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0
    if message == shop_3:
        elements = [
            Element(
                title=shop_3,
                image_url=shop_3_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": shop_3_1,
                        "payload": shop_3_1
                    },
                    {
                        "type": "postback",
                        "title": shop_3_2,
                        "payload": shop_3_2
                    },
                    {
                        "type": "postback",
                        "title": shop_3_3,
                        "payload": shop_3_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0
    if message == shop_4:
        elements = [
            Element(
                title=shop_4,
                image_url=shop_4_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": shop_4_1,
                        "payload": shop_4_1
                    },
                    {
                        "type": "postback",
                        "title": shop_4_2,
                        "payload": shop_4_2
                    },
                    {
                        "type": "postback",
                        "title": shop_4_3,
                        "payload": shop_4_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0
    if message == shop_5:
        elements = [
            Element(
                title=shop_5,
                image_url=shop_5_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": shop_5_1,
                        "payload": shop_5_1
                    },
                    {
                        "type": "postback",
                        "title": shop_5_2,
                        "payload": shop_5_2
                    },
                    {
                        "type": "postback",
                        "title": shop_5_3,
                        "payload": shop_5_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0


    # health
    if message == health_service:
        elements = [
            Element(
                title=health_1,
                image_url=health_1_p,
                buttons = [
                    {
                        "type": "postback",
                        "title": health_1_1,
                        "payload": health_1_1
                    },
                    {
                        "type": "postback",
                        "title": health_1_2,
                        "payload": health_1_2
                    },
                    {
                        "type": "postback",
                        "title": health_1_3,
                        "payload": health_1_3
                    }
                ]
            ),
            Element(
                title=health_2,
                image_url=health_2_p,
                buttons=[
                    {
                        "type": "postback",
                        "title": health_2_1,
                        "payload": health_2_1
                    },
                    {
                        "type": "postback",
                        "title": health_2_2,
                        "payload": health_2_2
                    },
                    {
                        "type": "postback",
                        "title": health_2_3,
                        "payload": health_2_3
                    }
                ]
            ),
            Element(
                title=health_3,
                image_url=health_3_p,
                buttons=[
                    {
                        "type": "postback",
                        "title": health_3_1,
                        "payload": health_3_1
                    },
                    {
                        "type": "postback",
                        "title": health_3_2,
                        "payload": health_3_2
                    },
                    {
                        "type": "postback",
                        "title": health_3_3,
                        "payload": health_3_3
                    }
                ]
            ),
            Element(
                title=health_4,
                image_url=health_4_p,
                buttons=[
                    {
                        "type": "postback",
                        "title": health_4_1,
                        "payload": health_4_1
                    },
                    {
                        "type": "postback",
                        "title": health_4_2,
                        "payload": health_4_2
                    },
                    {
                        "type": "postback",
                        "title": health_4_3,
                        "payload": health_4_3
                    }
                ]
            ),
            Element(
                title=health_5,
                image_url=health_5_p,
                buttons=[
                    {
                        "type": "postback",
                        "title": health_5_1,
                        "payload": health_5_1
                    },
                    {
                        "type": "postback",
                        "title": health_5_2,
                        "payload": health_5_2
                    },
                    {
                        "type": "postback",
                        "title": health_5_3,
                        "payload": health_5_3
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0

    # news
    if message == "醫療新聞":
        elements = [
            Element(
                title=please_choose,
                image_url="https://i.imgur.com/DRi5b6e.png",
                buttons = [
                    {
                        "type": "postback",
                        "title": "蘋果日報",
                        "payload": "蘋果日報"
                    },
                    {
                        "type": "postback",
                        "title": "奇摩新聞",
                        "payload": "奇摩新聞"
                    },
                    {
                        "type": "postback",
                        "title": "早安健康網",
                        "payload": "早安健康網"
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0

    # news-1
    if message == "蘋果日報":
        text = apple_health()
        bot.send_text_message(recipient_id, text)
        return 0

    # news-2
    if message == "奇摩新聞":
        article_sample = yahoo_health()
        news_generic(recipient_id, article_sample)
        return 0

    # news-3
    if message == "早安健康網":
        article_sample = everyday()
        news_generic(recipient_id, article_sample)
        return 0

    # shop
    if message == "網路購物":
        elements = [
            Element(
                title=please_choose,
                image_url="https://i.imgur.com/1EvMGA2.png",
                buttons = [
                    {
                        "type": "postback",
                        "title": "PChome購物",
                        "payload": "PChome購物"
                    },
                    {
                        "type": "postback",
                        "title": "Yahoo購物",
                        "payload": "Yahoo購物"
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0

    # shop-1
    if message == "PChome購物":
        elements = [
            Element(
                title=please_choose,
                image_url="https://i.imgur.com/WfELUs7.jpg",
                buttons = [
                    {
                        "type": "postback",
                        "title": "PChome維他命",
                        "payload": "PChome維他命"
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0

    # shop-1-1
    if message == "PChome維他命":
        elements = [
            Element(
                title=please_choose,
                image_url="https://i.imgur.com/gHit3GF.jpg",
                buttons = [
                    {
                        "type": "postback",
                        "title": "PChome維他命B",
                        "payload": "PChome維他命B"
                    },
                    {
                        "type": "postback",
                        "title": "PChome維他命C",
                        "payload": "PChome維他命C"
                    },
                    {
                        "type": "postback",
                        "title": "PChome維他命D",
                        "payload": "PChome維他命D"
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0

    # shop-1-1-1
    if message == "PChome維他命B":
        id = 'DBBC02'
        article_sample = pchome_vitamin(id)
        product_generic(recipient_id, article_sample)
        return 0

    # shop-1-1-2
    if message == "PChome維他命C":
        id = 'DBBC03'
        article_sample = pchome_vitamin(id)
        product_generic(recipient_id, article_sample)
        return 0

    # shop-1-1-3
    if message == "PChome維他命D":
        id = 'DBBC04'
        article_sample = pchome_vitamin(id)
        product_generic(recipient_id, article_sample)
        return 0

    # shop-2
    if message == "Yahoo購物":
        elements = [
            Element(
                title=please_choose,
                image_url="https://i.imgur.com/DsGp0w6.png",
                buttons = [
                    {
                        "type": "postback",
                        "title": "Yahoo維他命",
                        "payload": "Yahoo維他命"
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0

    # shop-2-1
    if message == "Yahoo維他命":
        elements = [
            Element(
                title=please_choose,
                image_url="https://i.imgur.com/gHit3GF.jpg",
                buttons = [
                    {
                        "type": "postback",
                        "title": "Yahoo維他命B",
                        "payload": "Yahoo維他命B"
                    },
                    {
                        "type": "postback",
                        "title": "Yahoo維他命C",
                        "payload": "Yahoo維他命C"
                    },
                    {
                        "type": "postback",
                        "title": "Yahoo綜合維他命",
                        "payload": "Yahoo綜合維他命"
                    }
                ]
            )
        ]
        bot.send_generic_message(recipient_id, elements)
        return 0
    # shop-2-1-1
    if message == "Yahoo維他命B":
        url = 'https://tw.mall.yahoo.com/%E7%B6%AD%E4%BB%96%E5%91%BDB-%E7%B6%AD%E4%BB%96%E5%91%BD-152982525-category.html?.r=1924284948'
        article_sample = yahoo_vitamin(url)
        product_generic(recipient_id, article_sample)
        return 0

    # shop-2-1-2
    if message == "Yahoo維他命C":
        url = 'https://tw.mall.yahoo.com/%E7%B6%AD%E4%BB%96%E5%91%BDC-%E7%B6%AD%E4%BB%96%E5%91%BD-152982521-category.html?.r=1805688191'
        article_sample = yahoo_vitamin(url)
        product_generic(recipient_id, article_sample)
        return 0

    # shop-2-1-3
    if message == "Yahoo綜合維他命":
        url = 'https://tw.mall.yahoo.com/%E7%B6%9C%E5%90%88%E7%B6%AD%E4%BB%96%E5%91%BD-%E7%B6%AD%E4%BB%96%E5%91%BD-152983856-category.html?.r=1109170753'
        article_sample = yahoo_vitamin(url)
        product_generic(recipient_id, article_sample)
        return 0

    # satisfaction_True
    if message == "滿意":
        text = "感謝您的使用"
        bot.send_text_message(recipient_id, text)
        return 0

    # satisfaction_False
    if message == "了解更多":
        text = "點擊連結撥打 Skype 線上客服"
        buttons = [
            {
                "type":"web_url",
                "url":skype_url,
                "title":"Skype 線上客服",
                "webview_height_ratio": "compact"
            }
        ]
        bot.send_button_message(recipient_id,text,buttons)
        return 0

    if message == "開始使用":
        start_generic(recipient_id)
        return 0

    if message == "Get Started":
        start_generic(recipient_id)
        return 0

    # 連結 Api.ai
    ai_request = ai.text_request()
    ai_request.session_id = recipient_id
    ai_request.query = message
    response = ai_request.getresponse()
    reply = json.loads(response.read())
    ai_text = reply['result']['fulfillment']['speech']
    # 如果可辨識為預定表單
    if ai_text in service_list:
        handle_message(recipient_id, ai_text)
        return 0

    # 斷詞
    cut = jieba.cut(message)
    cut_list = []
    for cu in cut:
        # 停用詞過濾
        if cu not in stop_list:
            cut_list.append(cu)
    if cut_list != []:
        for word in cut_list:
            print(word)
            # 搜尋中亞健康網的文章
            article_seq = hoa_crawler(word, recipient_id)
            if len(article_seq) > 0:
                elements = hoa_elements(article_seq)
                bot.send_generic_message(recipient_id, elements)
                return 0
            elif word == cut_list[-1]:
                bot.send_text_message(recipient_id, ai_text)
                return 0
    else:
        bot.send_text_message(recipient_id, ai_text)
        return 0

if __name__ == "__main__":
    app.run(port=5002, debug=True)