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
            // TODO: set lat and lon properly
            json.lat = 0.0;
            json.lon = 0.0;
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
                    error_message("Unknown error.");
            }
            else if (data.status !== "ok") {
                error_message("Unknown error.");
            }
            else {
                // TODO: properly draw stuff
                console.log(data);
            }
        }).fail(function (jqXHR, status, errorThrown) {
            if (status === "timeout") {
                error_message("Timed out on your request. Please try again later.");
            }
            else {
                error_message("Failed to fetch data from the server. Please try again later.");
            }
        });
    });
});
