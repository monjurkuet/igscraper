import random
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json
from tqdm import tqdm
import mysql.connector

conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='root',
        database='instagram',
        port=3306
        )
cursor = conn.cursor()

def waitfor(xpth, driver):
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, xpth)))
    except:
        pass

def insert_userdata(response_body):
    pk_id=response_body['user']['pk_id']
    full_name=response_body['user']['full_name']
    is_verified=response_body['user']['is_verified']
    is_private=response_body['user']['is_private']
    username=response_body['user']['username']
    sql_insert_with_param = """REPLACE userdata
                        (pk_id,full_name,is_verified,is_private,username) 
                        VALUES (%s, %s, %s, %s, %s);"""
    data_tuple = (pk_id,full_name,is_verified,is_private,username)
    cursor.execute(sql_insert_with_param, data_tuple)
    conn.commit()
    print(data_tuple)

def insert_posts(pk_id,response_body):
    items=response_body['items']
    for item in items:
        code=item['code']
        sql_insert_with_param = """INSERT IGNORE postdata
                            (pk_id,postdata,code) 
                            VALUES (%s, %s, %s);"""
        data_tuple = (pk_id,json.dumps(item),code)
        cursor.execute(sql_insert_with_param, data_tuple)
        conn.commit()
        print(data_tuple)

def clean_logs(target_url):
    logs = driver.get_log("performance")  
    logs = [json.loads(lr["message"])["message"] for lr in logs]
    cleaned_log=None
    for log in logs:
        try:
            resp_url = log["params"]["response"]["url"]
            if target_url in resp_url:
                cleaned_log=log
                return cleaned_log
        except:
            pass   
    return cleaned_log

def extract_json_from_log(log,driver):
    request_id = log["params"]["requestId"]
    response_body=driver.execute_cdp_cmd("Network.getResponseBody", {"requestId": request_id})
    response_json=json.loads(response_body['body'])
    return response_json

options = uc.ChromeOptions()
options.user_data_dir = "D://temp//chromeprofile1"
caps = options.to_capabilities()
caps['goog:loggingPrefs'] = {'performance': 'ALL'} 
driver = uc.Chrome(options = options,desired_capabilities=caps) 

driver.get('https://www.instagram.com/larajadephotography/')

logs=clean_logs('https://www.instagram.com/api/v1/feed/user/')
response_body=extract_json_from_log(logs,driver)
pk_id=response_body['user']['pk_id']
insert_userdata(response_body)
insert_posts(pk_id,response_body)
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.uniform(15,30))
    logs=clean_logs('https://www.instagram.com/api/v1/feed/user/')
    response_body=extract_json_from_log(logs,driver)
    insert_posts(pk_id,response_body)

conn.close()

if __name__ == "__main__":
    INSTANCES = 2
    queue_rows = getqueue()   # get list of unprocessed data from queue
    tqdm(ThreadPool(INSTANCES).map(scroll_gmaps_extract_data, queue_rows), total=len(queue_rows))