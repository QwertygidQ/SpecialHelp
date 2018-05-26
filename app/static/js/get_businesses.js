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