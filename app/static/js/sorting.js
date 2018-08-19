let geolocation = {};

function geolocation_success(position) {
    geolocation.status = "ok";
    geolocation.position = position;
}

function geolocation_failure(error) {
    geolocation.status = "error";
    switch(error.code) {
        case error.PERMISSION_DENIED:
            geolocation.desc = "Please allow geolocation on this website.";
            break;
        case error.POSITION_UNAVAILABLE:
            geolocation.desc = "User location is unavailable. Please try again later.";
            break;
        case error.TIMEOUT:
            geolocation.desc = "Timed out on a geolocation request. Please try again later.";
            break;
        default:
            geolocation.desc = "Unknown geolocation error. Please try again later.";
    }
}

if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(geolocation_success, geolocation_failure);
}
else {
    geolocation.status = "error";
    geolocation.desc = "Your browser does not support geolocation. Please update it or use a different browser."
}

function hide_options() {
    $("#distance_div").hide();
    $("#rating_div").hide();
}

function reset_options() {
    $("#distance_input").val("0");
    $("#rating_input").rating("rate", "");
}

function error_message(message) {
    const msg = $(
        "<div class=\"alert alert-danger alert-dismissible fade show\" role=\"alert\">" +
            "<h4 class=\"alert-heading\">Error</h4>" +
            "<button type=\"button\" class=\"close\" data-dismiss=\"alert\">" +
                "<span>&times;</span>" +
            "</button>" +
            message +
        "</div>"
    ).hide();
    msg.fadeIn().appendTo("#message_div");
}

function draw_businesses(json) {
    $.ajax({
        url: "/get_businesses",
        type: "POST",
        contentType: "application/json",
        dataType: "json",
        data: JSON.stringify(json),
        timeout: 15000
    }).done(function(data){
        if (data.status === "error") {
            if (data.desc)
                error_message(data.desc);
            else
                error_message("Unknown error. Please try again later.");
        }
        else if (data.status !== "ok")
            error_message("Unknown error. Please try again later.");
        else {
            
        }
    }).fail(function (jqXHR, status, errorThrown) {
        if (status === "timeout")
            error_message("Timed out on your request. Please try again later.");
        else
            error_message("Failed to fetch data from the server. Please try again later.");
    });
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

    // TODO: translate error messages
    $("#sort_apply_button").click(function() {
        let type = $("#sort_type_dropdown").val();
        if (!["location", "alphabet", "rating", "date"].includes(type)) {
            error_message("Invalid sort type.")
            return;
        }

        let reverse = $("#reverse_checkbox").is(':checked');
        if (typeof(reverse) !== "boolean") {
            error_message("Invalid reverse checkbox value.")
            return;
        }

        let json = {
            type: type,
            page: 1,
            reverse: reverse
        };
        if (type === "location") {
            if ($.isEmptyObject(geolocation)) {
                error_message("There is no geolocation data available yet. Try again in a moment.");
                return;
            }
            else if (geolocation.status === "error") {
                if (geolocation.desc)
                    error_message(geolocation.desc);
                else
                    error_message("Unknown geolocation error. Please try again later.");

                return;
            }
            else if (geolocation.status !== "ok") {
                error_message("Unknown geolocation error. Please try again later.");
                return;
            }

            json.lat = geolocation.position.coords.latitude;
            json.lon = geolocation.position.coords.longitude;

            let str_max_dist = $("#distance_input").val();
            let max_dist = parseInt(str_max_dist);
            if (str_max_dist.indexOf(".") != -1 || isNaN(max_dist) ||
                    max_dist < 0 || max_dist > 50000) {
                error_message("Invalid maximum distance value.");
                return;
            }
            json.max_dist = max_dist;
        }
        else if (type === "rating") {
            let min_rating = parseInt($("#rating_input").val());
            if (isNaN(min_rating) || min_rating < 0 || min_rating > 5) {
                error_message("Invalid minumum rating value.");
                return;
            }
            json.min_rating = min_rating;
        }

        draw_businesses(json);
    });
});
