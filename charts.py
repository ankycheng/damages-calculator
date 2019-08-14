import calculateTool.legaltechDataProcess as ltp
import jieba.analyse
import jieba
import pandas as pd
import numpy as np
import nltk
from collections import Counter
import re
import seaborn as sns
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import findfont, FontProperties
import matplotlib.font_manager as fm
matplotlib.use("agg")
import random
import io
import base64

# set fonts stuff
font_dirs = ['statics/fonts/', ]
font_files = fm.findSystemFonts(fontpaths=font_dirs)
font_list = fm.createFontList(font_files)
fm.fontManager.ttflist.extend(font_list)

plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = ['Arial Unicode MS']
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS'] 
plt.rcParams['font.size'] = 24
plt.rcParams["figure.figsize"] = (20, 12)
plt.subplots_adjust(left=None, bottom=0.3, right=None,
                    top=1.5, hspace=.27, wspace=.2)

def jdReportHist(dataframe, col_name, *args):
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.set_facecolor('lemonchiffon')
    ax2.set_facecolor('lemonchiffon')
    label_name = []
    for key in args:
        select = dataframe[col_name].values.tolist()
        a = [key in i for i in select]
        dataframe = dataframe[a]
        dataframe = dataframe[dataframe['solatium_request'] < 10000000]
        x = dataframe['solatium_request'].values/10000
        c = ["#"+''.join([random.choice('0123456789ABCDEF')
                        for j in range(6)])for i in range(1)]

        # 處理label
        label_name.append(key)
        try:
            label_name2 = '&'.join(label_name)
        except:
            label_name2 = label_name[0]

        p = x.mean()
        name = '&'.join([key for key in args])

        sns.distplot(x, bins=20, label=label_name2, kde=False, ax=ax1)
        ax1.set_xticks(range(0, 1100, 100))
        ax1.set_xlabel('請求金額(萬)')
        ax1.set_ylabel('人數')
        ax1.set_title(name+'--慰撫金請求金額直方圖(條件交集)')
        ax1.axvline(x=p, linewidth=4.5, color=c[0], label=label_name2+'平均金額')
        ax1.grid(color='b', linestyle='--', linewidth=0.2)
        ax1.legend()

        sns.kdeplot(x, shade=True, label=label_name2, ax=ax2)
        ax2.set_xticks(range(0, 1100, 100))
        ax2.set_xlabel('請求金額(萬)')
        ax2.set_title(name+'--慰撫金請求金額高斯分佈圖(條件交集)')
        ax2.axvline(x=p, linewidth=4.5, color=c[0], label=label_name2+'平均金額')
        ax2.legend()

    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png', dpi=300)
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)


def jdReportHistGaussian(dataframe, col_name, *args):
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.set_facecolor('snow')
    ax2.set_facecolor('snow')

    for key in args:
        select = dataframe[col_name].values.tolist()
        a = [key in i for i in select]
        df2 = dataframe[a]
        df2 = df2[df2['solatium_request'] < 10000000]
        x = df2['solatium_request'].values/10000
        c = ["#"+''.join([random.choice('0123456789ABCDEF')
                        for j in range(6)])for i in range(1)]

        p = x.mean()
        name = '&'.join([key for key in args])

        sns.distplot(x, bins=20, label=key, kde=False, ax=ax1)
        ax1.axvline(x=p, linewidth=4.5, color=c[0], label=key+'平均金額')
        ax1.set_xticks(range(0, 1100, 100))
        ax1.set_ylabel('人數')
        ax1.set_xlabel('請求金額(萬)')
        ax1.set_title(name+'慰撫金請求金額直方圖')
        ax1.grid(color='b', linestyle='--', linewidth=0.2)
        ax1.legend()

        sns.kdeplot(x, shade=True, label=key, ax=ax2)
        ax2.set_xticks(range(0, 1100, 100))
        ax2.set_xlabel('請求金額(萬)')
        ax2.set_title(name+'慰撫金請求金額高斯分佈圖')
        ax2.axvline(x=p, linewidth=4.5, color=c[0], label=key+'平均金額')
        ax2.legend()

    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)


