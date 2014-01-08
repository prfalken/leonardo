$(document).ready(function() {
  if($('#dt_from').val() != 'from')
    $('#toggleDateTimePicker').parent().addClass('active');
  else
    $('#dateTimePicker').hide();
});

$(function() {
  $('#toggleDateTimePicker').click(function() {
    $('#dateTimePicker').toggle(400);
  });
});

$(function() {
  var startDateTextBox = $('#dt_from');
  var endDateTextBox = $('#dt_to');
  startDateTextBox.datetimepicker({
    dateFormat: 'yy-mm-dd',
    onClose: function(dateText, inst) {
      setDestinationDate(startDateTextBox, endDateTextBox, dateText);
    }
  });
  endDateTextBox.datetimepicker({ 
    dateFormat: 'yy-mm-dd',
    onClose: function(dateText, inst) {
      setDestinationDate(endDateTextBox, startDateTextBox, dateText);
    }
  });
});

function getURLParameter(name) {
  return decodeURIComponent(
    (RegExp(name + '=' + '(.+?)(&|$)').exec(location.search)||[,""])[1]
  );
}

function removeURLParameter(url, parameter) {
    //prefer to use l.search if you have a location/link object
    var urlparts= url.split('?');   
    if (urlparts.length>=2) {

        var prefix= encodeURIComponent(parameter)+'=';
        var pars= urlparts[1].split(/[&;]/g);

        //reverse iteration as may be destructive
        for (var i= pars.length; i-- > 0;) {    
            //idiom for string.startsWith
            if (pars[i].lastIndexOf(prefix, 0) !== -1) {  
                pars.splice(i, 1);
            }
        }

        url= urlparts[0]+'?'+pars.join('&');
        return url;
    } else {
        return url;
    }
}

function setDestinationDate(srcDateBox, destDateBox, dateText)
{
  if (destDateBox.val() == destDateBox.prop("defaultValue"))
    destDateBox.val(dateText);
  else {
    var startDate = $('#dt_from').datetimepicker('getDate');
    var endDate = $('#dt_to').datetimepicker('getDate');
    if (startDate > endDate)
      destDateBox.datetimepicker('setDate', srcDateBox.datetimepicker('getDate'));
  }
}

function formatSelectedDate(date) {
  return "" + zeroPad(date.getMonth() + 1) + "/" + 
    zeroPad(date.getDate()) + "/" 
    + date.getFullYear() + " " 
    + zeroPad(date.getHours()) + ":" + 
    zeroPad(date.getMinutes());
}

function getMethods(obj) {
  var result = [];
  for (var id in obj) {
    try {
      if (typeof(obj[id]) == "function") {
        result.push(id + ": " + obj[id].toString());
      }
    } catch (err) {
      result.push(id + ": inaccessible");
    }
  }
  return result;
}

function selectDt() {
  dt_from = new Date($('#dt_from').val());
  dt_to = new Date($('#dt_to').val());
  window.location = buildGraphiteDateUrl(dt_from, dt_to);
  return true;
}

function buildGraphiteDateUrl(dt_from, dt_to)
{
  from = buildGraphiteDateString(dt_from);
  to = buildGraphiteDateString(dt_to);
  newurl = document.URL.replace(/#/g, '');
  newurl = removeURLParameter(newurl, "from")
  newurl = removeURLParameter(newurl, "to")
  params = "?from=" + from + "&to=" + to;
  return newurl + params;
}

function buildGraphiteDateString(date)
{
  // val = zeroPad(date.getHours()) + "%3A" + zeroPad(date.getMinutes()) + "_" + date.getFullYear() + zeroPad(date.getMonth()+1) + zeroPad(date.getDate());
  val = Math.round(date.getTime() / 1000);
  return val;
}

function zeroPad(num) {
	num = "" + num
	if (num.length == 1) {
		num = "0" + num
	}
	return num
}
