$(document).ready(function(){
    $('.rating').rating({
        initialRating: 4,
        maxRating: 5
    });

    $('.rating').rating(
        'setting', 'onRate', function(value){
            $('#rating').val(value);
        }
    );
});
