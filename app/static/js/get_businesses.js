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
            'Message': 'Сообщение',
            'Your browser does not support geolocation.': 'Ваш браузер не поддерживает геолокацию.',
            'Please allow geolocation.': 'Пожалуйста, разрешите геолокацию.',
            'Your position is unavailable.': 'Ваша позиция недоступна.',
            'Geolocation request timed out.': 'Геолокационный запрос занял слишком много времени.',
            'Unknown geolocation error.': 'Неизвестная ошибка геолокации.'
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
    else
        show_message('error', 'Your browser does not support geolocation.');

    function success(position) {
        geolocation['status'] = 'ok';
        geolocation['position'] = position;
    }

    function error(error) {
        switch(error.code) {
            case error.PERMISSION_DENIED:
                show_message('error', 'Please allow geolocation.');
                break;
            case error.POSITION_UNAVAILABLE:
                show_message('error', 'Your position is unavailable.');
                break;
            case error.TIMEOUT:
                show_message('error', 'Geolocation request timed out.');
                break;
            default:
                show_message('error', 'Unknown geolocation error.');
                break;
        }
    }

    $('#radius_input').focusout(function() {
        // TODO: finish writing this function
    });

    $('#filter_apply').click(function() {
        let sort_type = $('#sort_by option:selected').text().trim();
        let radius = $('#radius').val().trim();

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
