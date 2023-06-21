from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ChromeOptions
from selenium.webdriver.common.keys import Keys
import time
import smtplib
from email.message import EmailMessage
import chromedriver_autoinstaller



URL = "https://prohardver.hu/tema/bestbuy_topik_akcio_ajanlasakor_akcio_hashtag_kote/friss.html"


user_username = 'XXX'
user_password = 'YYY'

my_email = "ASD"
email_password = "ZZZ"

chromedriver_autoinstaller.install()
driver = webdriver.Chrome()

# chrome_driver_path = "/chromedriver_win32/chromedriver.exe"
# service = Service(chrome_driver_path)
# options = ChromeOptions()
# options.add_experimental_option("detach", True)
# driver = webdriver.Chrome(service=service, options=options)


def init(url):
    driver.get(url)

#    closing popups
    cookie_close_button = driver.find_element(By.CSS_SELECTOR, "#cookie-accept > button")
    cookie_close_button.click()
    ASZF_close_button = driver.find_element(By.CSS_SELECTOR, "#rules-accept > button")
    ASZF_close_button.click()

#    login
    username = driver.find_element(By.NAME, "email")
    username.send_keys(user_username)
    password = driver.find_element(By.NAME, "pass")
    password.send_keys(user_password)
    password.send_keys(Keys.ENTER)


def load_prev_sent_msg():
    with open("data.txt") as file:
        already_sent = file.readlines()
    already_sent_stripped = [sent.strip() for sent in already_sent]
    return already_sent_stripped


def save_sent_msg(bestbuy_dict):
    with open("data.txt", "a") as file:
        for i in bestbuy_dict:
            file.write(f"{bestbuy_dict[i]['number'][1:]}\n")


def save_links(msg):
    link_list = []
    for i in range(len(msg)):
        if not msg[i].find_elements(By.CSS_SELECTOR, "p > a"):
            link_list.append("no link in the msg")
        else:
            msg_links = msg[i].find_elements(By.CSS_SELECTOR, "p > a")
            if len(msg_links) == 1:
                link_list.append(msg_links[0].get_attribute('href'))
            else:
                multiple_msg_links = []
                for link in msg_links:
                    multiple_msg_links.append(link.get_attribute('href'))
                link_list.append(multiple_msg_links)
    return link_list


def create_dict(msg, number, msg_time, links, page_number, prev_sent_msg):
    already_sent_stripped = prev_sent_msg
    link_list = links

    bestbuy = {}
    for i in range(len(msg)):
        if number[i].text[1:7:] in already_sent_stripped:
            print(f"{number[i].text} msg already sent!")
        else:
            if link_list[i] != "no link in the msg":
                bestbuy[number[i].text] = {
                    "page number": page_number.text,
                    "number": number[i].text,
                    "time": msg_time[i].text,
                    "msg": msg[i].text,
                    "link": link_list[i]
                }
            else:
                pass
    return bestbuy


def send_email(my_email, email_password, bestbuy_dict):
    email_msg = ""
    if not bestbuy_dict:
        email_msg += "Nincs új hozzászólás a legutolsó email óta!"
    else:
        for i in bestbuy_dict:
            email_msg += f'-----------------------------------------------------------------------------------------' \
                         f'-------------------------------------------------------\n' \
                         f'Hozzászólás sorszám: {bestbuy_dict[i]["number"]}    idő: {bestbuy_dict[i]["time"]}\n\n' \
                         f'Üzenet:\n{bestbuy_dict[i]["msg"]}\n\nLink:\n{bestbuy_dict[i]["link"]}\n' \
                         f'------------------------------------------------------------------------------------------' \
                         f'------------------------------------------------------\n\n\n\n'

    print(email_msg)

    msg_to_send = EmailMessage()
    msg_to_send.set_content(email_msg)
    msg_to_send['Subject'] = f"PH best buy"
    msg_to_send['From'] = my_email
    msg_to_send['To'] = my_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as connection:
        connection.login(user=my_email, password=email_password)
        connection.send_message(msg_to_send)




# main program

init(URL)
prev_sent_msg = load_prev_sent_msg()

links = []
bestbuy_dict = {}
for i in range(3):
    time.sleep(3)
    page_number = driver.find_element(By.CSS_SELECTOR, "#center > div:nth-child(1) > ul.nav.navbar-nav.mr-md-auto > li.dropdown.nav-pager > a")
    number = driver.find_elements(By.CSS_SELECTOR, "#center > div:nth-child(3) > ul > li div > div.card-header > div.msg-head-user > span.msg-head-author > span.msg-num > a")
    msg = driver.find_elements(By.CSS_SELECTOR, "#center > div:nth-child(3) > ul > li div > div.card-body > div.media-body > div.msg-content")
    msg_time = driver.find_elements(By.CSS_SELECTOR, "#center > div:nth-child(3) > ul > li div > div.card-header > div.msg-head-options.ml-auto > span.msg-desc > span.msg-time > time")

    print(page_number.text)
    links.extend(save_links(msg))
    bestbuy_dict.update(create_dict(msg, number, msg_time, links, page_number, prev_sent_msg))

    URL_2 = f"https://prohardver.hu/tema/bestbuy_topik_akcio_ajanlasakor_akcio_hashtag_kote/hsz_{int(page_number.text[0:6:]) - 50}-{int(page_number.text[0:6:]) - 1}.html"
    driver.get(URL_2)

save_sent_msg(bestbuy_dict)
send_email(my_email, email_password, bestbuy_dict)
