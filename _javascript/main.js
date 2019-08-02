let options = {

}
bulmaSteps.attach('#stepsEl', options);

// Find output DOM associated to the DOM element passed as parameter
function findOutputForSlider(element) {
  var idVal = element.id;
  let outputs = document.getElementsByTagName('output');
  for (var i = 0; i < outputs.length; i++) {
    if (outputs[i].htmlFor == idVal)
      return outputs[i];
  }
}

function getSliderOutputPosition(slider) {
  // Update output position
  var newPlace, minValue;

  var style = window.getComputedStyle(slider, null);
  // Measure width of range input
  let sliderWidth = parseInt(style.getPropertyValue('width'), 10);

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
  }
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
        output.value = event.target.value > 4?event.target.value+" 年以上":event.target.value+" 年"
      });
    }
  });
});