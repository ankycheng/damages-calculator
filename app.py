from flask import Flask, jsonify, request, make_response, abort, render_template
from flask_cors import CORS, cross_origin
from utils import *
from charts import *

import numpy as np
from numpy import exp, cos, linspace
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt

# https://github.com/matplotlib/matplotlib/issues/4590#issuecomment-415235233
# 用 "agg" 來跑 headless 的 pandas
matplotlib.use("agg")
import math

app = Flask(__name__)
CORS(app, supports_credentials=True, resources='/*')


@app.route('/')
def index():
    return "Hello, World!"


@cross_origin()
@app.route('/hackmmurabi/calculator', methods=['POST'])
def calculator():
    if not request.json:
        abort(400)
    formData = request.json
    # print(formData)
    solatium_pars = {
        'accuser_edu': int(formData['accuser_edu']),
        'accuser_age': int(formData['accuser_age']),
        'accuser_occupation': int(formData['accuser_occupation']),
        'accuser_annual_rev': int(formData['accuser_annual_rev']),
        'accuser_investment': int(formData['accuser_investment']),
        'defendant_edu': int(formData['defendant_edu']),
        'defendant_age': int(formData['defendant_age']),
        'defendant_occupation': int(formData['defendant_occupation']),
        'defendant_annual_rev': int(formData['defendant_annual_rev']),
        'defendant_investment': int(formData['defendant_investment']),
        'fault_percentage_accuser': int(formData['fault_percentage_accuser']),
        'fault_percentage_defendant': int(formData['fault_percentage_defendant'])
    }

    vehicle_pv = Present_value(int(formData['vehicle_type']), int(formData['vehicle_start_value']), int(
        formData['vehicle_end_value']), int(formData['vehicle_used_years']))
    revnue_loss_amount = revnue_loss(int(formData['income_avg']), int(
        formData['days_in_month']), int(formData['rest_days']))
    ability_loss_amount = ability_loss_num(int(formData['disable_level']), int(
        formData['insured_salary']), int(formData['current_age']))
    history_solatium = jdReport(x, 'judgement', *formData['keywords'])
    solatium_rate = solatium_cal(solatium_pars)
    predicted_solatium = history_solatium*solatium_rate
    # print(solatium_rate)

    # print(ability_loss_amount)
    results = {
        'vehicle': round(vehicle_pv),
        'loss_from_not_working': round(revnue_loss_amount),
        'disabled_compensation': round(ability_loss_amount),
        'care_expense': 0,
        'solatium': round(predicted_solatium),
        'falut_accuser': int(formData['fault_percentage_accuser'])/100,
        'result': True
    }

    return jsonify(results), 200

x = pd.read_pickle("statics/datas/result.pickle")
t1=x['jd_money'].values.tolist()
t2=x['solatium_request'].values.tolist()
x['jd_solatium_predict']=[b*0.8 if a>=b else a*0.7 for a,b in zip(t1,t2)]

@app.route('/charts')
def chartTest():
    keywords = ['扶養', '憂鬱']
    url_jdReportHist = jdReportHist(x,'judgement',*keywords)
    url_jdReportHistGaussian = jdReportHistGaussian(x,'judgement',*keywords)
    url_jdReportHistRealPredict = jdReportHistRealPredict(x,'judgement',*keywords)
    url_jdReportScatterRealPredict = jdReportScatterRealPredict(x,'judgement','植物人','死亡')

    return render_template('charts.html',
                        jdReportHist = url_jdReportHist,
                        jdReportHistGaussian = url_jdReportHistGaussian,
                        jdReportHistRealPredict = url_jdReportHistRealPredict,
                        jdReportScatterRealPredict = url_jdReportScatterRealPredict
                        )

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)


if __name__ == '__main__':
    app.run(debug=True)