def jdReportHistRealPredict(dataframe, col_name, *args):
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.set_facecolor('lemonchiffon')
    ax2.set_facecolor('lemonchiffon')

    title_name = '&'.join([key for key in args])
    for keyword in args:
        select = dataframe[col_name].values.tolist()
        a = [keyword in i for i in select]
        dataframe = dataframe[a]

    for i in ['solatium_request', 'jd_solatium_predict']:
        dataframe = dataframe[dataframe[i] < 10000000]
        x = dataframe[i].values/10000

        c = ["#"+''.join([random.choice('0123456789ABCDEF')
                        for j in range(6)])for i in range(1)]
        c2 = ["#"+''.join([random.choice('0123456789ABCDEF')
                        for j in range(6)])for i in range(1)]

        if i == 'solatium_request':
            name = '請求金額'
        else:
            name = '實判預估金額'
        
        p = x.mean()
        sns.distplot(x, bins=20, label=name, kde=False, ax=ax1)
        ax1.set_xticks(range(0, 1100, 100))
        ax1.set_ylabel('人數')
        ax1.set_xlabel('金額(萬)')
        ax1.set_title(title_name+'--慰撫金請求金額V.S實判預估金額')
        ax1.axvline(x=p, linewidth=4.5, color=c[0], label=name+'平均金額')
        ax1.grid(color='b', linestyle='--', linewidth=0.2)
        ax1.legend()

        sns.kdeplot(x, shade=True, label=name, ax=ax2)
        ax2.set_xticks(range(0, 1100, 100))
        ax2.set_xlabel('金額(萬)')
        ax2.set_title(title_name+'--慰撫金請求金額V.S實判預估金額')
        ax2.axvline(x=p, linewidth=4.5, color=c2[0], label=name+'平均金額')
        ax2.legend()

    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png', dpi=300)
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)


def jdReportScatterRealPredict(df, col_name, *args):
    df = df.reset_index()
    df = df[df['solatium_request'] < 10000000]
    df = df[df['jd_money'] < 50000000]
    df['solatium_request'] = df['solatium_request']/10000
    df['jd_solatium_predict'] = df['jd_solatium_predict']/10000
    df['jd_money'] = df['jd_money']/10000
    for keyword in args:
        select = df[col_name].values.tolist()
        a = [keyword in i for i in select]
        df = df[a]
    plt.rcParams['font.family'] = ['Arial Unicode MS']
    plt.rcParams['font.size'] = 18
    plt.rcParams["figure.figsize"] = (28, 16)

    # 請求金額與主文判決總金額散點圖
    plt.subplot(1, 2, 1, facecolor='snow')
    name = '&'.join([key for key in args])
    cmap = sns.cubehelix_palette(dark=.3, light=.8, as_cmap=True)
    ax = sns.scatterplot(x="jd_solatium_predict", y="jd_money",
                        hue="court", size="jd_solatium_predict", sizes=(100, 500),
                        palette="Set3", data=df)
    plt.title(name+'--各地法院慰撫金請求金額V.S主文總判金額', fontsize='medium')

    plt.subplot(1, 2, 2, facecolor='snow')
    df2 = df.groupby('court').count()
    df2 = df2.iloc[:, 0:1]
    df2 = df2.sort_values('index', ascending=False)
    df2 = df2.reset_index()
    ax2 = sns.barplot(x="index", y="court", data=df2)
    plt.title(name+'--各地法院案件數', fontsize='medium')

    # 標籤
    for x, y, tex in zip(df2['index'], df2.index, df2['index']):
        t = plt.text(x, y, int(tex), horizontalalignment='right',
                    verticalalignment='center', fontdict={'color': 'black', 'size': 20})

    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)


def build_graph(x_coordinates, y_coordinates):
    img = io.BytesIO()
    plt.plot([1, 2, 3, 4])
    plt.ylabel('some numbers')
    # plt.plot(x_coordinates, y_coordinates)
    plt.savefig(img, format='png')
    img.seek(0)
    graph_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return 'data:image/png;base64,{}'.format(graph_url)
