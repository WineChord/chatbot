# geneRes.py
"""
用来生成自动回复，总共分为三个步骤：
1.查找消息中是否出现“传感器”字段，假如出现，则读取的数据库为"sensor"（传感器模式告警信息），否则默认读取数据库为"faulty_part"（故障部件模式告警信息）
2.根据正则表达式匹配消息中的五种字段，用flags来记录这个五个字段出现与否
3.运用LSI模型与数据库中的"phenomenon"（现象）字段进行相似度匹配（模型生成过程详见data.py）
最后读取数据库，调用post向服务器返回相应结果。
注意：post时需要知道聊天室的'uri'，该值在views.py中调用geneResponse时传入
"""
from .data import mydata
import requests
import re
import mysql.connector

def geneResponse(target, uri):
    """
    generate response according to:
    出现×××现象的故障主体是什么（faulty_part）    #### 故障主体
    出现×××现象的原因是什么（causes）            #### 原因
    出现×××现象对系统的影响是什么（impact_on_sys）#### 影响
    出现×××现象后，该怎么解决？（solutions）      #### 解决
    出现×××现象的详细解释是什么？ （explanation） #### 解释
    """
    # variable used to denote whether to 
    # retrieve data from faulty_part or sensor
    # True: from faulty_part
    # Faulse: from sensor
    faulty_sensor = True
    if re.search(r'.*传感器', target) != None or re.search(r'.*sensor', target, re.IGNORECASE):  # database is sensor
        faulty_sensor = False
    # flags 用来记录各个字段的出现情况
    f_faulty = False
    f_causes = False
    f_impact = False
    f_solu = False
    f_exp = False
    if re.search(r'.*故障主体', target) != None:
        f_faulty = True
    if re.search(r'.*原因', target) != None:
        f_causes = True
    if re.search(r'.*影响', target) != None:
        f_impact = True
    if re.search(r'.*解决', target) != None:
        f_solu = True
    if re.search(r'.*解释', target) != None:
        f_exp = True
    
    flags = [f_faulty, f_causes, f_impact, f_solu, f_exp]
    # 对要进行相似度匹配的字段进行预处理
    target_text = mydata.pre_process_cn([target], low_freq_filter=False)
    text = target_text[0]
    if faulty_sensor:  # database is faulty_part
        bow = mydata.dictionary_f.doc2bow(text) 
        ml_lsi = mydata.lsi_f[bow]     # ml_lsi 形式如 (topic_id, topic_value)
        sims = mydata.index_f[ml_lsi] 

        sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
        # retrieve data from database
        postRequest(sort_sims[1][0], flags, faulty_sensor, uri)
    else:               # data base is sensor
        bow = mydata.dictionary_s.doc2bow(text) 
        ml_lsi = mydata.lsi_s[bow]     # ml_lsi 形式如 (topic_id, topic_value)
        sims = mydata.index_s[ml_lsi] 

        sort_sims = sorted(enumerate(sims), key=lambda item: -item[1])
        # retrieve data from database
        postRequest(sort_sims[1][0], flags, faulty_sensor, uri)
        
def postRequest(index, flags, faulty_sensor, uri):
    """
    make different post request according to flags
    """
    if flags[0]:
        makePost(index, 'faulty_body', faulty_sensor, uri)
    if flags[1]:
        makePost(index, 'causes', faulty_sensor, uri)
    if flags[2]:
        makePost(index, 'impact_on_sys', faulty_sensor, uri)
    if flags[3]:
        makePost(index, 'solutions', faulty_sensor, uri)
    if flags[4]:
        makePost(index, 'explanation', faulty_sensor, uri)

def makePost(index, selection, faulty_sensor, uri):
    """
    make post request
    """
    if faulty_sensor:  # retrieve data from faulty_part
        phrase = "SELECT %s FROM faulty_part WHERE record_no = %d" % (selection, index+1)
    else:              # retrieve data from sensor
        phrase = "SELECT %s FROM sensor WHERE record_no = %d" % (selection, index+1)
    query = (phrase)
    mydata.cnx = mysql.connector.connect(user='mychat', password='qazwsx456852', database='database_chat')
    mydata.cursor = mydata.cnx.cursor()
    mydata.cursor.execute(query)
    exp_solution = []
    for d in mydata.cursor:
        if selection == 'solutions':
            exp_solution += ['解决步骤:'+d[0].replace("\n", "<br/>")]
        else:
            exp_solution += d
    mydata.cursor.close()
    mydata.cnx.close()

    # currentUri = '3462ea90e89d4be'
    currentUri = uri    # '0be16d07e771451'
    url = 'http://localhost:8000/api/chats/%s/messages/' % currentUri
    # authToken = '50bc622a6a2dcae234e434a5285da4cbd43c326a'
    mydata.authToken = mydata.generateToken()  # generate token before post data
    headers = {'Authorization': 'Token %s' % mydata.authToken}
    for Message in exp_solution:
        requests.post(url, headers=headers, json={'message': Message})
def gRes(uri):
    currentUri = uri    # '0be16d07e771451'
    url = 'http://localhost:8000/api/chats/%s/messages/' % currentUri
    # authToken = '50bc622a6a2dcae234e434a5285da4cbd43c326a'
    mydata.authToken = mydata.generateToken()  # generate token before post data
    headers = {'Authorization': 'Token %s' % mydata.authToken}
    Message = ''  # input your response ->_->
    requests.post(url, headers=headers, json={'message': Message})


