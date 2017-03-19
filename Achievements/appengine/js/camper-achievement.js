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
    //sessionStorage.caData = JSON.stringify(data);

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

    data.achievementIndex = {};
    data.achievements.forEach((a, i) => data.achievementIndex[a.key] = i);

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
    ca.sa.rewriteReport = ca.sa.writeAlphabetical;
    let data = ca.sa.data;
    $('#content').html(`
            ${data.scheduleCampers.length} campers
            <table>
                <thead><tr><td>Camper Name</td>${ca.sa.periodsHeader()}</tr></thead>
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
    ca.sa.rewriteReport = ca.sa.writeGroup;
    let data = ca.sa.data;
    data.achievements.forEach(a => {
        a.periods = [];
        data.periods.forEach(p => a.periods.push([]));
    });
    data.scheduleCampers.forEach(sc => sc.periods.forEach(sessA => {
        if (sessA) {
            let achievement = data.achievements[ca.sa.data.achievementIndex[sessA.achievement.key]];
            achievement.periods[ca.sa.periodIndex(sessA.period)].push(sessA);
        }
    }));
    
    $('#content').html('');
    $('#content').append(`
            <b>Totals</b>
            <table>
                <thead><tr><td>Name</td>${ca.sa.periodsHeader()}</tr></thead>
                <tbody id="achievementTotals"></tbody>
            </table><br/><br/>`);
    data.achievements.forEach((a, i) => {
        let periodsHtml = `<td>${a.name}</td>`;
        data.periods.forEach((p, j) => periodsHtml += `<td>${a.periods[j].length}</td>`);
        $('#achievementTotals').append(`<tr>${periodsHtml}</tr>`);
    });
    data.achievements.forEach((a, i) => {
        let headerPeriodsHtml = '';
        data.periods.forEach((p, j) => {
            headerPeriodsHtml += `<td>${p} (${a.periods[j].length})</td>`;
        });
        $('#content').append(`
                <b>${a.name}</b>
                <table>
                    <thead><tr>${headerPeriodsHtml}</tr></thead>
                    <tbody id="camperRows${i}"></tbody>
                </table><br/><br/>`);
        let j = 0;
        while (a.periods.some(p => p[j])) {
            let periodsHtml = '';
            a.periods.forEach(p => {
                if (p[j]) {
                    let camper = data.campers[p[j].camperKey].camper;
                    periodsHtml += `
                        <td class="camper-cell" data-camper-key="${p[j].camperKey}">
                            ${camper.lastName}, ${camper.firstName}
                        </td>
                    `;
                } else {
                    periodsHtml += '<td></td>';
                }
            });
            $(`#camperRows${i}`).append(`<tr>${periodsHtml}</tr>`);
            j++;
        }
    });
    $('.camper-cell').click(event => {
        let camperKey = $(event.delegateTarget).data('camper-key');
        ca.sa.showCamper(ca.sa.data.campers[camperKey]);
    });
}

ca.sa.showCamper = function(sc) {
    $('#side-content').html(`
            <button id="closeCamper">Close camper</button><br/>
            <h3>${sc.camper.lastName}, ${sc.camper.firstName} (${sc.camper.cabin})</h3>
            <table>
                <thead><tr>${ca.sa.periodsHeader()}<td>Name</td>
                </tr></thead>
                <tbody id="achievementRows"></tbody>
            </table>`);
    $('#closeCamper').click(event => {
        $('#side-content').html('');
    });
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
    $('td.achievementCheck').click(event => {
        let cell = $(event.delegateTarget)
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
            let periodIndex = ca.sa.periodIndex(period);
            sc.periods[periodIndex] = data.camperAchievement;
            ca.sa.initializeCamperAchievement(sc.periods[periodIndex]);
            ca.sa.showCamper(sc);
            ca.sa.rewriteReport();
        }).fail(() => window.alert(`Unable to save schedule update`));
    });
}

ca.sa.periodIndex = function(period) {
    return ca.sa.data.periods.findIndex((p) => p == period);
}
ca.sa.periodsHeader = function() {
    let periodsHeader = '';
    ca.sa.data.periods.forEach(p => periodsHeader += `<td>${p}</td>`);
    return periodsHeader;
}
