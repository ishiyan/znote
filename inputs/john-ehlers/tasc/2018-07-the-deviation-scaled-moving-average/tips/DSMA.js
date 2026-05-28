var MyModel = {};

//create parameter for period
MyModel.createParameters = function() {
  this.addParameter("DSMA Period", ParameterTypes.Int, 30, 3, 200);
};

//this function gets called once, prior to entering the main loop
MyModel.initialize = function(bars) { 
    var period = this.parameters[0].value;
    var source = bars.close;
  
    var prev = source[period - 1];
    var a1 = Math.exp(-1.414 * 3.14159 / (0.5 * period)); 
    var term = 1.414 * 180 / (0.5 * period);
    var radians = term * Math.PI / 180;
    var b1 = 2 * a1 * Math.cos(radians); 
    var c2 = b1; 
    var c3 = -a1 * a1; 
    var c1 = 1 - c2 - c3;
    var zeroes = new Array(source.length);
    zeroes.fill(0);
    var filt = new Array(source.length);
    filt.fill(1);
    var result = new Array(source.length);
    result.fill(Number.NaN);
    for(var n = 2; n < source.length; n++) {
      zeroes[n] = source[n] - source[n - 2];
      filt[n] = c1 * (zeroes[n] + zeroes[n - 1]) / 2 + c2 * filt[n - 1] + c3 * filt[n - 2];
      if (n < period) {
        continue;
      }
      var RMS = 0; 
      for(var count = 0; count < period; count++) {
        RMS = RMS + filt[n - count] * filt[n - count];
      }
      RMS = Math.sqrt(RMS / period);
      var ScaledFilt = filt[n] / RMS; 
      var alpha1 = Math.abs(ScaledFilt) * 5 / period; 
      result[n] = alpha1 * source[n] + (1 - alpha1) * prev;
      prev = result[n];
  };
  this.plot(result, "DSMA", "orange", 3);
};
  
//this function gets called once for every bar of data in the chart
MyModel.execute = function(bars, idx) {
};
return MyModel;