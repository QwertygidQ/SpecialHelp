$(document).ready(function(){
    $('.input-disallowed.rating').rating('disable');

    $('.input-allowed.ui.rating').rating(
        'setting', 'onRate', function(value){
            $('#rating').val(value);
        }
    );
});
