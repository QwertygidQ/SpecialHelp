let geolocation = {};
let last_json = {};
let last_data = {};

function geolocation_success(position) {
    geolocation.status = "ok";
    geolocation.position = position;
}

function geolocation_failure(error) {
    geolocation.status = "error";
    switch (error.code) {
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
} else {
    geolocation.status = "error";
    geolocation.desc = "Your browser does not support geolocation. Please update it or use a different browser."
}

function hide_options() {
    $("#distance_div").hide();
    $("#rating_div").hide();
}

function reset_options() {
    $("#distance_input").val("0");
    $("#rating_input").rating("rate", "0");
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

function send_ajax(json) {
    $.ajax({
        url: "/get_businesses",
        type: "POST",
        contentType: "application/json",
        dataType: "json",
        data: JSON.stringify(json),
        timeout: 15000
    }).done(function(data) {
        if (data.status === "error") {
            if (data.desc)
                error_message(data.desc);
            else
                error_message("Unknown error. Please try again later.");
        } else if (data.status !== "ok")
            error_message("Unknown error. Please try again later.");
        else {
            if (!data.num_pages || !data.businesses || data.businesses.length < 1) {
                error_message("Got invalid data from the server.");
                return;
            }

            if (json.page >= 1 && json.page <= data.num_pages)
                draw_navigation(json.page, data.num_pages);
            else
                error_message("Page is out of range.");

            draw_businesses(data.businesses);

            last_json = json;
            last_data = data;
        }
    }).fail(function(jqXHR, status, errorThrown) {
        if (status === "timeout")
            error_message("Timed out on your request. Please try again later.");
        else
            error_message("Failed to fetch data from the server. Please try again later.");
    });
}

function draw_navigation(page, max_pages) {
    let min_page = 1,
        max_page = 1;
    let back_enabled = true,
        forward_enabled = true;

    if (max_pages < 5) {
        min_page = 1;
        max_page = max_pages;
    } else if (page - 2 < 1) {
        min_page = 1;
        max_page = 5;
    } else if (page + 2 > max_pages) {
        min_page = max_pages - 5 + 1;
        max_page = max_pages;
    } else {
        min_page = page - 2;
        max_page = page + 2;
    }

    let dom = "";

    if (min_page > 1) {
        dom +=
            "<li id=\"pag_beginning\" class=\"page-item page-link\">" +
            "&laquo;"+
            "</li>";
    }

    for (page = min_page; page <= max_page; ++page) {
        dom +=
            "<li id=\"" + page + "\" class=\"page-item page-link\">" +
            page +
            "</li>"
    }

    if (max_page < max_pages) {
        dom +=
            "<li id=\"pag_end\" class=\"page-item page-link\">" +
            "&raquo;" +
            "</li>";
    }

    $("#pagination_ul").empty();
    $(dom).appendTo("#pagination_ul");
}

function draw_businesses(businesses) {
    $("#businesses_div").empty();

    for (i = 0; i < businesses.length; ++i) {
        let business = businesses[i];

        if ([business.img, business.name, business.link, business.address,
                business.tags, business.rating
            ].includes(undefined)) {
            error_message("Got invalid data from the server.");
            return;
        }

        let dom =
            "<div class=\"card mb-3\">" +
            "<div class=\"card-body\">" +
            "<div class=\"row\">" +
            "<div class=\"col-md-2\">" +
            "<img " +
            "src=\"" + business.img + "\"" +
            "class=\"circular img-fluid small mx-auto d-block\"/>" +
            "</div>" +
            "<div class=\"col-md-10\">" +
            "<h2><a href=/b/" + business.link + ">" + business.name + "</a></h2>" +
            "<input " +
            "type= \"hidden\"" +
            "class=\"rating\"" +
            "value=\"" + business.rating + "\"" +
            "data-filled=\"fa fa-2x fa-star checked\"" +
            "data-empty=\"fa fa-2x fa-star\"" +
            "data-readonly/>" +
            "<div class=\"mt-2\">";

        $.each(business.tags, function(index, tag) {
            dom +=
                "<a " +
                "href=\"/t/" + tag + "?page=1\"" +
                "class=\"badge badge-pill badge-secondary mr-1\">" + tag + "</a>";
        });

        dom += "<p class=\"user-input smaller-text\">" + business.address + "</p>" +
            "</div>" +
            "</div>" +
            "</div>" +
            "</div>" +
            "</div>"

        $(dom).appendTo("#businesses_div");
        $("input").rating();
    }
}

$(document).ready(function() {
    send_ajax({
        type: "date",
        page: 1,
        reverse: false
    });

    hide_options();

    $("#sort_type_dropdown").val("location");
    $("#distance_div").show();

    $("#sort_type_dropdown").on("change", function() {
        hide_options();
        reset_options();

        let selection = $(this).val();
        if (selection == "location") {
            $("#distance_div").show();
        } else if (selection == "rating") {
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
            } else if (geolocation.status === "error") {
                if (geolocation.desc)
                    error_message(geolocation.desc);
                else
                    error_message("Unknown geolocation error. Please try again later.");

                return;
            } else if (geolocation.status !== "ok") {
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
        } else if (type === "rating") {
            let min_rating = parseInt($("#rating_input").val());
            if (isNaN(min_rating) || min_rating < 0 || min_rating > 5) {
                error_message("Invalid minumum rating value.");
                return;
            }
            json.min_rating = min_rating;
        }

        send_ajax(json);
    });

    $("#pagination_ul").on("click", "li", function () {
        let id = $(this).attr("id");
        let json = last_json;
        if (id === "pag_beginning")
            json.page = 1;
        else if (id === "pag_end")
            json.page = last_data.num_pages;
        else {
            json.page = parseInt(id);
            if (isNaN(json.page)) {
                error_message("Invalid page.")
                return;
            }
        }

        send_ajax(json);
    });
});
