var ca = ca || {};
ca.scheduleAdjust = ca.scheduleAdjust || {};

ca.scheduleAdjust.init = function() {
    console.log('Hello World!');
    $.getJSON('/report_schedule_adjust_json' + window.location.search)
        .done(function(data) {
            console.log(data);
        })
        .fail(function() {
            window.alert('Data Load failed');
        });
};

