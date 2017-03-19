var ca = ca || {};
ca.i = ca.i || {};

ca.i.navigateReport = function() {
}

ca.i.init = function() {
    $('.reportLink').click((event) => {
        location.href = $(event.delegateTarget).data('url') + '?session=' + $('#sessionList').val();
    });
};
