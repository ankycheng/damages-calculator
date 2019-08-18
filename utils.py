import pandas as pd
import os, sys, requests

def downloadFile(url, fileName, targetPath):
    with open(targetPath+fileName, 'wb') as f:
        print("Downloading {}".format(fileName))
        response = requests.get(url, stream=True)
        total_length = response.headers.get('content-length')

        if total_length is None: # no content length header
            f.write(response.content)
        else:
            dl = 0
            total_length = int(total_length)
            for data in response.iter_content(chunk_size=4096):
                dl += len(data)
                f.write(data)
                done = int(50 * dl / total_length)
                sys.stdout.write("\r[%s%s]" % ('=' * done, ' ' * (50-done)) )    
                sys.stdout.flush()
            print('download finished')


# car='汽車種類'、new='新品價值','old'=最終殘值,'已使用年'
def Present_value(car_type, new, old, use_year):
    # 機車
    if car_type == '1':
        date = 2
    # 非營業用汽車
    elif car_type == '2':
        date = 5
    # 其他
    else:
        date = 4
    d = []
    Depreciation_rate = 1-((old/new)**(1/date))
    for i in range(3):
        new = new*(1-Depreciation_rate)
        d.append(new)
    if use_year >= date:
        result = d[-1]
    else:
        result = d[use_year-1]
    return round(result)

# (每月淨收入/該月日數)*日期
# month_revnue='每月收入',month_date='當月天數',date='不能工作天數'


def revnue_loss(month_revnue, month_date, date):
    return round(month_revnue/month_date*date)

# 失能等級共分為十五等級，各等級之給付標準，按平均日投保薪資，依下列規定日數計算之：


def ability_loss_rate(loss_level):
    # loss_level='失能等級',insurance_revnue_daily='平均日投保薪資',now_age='現在年齡',retire_age='退休年齡'

    if loss_level == 1:
        date = 1200
    elif loss_level == 2:
        date = 1000
    elif loss_level == 3:
        date = 840
    elif loss_level == 4:
        date = 740
    elif loss_level == 5:
        date = 640
    elif loss_level == 6:
        date = 540
    elif loss_level == 7:
        date = 440
    elif loss_level == 8:
        date = 360
    elif loss_level == 9:
        date = 280
    elif loss_level == 10:
        date = 220
    elif loss_level == 11:
        date = 160
    elif loss_level == 12:
        date = 100
    elif loss_level == 13:
        date = 60
    elif loss_level == 14:
        date = 40
    else:
        date = 30

    loss_rate = date/1200

    return round(loss_rate*100, 2)


def ability_loss_num(loss_level, month_revnue, now_age, retire_age=65):
    # loss_level='失能等級',insurance_revnue_daily='平均日投保薪資',now_age='現在年齡',retire_age='退休年齡'
    return round(ability_loss_rate(loss_level)*month_revnue*(retire_age-now_age))


def solatium_cal(solatium_pars):

    diff_edu = solatium_pars['accuser_edu'] - solatium_pars['defendant_edu']
    diff_age = solatium_pars['accuser_age'] - solatium_pars['defendant_age']
    diff_occupation = solatium_pars['accuser_occupation'] - \
        solatium_pars['defendant_occupation']
    diff_annual_rev = solatium_pars['accuser_annual_rev'] - \
        solatium_pars['defendant_annual_rev']
    diff_investment = solatium_pars['accuser_investment'] - \
        solatium_pars['defendant_investment']

    edu_PN = 1 if diff_edu >= 0 else -1
    edu_diff_rate = diff_edu*0.5 if abs(diff_edu) <= 3 else 3*0.5*edu_PN

    age_PN = 1 if diff_age >= 0 else -1
    age_diff_rate = diff_age*0.5 if abs(diff_age) <= 2 else 2*0.5*age_PN

    occupation_diff_rate = diff_occupation*1.25

    annual_rev_diff_rate, inv_diff_rate = get_eco_diff_rate(
        diff_annual_rev, diff_investment)

    rate_total = edu_diff_rate + age_diff_rate + \
        occupation_diff_rate + annual_rev_diff_rate
    print(rate_total)
    solatium_rate = 1 + rate_total*0.05 if rate_total >= 0 else 1 + rate_total*0.08
    return solatium_rate


def get_eco_diff_rate(diff_annual_rev, diff_investment):
    annual_rev_diff_rate = 0
    inv_diff_rate = 0

    if diff_annual_rev > 2:
        annual_rev_diff_rate = -2
    elif diff_annual_rev >= 2:
        annual_rev_diff_rate = -1
    elif diff_annual_rev >= 1:
        annual_rev_diff_rate = -0.5
    elif diff_annual_rev >= 0:
        annual_rev_diff_rate = 0
    elif diff_annual_rev >= -1:
        annual_rev_diff_rate = 0.5
    elif diff_annual_rev >= -2:
        annual_rev_diff_rate = 1
    elif diff_annual_rev < -2:
        annual_rev_diff_rate = 2

    if diff_investment > 2:
        inv_diff_rate = -1.25
    elif diff_investment >= 2:
        inv_diff_rate = -1
    elif diff_investment >= 1:
        inv_diff_rate = -0.5
    elif diff_investment >= 0:
        inv_diff_rate = 0
    elif diff_investment >= -1:
        inv_diff_rate = 0.5
    elif diff_investment >= -2:
        inv_diff_rate = 1
    elif diff_investment < -2:
        inv_diff_rate = 1.25

    return annual_rev_diff_rate, inv_diff_rate


def jdReport(dataframe, col_name, *args):
    for key in args:
        select = dataframe[col_name].values.tolist()
        a = [key in i for i in select]
        dataframe = dataframe[a]

    p1 = dataframe[dataframe['winOrloss'] == '被告敗訴']
    p2 = p1[p1['jd_money']-p1['solatium_request'] >= 0]

    win_probability = round(len(p1)/len(dataframe)*100, 2)
    solatium_satisfy_probability = round(len(p2)/len(dataframe)*100, 2)
    JD_Request = round(
        (dataframe['jd_money'].mean())/(dataframe['solatium_request'].mean()), 2)
    data = {
        'jd_num': len(dataframe),
        'win_probability': win_probability,
        'solatium_satisfy_probability': solatium_satisfy_probability,
        'JD/request': JD_Request,
        'jd_money_mean': round(dataframe['jd_money'].mean(), 2),
        'solatium_request_mean': round(dataframe['solatium_request'].mean(), 2)
    }
    name = '&'.join([key for key in args])
    result = pd.DataFrame(data, index=[name])
    return result.iloc[0].jd_money_mean
