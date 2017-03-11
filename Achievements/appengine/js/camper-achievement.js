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
    data.scheduleCampers.forEach(sc => {
        sc.camperAchievements.forEach(ca => {
            ca.achievement = data.achievements.find(a => a.key == ca.achievementKey);
        });
        sc.periods = [];
        data.periods.forEach((period, i) => {
            sc.periods[i] = sc.camperAchievements.find(ca => ca.period == period);
        });
    });
    ca.scheduleAdjust.writeAlphabetical();
}

ca.scheduleAdjust.writeAlphabetical = function() {
    let data = ca.scheduleAdjust.data;
    $('#content').html(`
            <table>
                <thead><tr>
                    <td>Camper Name</td>
                    <td>SM</td>
                    <td>TW</td>
                    <td>RF</td>
                </tr></thead>
                <tbody id="camperRows"></tbody>
            </table>`);
    data.scheduleCampers.forEach((sc, i) => {
        let periodsHtml = '';
        sc.periods.forEach(period => periodsHtml += `<td>${period ? period.achievement.name: ''}</td>`)

        $('#camperRows').append(`<tr id="camperRow${i}"><td>${sc.camper.lastName}, ${sc.camper.firstName}</td>${periodsHtml}</tr>`)
        $(`#camperRow${i}`).click(() => ca.scheduleAdjust.showCamper(sc));
    });
}

ca.scheduleAdjust.writeGroup = function() {
    $('#content').html(`Da group report`);
}

ca.scheduleAdjust.showCamper = function(sc) {
    $.getJSON(`/report_schedule_adjust_completed_achievements?camper=${sc.camper.key}`)
            .fail(() => window.alert('Completed Achievements Load failed'))
            .done(() => {
        $('#content').html(`
                <h3>${sc.camper.lastName}, ${sc.camper.firstName}</h3>
                <table>
                    <thead><tr>
                        <td>SM</td>
                        <td>TW</td>
                        <td>RF</td>
                        <td>Name</td>
                    </tr></thead>
                    <tbody id="achievementRows"></tbody>
                </table>`);
        ca.scheduleAdjust.data.achievements.forEach((achievement, i) => {
            $('#achievementRows').append(`<tr id="achievementRow${i}"><td></td><td></td><td></td><td>${achievement.name}</td></tr>`)
        });
    });
}
