# data.py
"""
数据生成模块，该模块在Django初始化时调用，所以初始读取数据库部分只用进行这一次。分为以下两步：
1.从数据库中读取故障部件告警信息(faulty_part)的现象(phenomenon)以及程度(degree)字段，
  从数据库中读取传感器告警信息(sensor)的现象(phenomenon)字段。
  以上两者作为在geneRes模块中进行相似度匹配的基准。
2.生成LSI模型所需的(index, dictionary, lsi)，这一部分详见[https://my.oschina.net/kakablue/blog/314513]
"""
import nltk
import jieba.analyse
from nltk.tokenize import word_tokenize
from nltk.stem.lancaster import LancasterStemmer
from gensim import corpora, models, similarities
# get data from database
import mysql.connector
import requests

class Data:
    """
    generate data that will be used later in the retrieval part.
    """
    def __init__(self):
        """
        initilization
        get data from database
        process raw data
        get value index, dictionary, lsi
        """
        # generate token for hubot
        self.authToken = ''# = self.generateToken()
        self.cnx = mysql.connector.connect(user='mychat', password='qazwsx456852', database='database_chat')
        self.cursor = self.cnx.cursor()
        self.total_f = []   # faulty_part data 故障部件模式告警
        self.total_s = []   # sensor data 传感器模式告警
        # get faulty_part data
        query = ("SELECT phenomenon, degree FROM faulty_part")
        self.cursor.execute(query)
        for (p, d) in self.cursor:
            self.total_f += [p+' '+d]
        # get sensor data
        query = ("SELECT phenomenon FROM sensor")
        self.cursor.execute(query)
        for d in self.cursor:
            self.total_s += d
    
        self.cursor.close()
        self.cnx.close()

        self.lib_texts_f = self.pre_process_cn(self.total_f, False)
        (self.index_f,self.dictionary_f,self.lsi_f) = self.train_by_lsi(self.lib_texts_f)

        self.lib_texts_s = self.pre_process_cn(self.total_s, False)
        (self.index_s,self.dictionary_s,self.lsi_s) = self.train_by_lsi(self.lib_texts_s)

    def generateToken(self):
        """
        生成Token，在geneRes模块中调用，因为在向服务器进行post请求时需要Token认证
        """
        url = 'http://localhost:8000/auth/token/create/'
        r = requests.post(url, json={'username': 'hubot', 'password': 'hubotpassword'})  # 所以在前端界面Sign up时要创建这么一个用户
        return r.json()['auth_token']        

    def pre_process_cn(self, courses, low_freq_filter = False):
        """
        preprocess data
        """
        texts_tokenized = []
        for document in courses:
            texts_tokenized_tmp = []
            for word in word_tokenize(document):
                # extract_tags(sentence, topK=20, withWeight=False,
                #   allowPOS=(), withFlag=False) method of 
                #   jieba.tfidf.TFIDF instance.
                #   Extract keywords from sentence using TF-IDF
                #   algorithm. 
                # para: topK: return how many top keywords
                texts_tokenized_tmp += jieba.analyse.extract_tags(word,10)
            texts_tokenized.append(texts_tokenized_tmp)   
        texts_filtered_stopwords = texts_tokenized
        #去除标点符号
        english_punctuations = [',', '.', ':', ';', '?', '(', ')', '[', ']', '&', '!', '*', '@', '#', '$', '%']
        texts_filtered = [[word for word in document if not word in english_punctuations] for document in texts_filtered_stopwords]
        #词干化
        st = LancasterStemmer()
        texts_stemmed = [[st.stem(word) for word in docment] for docment in texts_filtered]
        #去除过低频词
        if low_freq_filter:
            all_stems = sum(texts_stemmed, [])
            stems_once = set(stem for stem in set(all_stems) if all_stems.count(stem) == 1)
            texts = [[stem for stem in text if stem not in stems_once] for text in texts_stemmed]
        else:
            texts = texts_stemmed
        return texts

    def train_by_lsi(self, lib_texts):
        """
        train lsi model
        """
        # a mapping between words and their integer ids.
        dictionary = corpora.Dictionary(lib_texts)
        # doc2bow(): 将collection words 转为词袋，用两元组(word_id, word_frequency)表示
        # (word_id, word_count)
        corpus = [dictionary.doc2bow(text) for text in lib_texts]     
        tfidf = models.TfidfModel(corpus)
        corpus_tfidf = tfidf[corpus]

        #拍脑袋的：训练topic数量为10的LSI模型
        lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=10)
        index = similarities.MatrixSimilarity(lsi[corpus])     # index 是 gensim.similarities.docsim.MatrixSimilarity 实例
    
        return (index, dictionary, lsi)
# instantiate 实例化
mydata = Data()
