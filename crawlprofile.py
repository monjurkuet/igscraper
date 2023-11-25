import random
import undetected_chromedriver as uc
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
import json
import mysql.connector
from tqdm import tqdm

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
    username=response_body['data']['user']['username']
    userdetails=response_body['data']['user']
    sql_insert_with_param = """REPLACE userdetails
                        (username,userdetails) 
                        VALUES (%s, %s);"""
    data_tuple = (username,json.dumps(userdetails))
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

with open("profiletocrawl.json", "r") as fp:
    b = json.load(fp)

for username in tqdm(b):
    driver.get(f'https://www.instagram.com/{username.split("@")[1]}')
    time.sleep(random.uniform(15,30))
    try:
        if 'Sorry, this page ' in driver.page_source:
                sql_insert_with_param = """REPLACE userdetails
                                    (username,userdetails) 
                                    VALUES (%s, %s);"""
                data_tuple = (username.split('@')[1],json.dumps({'Data status':'data_unavailable'}))
                cursor.execute(sql_insert_with_param, data_tuple)
                conn.commit()
                print(data_tuple)
        else:
            logs=clean_logs('https://www.instagram.com/api/v1/users/web_profile_info')
            response_body=extract_json_from_log(logs,driver)
            insert_userdata(response_body)
    except Exception as e:
        print(e)

conn.close()

logs=clean_logs('https://www.instagram.com/api/v1/feed/user/')
response_body=extract_json_from_log(logs,driver)
insert_posts(pk_id,response_body)