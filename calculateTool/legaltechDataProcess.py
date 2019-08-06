import json
import pymongo
from pymongo import MongoClient
import pandas as pd
import numpy as np
import os
import jieba 
import nltk
import math
import string
from collections import Counter
import re


#自用字典
jieba.load_userdict("/Users/benbilly3/Desktop/Legaltech/MoreData/myaccidentdict.txt")
jieba.load_userdict("/Users/benbilly3/Desktop/Legaltech/MoreData/mycostdict.txt")

#進入資料庫
def enterLocalMD(Database,collection):
    client = MongoClient('localhost', 27017) #建立資料庫連線
    db = client[Database]#進入資料庫
    coll = db[collection] #進入collection(table)
    return coll

#進入線上資料庫
def enterOnlineMD(Database,collection):
    client = MongoClient('mongodb://hackmmurabi:ksfadacai@18.139.157.63:27017/') #建立資料庫連線
    db = client[Database]#進入資料庫
    coll = db[collection] #進入collection(table)
    return coll

#處理函式
def jdProcess(file_path):
    try:
        content = open(file_path,encoding="utf-8").read()#讀檔
        for i in ['\\r','\\n',' ','\u3000']:#去除骯髒字元
            content= content.replace(i, '')
        lines=json.loads(content,encoding="utf-8")#load json
    except:
        #判決格式錯誤時引入
        d={'court':0,'date': 0,'no': 0,'sys': 0,'reason': 0,'judgement': 0,'type': 0,
           'historyHash': 0,'mainText': 0,'opinion': 0,'relatedIssues':0,'party':0}
        error= d.fromkeys(d, file_path)#value為自己路徑，將value塞進key，避免重複
        return error
    return lines

#將原始檔json匯入到MD
def jdImport(court_dir_path,collection):#第一個變數為json檔存放資料夾位置,第二個變數為table名稱
    for file in court_dir_path:
        print(file)
        dataset=[os.path.join(root,file) for root, dirs, files in os.walk(file) for file in files]
        df=[jdProcess(i) for i in dataset[:]]#陣列儲存，快速
        collection.insert(df)

#陣列直接儲存，未經處理，用於local篩選DB後匯入      
def jdImport2(court_dir_path,collection):#第一個變數為json檔存放資料夾位置,第二個變數為table名稱
    for file in court_dir_path:
        dataset=[os.path.join(root,file) for root, dirs, files in os.walk(file) for file in files]
        if file+'/.DS_Store' in dataset:
            dataset.remove(file+'/.DS_Store')
        for file_path in dataset:
            print(file_path)
            content = open(file_path).read()#讀檔
            lines=json.loads(content)
            collection.insert(lines)
        
#欄為絕對值搜尋
def mdGeneralFilter(collection,operator="$and",**kwargs):
    ls=[{col:value} for col,value in kwargs.items()]
    a=[post for post in collection.find({operator:ls})]
    result=pd.DataFrame(a,index=range(0,len(a)))
    return result

# mdGeneralFilter(collection2,reason="損害賠償",sys="民事")

#同欄位包含值(多選)
def mdIncludeFilter(collection,column,*args):
    ls=[i for i in args]
    a=[post for post in collection.find({column:{"$in":ls}})]
    result=pd.DataFrame(a,index=range(0,len(a)))
    return result

#mdIncludeFilter(collection,"reason","損害賠償","侵權行為損害賠償")

#法條查詢($and,$or,$nor,$gt,$lt,$in,$nin)
def mdLegalFilter(collection,operator="$and",**kwargs):
    ls=[{'relatedIssues':{'lawName': lawName, 'issueRef': issueRef }} for lawName,issueRef in kwargs.items()]
    a=[post for post in collection.find({operator:ls})]
    result=pd.DataFrame(a,index=range(0,len(a)))
    return result

# mdLegalFilter(collection2,"$and",民事訴訟法="53",家事事件法="41")

#當事人查詢
def mdPartyFilter(collection,grouplist,title,value):#group要貼list
    ls=[{'party':{'group': d1, 'title': d2,'value': d3 }} for d1,d2,d3 in zip([grouplist],[title],[value])]
    a=[post for post in collection.find(ls[0])]
    result=pd.DataFrame(a,index=range(0,len(a)))
    return result
# mdPartyFilter(collection2,['plaintiff', 'agentAdLitem'],"訴訟代理人",'姜立方')

#切片提取資料庫轉pandas
def pdGet(collection,start=0,end=None):
    res=collection.find({})[start:end]#提取變json
    a=list(res)#轉成json 陣列
    df=pd.DataFrame(a,index=range(0,len(a)))
    return df

#pdGet(collection,1000,5000)

#Pandas內容包含聯集搜尋
def pdColFilter(dataframe,col_name,*args):
    select=dataframe[col_name].values.tolist()
    dataset=[]
    for key in args:
        a=[key in i for i in select]
        df=dataframe[a]
        dataset.append(df)
    result=pd.concat(dataset)
    return  result[~ result.duplicated(subset="judgement")]#去掉重複

# pdColFilter(pdGet(collection2,0,5000),"judgement","事故","車禍")

