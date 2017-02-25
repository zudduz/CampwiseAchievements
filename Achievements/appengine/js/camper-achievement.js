var ca = ca || {};
ca.scheduleAdjust = ca.scheduleAdjust || {};

ca.scheduleAdjust.data = sessionStorage.caData ? JSON.parse(sessionStorage.caData) : {};
ca.scheduleAdjust.init = function() {
    $('#content').text('Loading...');
    $.getJSON('/report_schedule_adjust_json' + window.location.search)
            .done(ca.scheduleAdjust.dataLoaded)
            .fail(function() {
                window.alert('Data Load failed');
            });
};

ca.scheduleAdjust.dataLoaded = function(data) {
    ca.scheduleAdjust.data = data;
    sessionStorage.caData = JSON.stringify(data);
    ca.scheduleAdjust.writeAlphabetical();
}

ca.scheduleAdjust.writeAlphabetical = function() {
    let data = ca.scheduleAdjust.data;
    data.scheduleCampers.forEach(sc => {
        $('#content').append(sc.camper.lastName + ', ' + sc.camper.firstName + '<br/>')
        console.log(sc.camper.lastName);
    });
}
