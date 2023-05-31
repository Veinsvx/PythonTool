
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import spacy
import socket
import threading
import json
from selenium import webdriver
        

def translate_youdao(en_text):
    service = EdgeService(r'C:\edgedriver_win64\msedgedriver.exe')
    options = webdriver.EdgeOptions()
    options.add_argument('--headless')  # 静默运行，不弹出浏览器窗口
    options.add_argument('--disable-extensions')  # 禁用扩展
    url=u'https://fanyi.youdao.com/'
    driver = webdriver.Edge(service=service, options=options)
    driver.get(url)
    # 尝试关闭广告
    try:
        close_ad_btn = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, 'img.close'))
        )
        close_ad_btn.click()
    except TimeoutException:
        print("未找到广告关闭按钮，可能已自动关闭")

    # 模拟点击屏幕任意位置
    action = ActionChains(driver)
    action.move_by_offset(50, 50).click().perform()
    action.move_by_offset(-50, -50).perform()

    # 等待一段时间，确保页面加载完成
    time.sleep(2)

    input_element = WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.ID, 'js_fanyi_input'))
    )

    input_element.send_keys(en_text)

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, 'js_fanyi_output_resultOutput')))

    translated_text = driver.find_element(By.ID, 'js_fanyi_output_resultOutput').text

    print(f"Translated text: {translated_text}")

    # 点击清空按钮
    clear_btn = driver.find_element(By.CSS_SELECTOR, 'a.clearBtn')
    action = ActionChains(driver)
    action.move_to_element(clear_btn).click().perform()
    driver.quit()
    return translated_text




#def translate_youdao(en_text):
#    msg_encoded = urllib.parse.quote(en_text)
#    #url=u'https://v.api.aa1.cn/api/api-fanyi-yd/index.php?msg="{}"&type={}'.format(msg_encoded,ty)
#    url=u'''https://zj.v.api.aa1.cn/api/txjun/?sourceText={}&source=auto&target=zh'''.format(msg_encoded)
#    response = requests.get(url)
#    res = json.loads(response.text)
#    text = res['targetText']
#    print(text)
#    return text



def tag_verbs_or_adverbs(text):
    nlp = spacy.load("en_core_web_trf")
    doc = nlp(text)

    tagged_text = ""
    for token in doc:
        #print(f"{token.text:<15} {token.dep_:<10} {token.head.text:<15}")
        if (token.dep_ == "ROOT" or token.dep_ == "auxpass"or token.dep_ == "relcl"or token.dep_ == "xcomp"or token.dep_ == "acl"or token.dep_ == "aux"or token.dep_ == "cop")and (token.text!="to")or((token.dep_ =="pcomp"or token.dep_ =="pobj"or token.dep_ =="conj"or token.dep_ == "ccomp")and (token.pos_=="VERB"or token.pos_=="AUX")or(token.text!="in" and token.dep_ == "advcl")):
            tagged_text += f'<font color="red">{token.text}</font> '
        else:
            tagged_text += f"{token.text} "

    return tagged_text.strip()


def handle_client(client_socket, client_address):
    print(f"已连接到客户端 {client_address}")

    data = client_socket.recv(10240)


    #print(f"收到来自 {client_address} 的数据: {data.decode('utf-8')}")
    #print(f"收到来自 {client_address} 的数据")
    # 发送数据
    temp1=tag_verbs_or_adverbs(data.decode('utf-8'))
    temp2=translate_youdao(data.decode('utf-8'))
    result={
        'CX':u'''''',
        'FY':u'''''',
    }
    result["CX"]=temp1
    result["FY"]=temp2
    result.update()
    data_str = json.dumps(result)
    #print(result)
    client_socket.sendall(data_str.encode('utf-8'))
        
    # 关闭连接
    print(f"客户端 {client_address} 断开连接")
    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ('localhost', 12345)
    server_socket.bind(server_address)
    server_socket.listen(16)  # 允许的最大连接数

    print("服务器已启动，等待连接...")

    while True:
        # 接受客户端连接
        client_socket, client_address = server_socket.accept()

        # 为每个客户端创建一个新线程
        client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
        client_thread.start()

if __name__ == "__main__":
    main()







## 修改请求头
#headers = {
#    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

## 获取网页内容
#url = 'https://breakingnewsenglish.com/easy-english-news.html'
#response = requests.get(url, headers=headers)
#html = response.content

## 解析HTML代码
#soup = BeautifulSoup(html, 'html.parser')
#list_items = soup.select('.list-class li')[:5]  # 获取前五个li元素

## 提取超链接和标题，并获取链接内容
#for item in list_items:
#    link = item.find('a').get('href')
#    title = item.find('a').get('title')
#    print(f"Link: {link}, Title: {title}")
#    # 获取链接内容
#    link_response = requests.get('https://breakingnewsenglish.com/'+link, headers=headers)
#    link_html = link_response.content
#    link_soup = BeautifulSoup(link_html, 'html.parser')
#    article = link_soup.find('article')  # 获取<article>标签
#    content = article.text.strip()  # 获取<article>标签下的内容
#    print(content)
#    print("____________________________________________________________________")
