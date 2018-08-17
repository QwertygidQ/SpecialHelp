function hide_options() {
    $("#distance_div").hide();
    $("#rating_div").hide();
}

function reset_options() {
    $("#distance_input").val("0");
    $("#rating_input").rating("rate", "");
}

$(document).ready(function() {
    hide_options();

    $("#sort_type_dropdown").val("location");
    $("#distance_div").show();

    $("#sort_type_dropdown").on("change", function() {
        hide_options();
        reset_options();

        let selection = $(this).val();
        if (selection == "location") {
            $("#distance_div").show();
        }
        else if (selection == "rating") {
            $("#rating_div").show();
        }
    });
});