#Pandas內容包含交集搜尋
def pdColFilterIntersection(dataframe,col_name,*args):
    for key in args:
        select=dataframe[col_name].values.tolist()
        a=[key in i for i in select]
        dataframe=dataframe[a]
    return  dataframe


#過濾特殊符號
def removeSymbol(text):
    content=text
    for i in ['/','\n',' ','\u3000','，',',','。','（','）','、','-','：','(',')',".",'；','「','」']:#去除骯髒字元
        content= content.replace(i, '')
    return content

def removeSymbol2(text):
    content=text
    for i in ['/','\n',' ','\u3000','，',',','。','（','）','、','-','：','(',')',".",'；','「','」']:#去除骯髒字元
        try:
            content= content.remove(i)
        except:
            continue
    return content

def replaceWords(text,replaceword,*args):
    content=text
    for i in args:#去除骯髒字元
        content= content.replace(i, replaceword)
    return content

#斷詞輸出成text
def jiebCutToText(text):
    seg_list = jieba.cut(text, cut_all=False)
    segments='/ '.join(seg_list)
    return segments

#斷詞輸出成list
def jiebCutToList(text):
    seg_list = jieba.cut(text, cut_all=False)
    segments=','.join(seg_list)
    segments_list=segments.split(",")
    return segments_list

#過濾停用字,
#法律斷詞轉成list
stopWords=[]
with open('/Users/benbilly3/Desktop/Legaltech/MoreData/stopWords.txt', 'r', encoding='UTF-8') as file:
    for data in file.readlines():
        data = data.strip()
        stopWords.append(data)
def removeStopWords(text):
    segments=[]
    remainderWords=[]
    #結巴中文斷詞
    segments = jieba.cut(text, cut_all=False)
    # 移除停用詞及跳行符號
    remainderWords = list(filter(lambda a: a not in stopWords and a != '\n', segments))
    return remainderWords

#勝敗訴分類
def winOrloss(df):
    df2=df.loc[:,'mainText'].apply(lambda s:removeStopWords(s))
#     j1=['被告', '應給付', '原告']
#     j2=['被告', '應','連帶給付', '原告']
#     j3=['被告', '應分別','給付', '原告']
#     df["winOrloss"]=["被告敗訴" if (x[:3]==j1)or(x[:4]==j2)or(x[:4]==j3) else "被吿勝訴" for x in df2]
    df["winOrloss"]=["被告敗訴" if ('應給付' in x)or('連帶給付' in x)or('分別給付' in x) else "被吿勝訴" for x in df2]
    return df

#計算各字權重,num為顯示前幾大
def tokens_count(text,num=25):
    tokens = removeStopWords(text)
    count = Counter(tokens)
    return count.most_common(num)

#tfidf演算法找文本關鍵字(扣除停用字),sent為字串檔,num為前幾大,withWeight為權重,allowPOS為篩選詞性
def tfidf_RSW(sent,num=20,withWeight=True,allowPOS=("n",'v')):
    a=removeStopWords(sent)
    senttext=('/ '.join(a))
    result=jieba.analyse.extract_tags(senttext,num,withWeight, allowPOS)#allowPOS選取詞性
    return result

#詞彙多樣性比率
def lexical_diversity(text):
    return round((len(set(text)) / len(text))*100,4)

#抽取金額
def jiebaSelectMoney(text):
    try:
        m=text[text.index("幣")+1:text.index("元")]
    except:
        m=None
    return m

#大寫中文轉數字
CN_NUM = { '〇' : 0, 
           '一' : 1, 
           '二' : 2, 
           '三' : 3, 
           '四' : 4, 
           '五' : 5, 
           '六' : 6, 
           '七' : 7, 
           '八' : 8, 
           '九' : 9, 
           '零' : 0, 
           '壹' : 1, 
           '貳' : 2, 
           '參' : 3, 
           '肆' : 4, 
           '伍' : 5, 
           '陸' : 6, 
           '柒' : 7, 
           '捌' : 8, 
           '玖' : 9, 
           '貮' : 2, 
           '兩' : 2,
         }

# Declare Units
CN_UNIT = { '十' : 10, 
            '拾' : 10, 
            '百' : 100, 
            '佰' : 100, 
            '千' : 1000, 
            '仟' : 1000, 
            '萬' : 10000, 
            '億' : 100000000,
            '兆' : 1000000000000,
          }

