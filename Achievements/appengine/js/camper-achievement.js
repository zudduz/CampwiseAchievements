var ca = ca || {};
ca.sa = ca.sa || {};

ca.sa.data = sessionStorage.caData ? JSON.parse(sessionStorage.caData) : {};
ca.sa.init = function() {
    $('#content').text('Loading...');
    $.getJSON('/report_schedule_adjust_json' + window.location.search)
            .done(ca.sa.campersLoaded)
            .fail(() => window.alert('Camper Load failed'));
};

ca.sa.campersLoaded = function(data) {
    ca.sa.data = data;
    sessionStorage.caData = JSON.stringify(data);
    let camperKeys = [];
    data.campers = {};
    data.scheduleCampers.forEach(sc => {
        sc.completedAchievements = [];
        sc.periods = [];
        data.periods.forEach((period, i) => {
            sc.periods[i] = sc.sessionAchievements.find(campA => campA.period == period);
        });
        sc.sessionAchievements = undefined;
        sc.periods.forEach(campA => {
            if (campA) {
                ca.sa.initializeCamperAchievement(campA)
                if(campA.cabin) {
                    sc.camper.cabin = campA.cabin;
                }
            }
        });
        data.campers[sc.camper.key] = sc;
        camperKeys.push(sc.camper.key)
    });
    ca.sa.writeAlphabetical();

    let pageSize = 50;
    for (let i = 0; i < camperKeys.length; i += pageSize) {
        $.ajax({
            dataType: 'json',
            method: 'POST',
            url: '/report_schedule_adjust_completed_achievements',
            data: {camperKeys: camperKeys.slice(i, i + pageSize)}})
                .done(ca.sa.completedLoaded)
                .fail(() => window.alert(`Completed Achievement Load page ${i} failed`));
    }
}

ca.sa.initializeCamperAchievement = function(campA) {
    if(campA) {
        campA.achievement = ca.sa.data.achievements.find(a => a.key == campA.achievementKey);
    }
}

ca.sa.completedLoaded = function(data) {
    data.completedAchievements.forEach(compA => {
        if (compA.sessionKey != ca.sa.data.session.key) {
            ca.sa.data.campers[compA.camperKey].completedAchievements.push(compA);
        }
    });
}

ca.sa.writeAlphabetical = function() {
    let data = ca.sa.data;
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
        $(`#camperRow${i}`).click(() => ca.sa.showCamper(sc));
    });
}

ca.sa.writeGroup = function() {
    $('#content').html(`Da group report`);
}

ca.sa.showCamper = function(sc) {
    $('#content').html(`
            <h3>${sc.camper.lastName}, ${sc.camper.firstName} (${sc.camper.cabin})</h3>
            <table>
                <thead><tr>
                    <td>SM</td>
                    <td>TW</td>
                    <td>RF</td>
                    <td>Name</td>
                </tr></thead>
                <tbody id="achievementRows"></tbody>
            </table>`);
    ca.sa.data.achievements.forEach((achievement, i) => {
        let completed = sc.completedAchievements.some(
                (compA) => compA.passed && compA.sessionKey != ca.sa.data.session.key && compA.achievementKey == achievement.key);
        
        let periodsHtml = '';
        ca.sa.data.periods.forEach(period => {
            scheduled = sc.periods.some((compA) => compA && compA.period == period && compA.achievementKey == achievement.key);
            periodsHtml += `<td
                class="achievementCheck ${scheduled ? 'scheduled' : ''}"
                data-scheduled="${scheduled}"
                data-period="${period}"
                data-achievement="${achievement.key}">`;
            if (scheduled) {
                periodsHtml += '<img src="/images/checkmark.png" height="18"/>';
            }
            periodsHtml += '</td>'
        });
        $('#achievementRows').append(`
                <tr class="${completed ? 'completed' : 'needed'}" id="achievementRow${i}">
                    ${periodsHtml}<td>${achievement.name}</td>
                </tr>`)
    });
    $('td.achievementCheck').click(cell => {
        cell = $(cell.delegateTarget)
        scheduled = cell.data('scheduled');
        achievementKey = cell.data('achievement');
        period = cell.data('period');

        $.ajax({
            dataType: 'json',
            method: 'POST',
            url: '/report_schedule_adjust_check',
            data: {
                scheduled: cell.data('scheduled'),
                achievementKey: cell.data('achievement'),
                period: cell.data('period'),
                camperKey: sc.camper.key,
                sessionKey: ca.sa.data.session.key,
                cabin: sc.camper.cabin,
            }
        }).done(data => {
            periodIndex = ca.sa.data.periods.findIndex((p) => p == period);
            sc.periods[periodIndex] = data.camperAchievement;
            ca.sa.initializeCamperAchievement(sc.periods[periodIndex]);
            ca.sa.showCamper(sc);
        }).fail(() => window.alert(`Unable to save schedule update`));
    });
}

