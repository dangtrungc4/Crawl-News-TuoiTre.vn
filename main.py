from bs4 import BeautifulSoup
from PIL import Image, ImageDraw, ImageFont
import requests
from time import sleep
from selenium import webdriver
import json

SAVE_PATH = 'data.json'
browser = webdriver.Chrome(executable_path="chromedriver.exe")

def write_data(data):
    with open(SAVE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def crawNewsData(baseUrl, url):
    browser.get(url)
    sleep(5)
    see_more_link = browser.find_element_by_xpath("/html/body/div[1]/div/section/div/div[3]/div/div[1]/div/div/div/a")
    see_more_link.click()
    sleep(5)
    see_more_link.click()
    sleep(5)
    soup = BeautifulSoup(browser.page_source, "html.parser")
    titles = soup.findAll('h3', class_='title-news')
    links = [link.find('a').attrs["href"] for link in titles]
    data = []
    for link in links:
        news = requests.get(baseUrl + link)
        soup = BeautifulSoup(news.content, "html.parser")
        title = soup.find("h1", class_="article-title").text
        abstract = soup.find("h2", class_="sapo").text
        body = soup.find("div", id="main-detail-body")
        content = ""
        try:
            for detail in body.findChildren("p", recursive=False):
                content += detail.text
        except:
            content = ""
        images = body.find("img").attrs["src"]
        data.append({
            "title": title,
            "url": baseUrl + link,
            "abstract": abstract,
            "content": content,
            "images": images,
        })
    write_data(data)
    return data

def writeToImage(image, text, position, font, color, maxLine):
    charPerLine = 650 // font.getsize('x')[0]
    pen = ImageDraw.Draw(image)
    yStart = position[1]
    xStart = position[0]
    point = 0
    prePoint = 0
    while point < len(text):
        prePoint = point
        point += charPerLine
        while point < len(text) and text[point] != " ":
            point -= 1
        pen.text((xStart, yStart), text[prePoint:point], font=font, fill=color)
        yStart += font.getsize('hg')[1]
        maxLine -= 1
        if (maxLine == 0):
            if (point < len(text)):
                pen.text((xStart, yStart), "...", font=font, fill="black")
            break


def makeFastNews(data):
    for index, item in enumerate(data):
        # make new image and tool to draw
        image = Image.new('RGB', (650, 750), color="white")
        pen = ImageDraw.Draw(image)
        # load image from internet => resize => paste to main image
        pen.rectangle(((0, 0), (650, 300)), fill="grey")
        newsImage = Image.open(requests.get(item["images"], stream=True).raw)
        newsImage.thumbnail((650, 300), Image.ANTIALIAS)
        image.paste(newsImage, (650 // 2 - newsImage.width // 2, 300 // 2 - newsImage.height//2))
        # write title
        titleFont = ImageFont.truetype("font/arial.ttf", 22)
        writeToImage(image, item["title"], (10, 310), titleFont, "black", 3)
        abstractFont = ImageFont.truetype("font/arial.ttf", 15)
        writeToImage(image, item["abstract"], (10, 390), abstractFont, "gray", 4)
        contentFont = ImageFont.truetype("font/arial.ttf", 20)
        writeToImage(image, item["content"], (10, 460), contentFont, "black", 11)
        name = "image-" + str(index) + ".png"
        image.save("images/" + name)

if __name__ == "__main__":
    makeFastNews(crawNewsData("https://tuoitre.vn", "https://tuoitre.vn/tin-moi-nhat.htm"))
    browser.close()