function get_cookie(name) {
    let value = '; ' + document.cookie;
    let parts = value.split('; ' + name + '=');
    if (parts.length == 2)
        return parts.pop().split(';').shift();
    else
        console.log(name + ' is not defined in the cookie!');
}

function get_translation(str) {
    const translations = {
        'ru': {
            'Notification': 'Уведомление',
            'Error': 'Ошибка',
            'Message': 'Сообщение'
        }
    }

    let locale = get_cookie('locale');
    let lang_translations = translations[locale];
    if (!lang_translations || !lang_translations[str])
        return str;
    else
        return lang_translations[str];
}

function show_message(category, message) {
    let alert_type, alert_heading;

    switch (category)
    {
        case 'message':
            alert_type = 'alert-info';
            alert_heading = get_translation('Notification');
            break;
        case 'error':
            alert_type = 'alert-danger';
            alert_heading = get_translation('Error');
            break;
        default:
            alert_type = 'alert-primary';
            alert_heading = get_translation('Message');
    }

    let html = `
    <div class="alert ` + alert_type + ` alert-dismissible fade show" role="alert">
        <h4 class="alert-heading">` + alert_heading + `</h4>
        <button type="button" class="close" data-dismiss="alert">
            <span>&times;</span>
        </button>` +
        get_translation(message) +
    `</div>`;
    $('#msg_div').append(html);
}

$(document).ready(function() {
    let geolocation = {};

    if (navigator.geolocation)
        navigator.geolocation.getCurrentPosition(success, error);
    else {
        geolocation['status'] = 'error';
        geolocation['error_type'] = 'GEOLOCATION_UNSUPPORTED';
    }

    function success(position) {
        geolocation['status'] = 'ok';
        geolocation['position'] = position;
    }

    function error(error) {
        geolocation['status'] = 'error';

        switch(error.code) {
            case error.PERMISSION_DENIED:
                geolocation['error_type'] = 'PERMISSION_DENIED';
                break;
            case error.POSITION_UNAVAILABLE:
                geolocation['error_type'] = 'POSITION_UNAVAILABLE';
                break;
            case error.TIMEOUT:
                geolocation['error_type'] = 'TIMEOUT';
                break;
            default:
                geolocation['error_type'] = 'UNKNOWN_ERROR';
                break;
        }
    }

    $('#radius_input').focusout(function() {
        // TODO: finish writing this function
    });

    $('#filter_apply').click(function() {
        let sort_type = $('.ui.dropdown').dropdown('get value').trim();
        let radius = $('#radius_input').val().trim();

        $.ajax({
            url: url,
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                sort_type: sort_type,
                radius: radius,
                geolocation: geolocation,
                page: page
            }),
            dataType: 'json',
            timeout: 30000
        }).done(function() {

        }).fail(function() {

        });
    });
});
