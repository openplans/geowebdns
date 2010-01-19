var API = '/api1';
var geocoder = new GClientGeocoder();

$(function () {
  $.getJSON(API + '/types', function (data) {
    var sel = $('#type');
    $.each(data, function(key, value) {
      sel.append($("<option></option>").attr("value",value).text(value));
    });
  });

  $('#geocode').click(function () {
    var address = $('#address');
    if (address.attr('value')) {
      geocoder.getLatLng(
        address.attr('value'),
        function(point) {
          if (!point) {
            $('#point').attr('value', 'Point not found');
          } else {
          console.log(point);
            $('#point').attr('value', (point.y + ' ' + point.x));
          }
        });
      }
    });

  $('#query-button').click(function () {
    var point = $('#point').attr('value');
    var points = point.split(/\s+/);
    var url = API + '?lat=' + points[0] + '&long=' + points[1];
    $('#type option').each(function () {
      url += '&type=' + escape(this.value);
    });
    $('#request').text(url);
    $.getJSON(url, function(data) {
      $('#result').html('')
      $.each(data.results, function (key, value) {
        var result = $('#result-template .result').clone();
        $('.type', result).attr('href', value["type"]);
        $('.type', result).text(value["type"]);
        $('.uri', result).attr('href', value["uri"]);
        $('.uri', result).text(value["uri"]);
        $('.name', result).text(value["name"]);
        $('.kml', result).attr('href', value["kml_uri"]);
        $('.viewkml', result).attr(
            'href',
            "http://maps.google.com/?q=" + escape(value["kml_uri"]));
        $('#result').append(result);
      });
    });
  });

});
