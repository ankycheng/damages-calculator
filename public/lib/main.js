'use strict';

var options = {
  beforeNext: function beforeNext(id) {
    var data = {
      'a': 500,
      'b': 5566,
      'c': 'texxxt'
    };

    if (id == 3) {
      var formData = getFormDatas();
      console.log(formData);
      $.ajax({
        url: 'http://127.0.0.1:5000/hackmmurabi/calculator',
        data: JSON.stringify(formData),
        type: 'POST',
        cache: false,
        dataType: 'json',
        contentType: 'application/json; charset=utf-8',
        crossDomain: true,
        success: function success(data) {
          if (data.result == true) {
            console.log(data);
            updateResultTable(data);
          } else {
            console.log('result not success');
          }
        },
        error: function error(e) {
          console.log(e);
        }
      });
    }
  }
};

var updateResultTable = function updateResultTable(data) {
  $('#result_vehicle_pv').html(data['vehicle']);
  $('#result_loss_from_not_working').html(data['loss_from_not_working']);
  $('#result_disabled_compensation').html(data['disabled_compensation']);
  $('#result_solatium').html(data['solatium']);
  $('#result_accuser_percentage').html(data['falut_accuser'] * 100 + '%');
  var sum = data['vehicle'] + data['loss_from_not_working'] + data['disabled_compensation'] + data['solatium'];
  var result = Math.round(sum * (1 - data['falut_accuser']));
  $('#money_result').html(result);
  $('#result_sum').html(sum);
};

var getFormDatas = function getFormDatas() {
  // 車輛
  var vehicle_type = $('#vehicle-type')[0].value;
  var vehicle_start_value = $('#vehicle-start-value')[0].value;
  var vehicle_end_value = $('#vehicle-end-value')[0].value;
  var vehicle_used_years = $('#years-used')[0].value;

  // 不能工作之損失
  var income_avg = $('#income-avg')[0].value;
  var days_in_month = $('#days-in-month')[0].value;
  var rest_days = $('#rest-days')[0].value;

  // 失能給付
  var disable_level = $('#disabled-level')[0].value;
  var insured_salary = $('#insured-salary')[0].value;
  var current_age = $('#current-age')[0].value;

  // 其他資訊
  var accuser_edu = $('#accuser-edu')[0].value;
  var accuser_age = $('#accuser-age')[0].value;
  var accuser_occupation = $('#accuser-occupation')[0].value;
  var accuser_annual_rev = $('#accuser-annual-rev')[0].value;
  var accuser_investment = $('#accuser-investment')[0].value;

  var defendant_edu = $('#defendant-edu')[0].value;
  var defendant_age = $('#defendant-age')[0].value;
  var defendant_occupation = $('#defendant-occupation')[0].value;
  var defendant_annual_rev = $('#defendant-annual-rev')[0].value;
  var defendant_investment = $('#defendant-investment')[0].value;

  var fault_percentage_accuser = $('#fault_percentage_accuser')[0].value;
  var fault_percentage_defendant = $('#fault_percentage_defendant')[0].value;

  var keywords = $('#keywords')[0].value.split(' ');
  var data = {
    'vehicle_type': vehicle_type,
    'vehicle_start_value': vehicle_start_value,
    'vehicle_end_value': vehicle_end_value,
    'vehicle_used_years': vehicle_used_years,
    'income_avg': income_avg,
    'days_in_month': days_in_month,
    'rest_days': rest_days,
    'disable_level': disable_level,
    'insured_salary': insured_salary,
    'current_age': current_age,
    'accuser_edu': accuser_edu,
    'accuser_age': accuser_age,
    'accuser_occupation': accuser_occupation,
    'accuser_annual_rev': accuser_annual_rev,
    'accuser_investment': accuser_investment,
    'defendant_edu': defendant_edu,
    'defendant_age': defendant_age,
    'defendant_occupation': defendant_occupation,
    'defendant_annual_rev': defendant_annual_rev,
    'defendant_investment': defendant_investment,
    'fault_percentage_accuser': fault_percentage_accuser,
    'fault_percentage_defendant': fault_percentage_defendant,
    'keywords': keywords
  };

  return data;
};

bulmaSteps.attach('#stepsEl', options);

// Find output DOM associated to the DOM element passed as parameter
function findOutputForSlider(element) {
  var idVal = element.id;
  var outputs = document.getElementsByTagName('output');
  for (var i = 0; i < outputs.length; i++) {
    if (outputs[i].htmlFor == idVal) return outputs[i];
  }
}

function getSliderOutputPosition(slider) {
  // Update output position
  var newPlace, minValue;

  var style = window.getComputedStyle(slider, null);
  // Measure width of range input
  var sliderWidth = parseInt(style.getPropertyValue('width'), 10);

  // Figure out placement percentage between left and right of input
  if (!slider.getAttribute('min')) {
    minValue = 0;
  } else {
    minValue = slider.getAttribute('min');
  }
  var newPoint = (slider.value - minValue) / (slider.getAttribute('max') - minValue);

  // Prevent bubble from going beyond left or right (unsupported browsers)
  if (newPoint < 0) {
    newPlace = 0;
  } else if (newPoint > 1) {
    newPlace = sliderWidth;
  } else {
    newPlace = sliderWidth * newPoint;
  }

  return {
    'position': newPlace + 'px'
  };
}

document.addEventListener('DOMContentLoaded', function () {
  // Get all document sliders
  var sliders = document.querySelectorAll('input[type="range"].slider');
  [].forEach.call(sliders, function (slider) {
    var output = findOutputForSlider(slider);
    if (output) {
      if (slider.classList.contains('has-output-tooltip')) {
        // Get new output position
        var newPosition = getSliderOutputPosition(slider);

        // Set output position
        output.style['left'] = newPosition.position;
      }

      // Add event listener to update output when slider value change
      slider.addEventListener('input', function (event) {
        if (event.target.classList.contains('has-output-tooltip')) {
          // Get new output position
          var newPosition = getSliderOutputPosition(event.target);

          // Set output position
          output.style['left'] = newPosition.position;
        }

        // Update output with slider value
        // output.value = event.target.value;
        output.value = event.target.value > 4 ? event.target.value + " 年以上" : event.target.value + " 年";
      });
    }
  });
});