#大寫中文轉數字,多層例外處理
#大寫中文轉數字,多層例外處理
def chinese_to_arabic(cn): 
    if cn==None:
        return None
    try:#抽純數字出來
        num= int(cn.replace('（下同）', '').replace(',', ''))
    except (ValueError ):#處理大寫中文
        try:
            if cn.count('幣')==1:#弄掉寫兩次新台幣的
                cn=cn[cn.index("幣")+1:]
            unit = 0 # current 
            ldig = [] # digest 
            for cndig in reversed(cn): 
                # If the char is unit, then store unit value for number
                if cndig in CN_UNIT: 
                    unit = CN_UNIT.get(cndig)
                    if unit == 10000 or unit == 100000000: 
                        ldig.append(unit) 
                        unit = 1 
                # If the char is number, then multiple number with unit and append to ldig
                else: 
                    dig = CN_NUM.get(cndig)
                    if unit: 
                        dig *= unit 
                        unit = 0 
                    ldig.append(dig) 
            # unit = ten should be handled
            if unit == 10: 
                ldig.append(10) 

            val, tmp = 0, 0 
            # print the final result back to readable form
            for x in reversed(ldig): 
                # unit = 10000 & 100000000 should be handled
                if x == 10000 or x == 100000000: 
                    val += tmp * x 
                    tmp = 0 
                else: 
                    tmp += x 
            val += tmp
            return val
        except:
            try:
                if ( '萬' in cn):#處理1萬2千這種數字中文穿插的型態
                    cn=cn[:cn.index('萬')+1]
                    cn=cn.replace("萬",'0000')
                num=re.sub("\D", "", cn)
            except TypeError :#特殊型態不管了
                return None
    return num

#提取df某欄金額生成
def pdMoneyCol(df,col_name,money_col_name):
    df[money_col_name]=df[col_name].apply(lambda s:jiebaSelectMoney(s)).apply(lambda s: chinese_to_arabic(s))
    return df

#[(1.2),(3.4)....]轉成雙欄dataframe
def pdTupleToDf(df,col_name1,col_name2):
    d=[]
    d2=[]
    for n in range(len(df)):#
        s=df.iloc[n]
        for k,v in s:
            d.append(k)
            d2.append(v)
    return pd.DataFrame({col_name1:d,col_name2:d2},index=range(len(d)))

def pdTupleToDf2(list_dadta,col_name1,col_name2):
    d=[]
    d2=[]
    for k,v in list_dadta:
        d.append(k)
        d2.append(v)
    return pd.DataFrame({col_name1:d,col_name2:d2},index=range(len(d)))

def allKeyWordsIndex(keyword,text):
    text=jiebCutToList(text)
    try:
        d=[]
        while keyword in text:#直到keyword沒在text才停下
            location=text.index(keyword)
            text=text[location+1:]
            d.append(location+1)
        d[0]=d[0]-1
    except:
        return []
    return np.cumsum(d)

def selectSent(sent,key1,key2,key3,range1=30,range2=30):
    sent2=jiebCutToList(sent)

    c1=allKeyWordsIndex(key1,sent)
    c2=allKeyWordsIndex(key2,sent)
    c3=allKeyWordsIndex(key3,sent)

    try:
        d=[]
        d_2=[]
        d_3=[]

        for i in c3:
            a=[i-n for n in range(1,range1)]
            a2=[i-n for n in range(1,range2)]
            g=sum([ i in c2 for i in a])
            g2=sum([ i in c1 for i in a2])
            if (g>0)&(g2>0):
                d.append(i)
                d_2.append(c2[c2<i].max())
                d_3.append(c1[c1<(c2[c2<i].max())].max())
        dict1=[]
        for i,i2 in zip(d,d_3):
            result=sent2[i2:i+1]
            dict1.append(result)

        dict2=[]
        for i in dict1:
            segments=removeSymbol(','.join(i))
            dict2.append(segments)
    except:
        return None
    return dict2

def selectSentSetReduce(text):
    try:
        d=[]
        a1=selectSent(text,'慰撫金','萬元','適合')
        a2=selectSent(text,'慰撫金','元','適合')
        a3=selectSent(text,'非財產上損害','萬元','適合')
        a4=selectSent(text,'非財產上損害','元','適合')
        a5=selectSent(text,'慰撫金','酌減','元')
        a6=selectSent(text,'慰撫金','酌減','萬元')
        for i in [a1,a2,a3,a4]:
            d.extend(i)
        
    except:
        return None
    return d


def selectSentSet(text):
    try:
        d=[]
        a1=selectSent(text,'請求','萬元','慰撫金')
        a2=selectSent(text,'請求','慰撫金','萬元')
        a3=selectSent(text,'請求','慰撫金','元')
        a4=selectSent(text,'原告','慰撫金','元')
        a5=selectSent(text,'原告','請求','慰撫金')
        for i in [a1,a2,a3,a4,a5]:
            d.extend(i)
        
    except:
        return None
    return d


#抽取金額
def solatiumSelectMoney(text):
    try:
        m=text[text.index("金")+1:text.index("元")]
    except:
        try:
            m=text[text.index("金")+1:text.index("萬")] 
        except:   
            try:
                m=text[text.index("求")+1:text.index("元")] 
            except:
                m=None     
    return m


#從斷句資料再抽金額
def solatiumSelectMoney2(text):
    a=text.replace("'",'')
    a=a[1:-1]
    b=a.split (',')
    d=[]
    for i in range( len(b)):
        c=solatiumSelectMoney(b[i])
        try:
            if ( '萬' in c):
                c=c[:c.index('萬')+1]
                c=c.replace("萬",'0000')
            c=re.sub("\D", "", c)
            d.append(int(c))    
        except:
            d.append(0)
        try:
            r=sorted(d)[-1]
            if r>=10000000:
                r=sorted(d)[-2]
                if r>100000000:
                    r=r/10000
        except:
            r=0
    return  r