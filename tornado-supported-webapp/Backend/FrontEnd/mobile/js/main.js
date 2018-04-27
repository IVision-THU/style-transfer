
let host = "http://166.111.17.71:8000";

function hide_logo_show_function_panel() {
    let switchDuration = 3000;
    $("#welcome-panel").animate({opacity: 0}, switchDuration, function () {
        $("#welcome-panel").css("display", "none");
    });
    $("#function-area").animate({opacity: 1}, switchDuration);
}

function upload_image(blob) {
    let formData = new FormData();
    formData.append("content-image", blob, "content-image.jpeg");
    $("#render-time > i").text("uploading");
    $.ajax({
        url: host + "/style-transfer",
        method: "POST",
        data: formData,
        processData: false,
        contentType: false,
        cache: false,
        success: function (data) {
            data = $.parseJSON(data);
            document.getElementById("display-img").src = host + data["image_url"];
            $("#render-time > i").text(data["process_time"] + "s");

            let btn = $("#take-photo");
            btn.prop("disabled", false);
            btn.css("opacity", 1);
        },
        error: function (e) {
            $("#render-time > i").text("Error occurs");
        }
    });
}

function config_camera() {
    let uploader = document.createElement("input");
    uploader.type = "file";
    uploader.accept = "image/*";

    uploader.onchange = function () {
        let reader = new FileReader();
        reader.onload = function (e) {
            let image = document.getElementById("display-img");
            image.src = e.target.result;
        };
        reader.readAsDataURL(uploader.files[0]);
        upload_image(uploader.files[0]);
    };

    $("#take-photo").click(function (e) {
        let btn = $("#take-photo");
        btn.prop("disabled", true);
        btn.css("opacity", 0.2);
        uploader.click();
    });
}

function do_init() {
    hide_logo_show_function_panel();
    config_camera();
}


$(document).ready(function () {
    console.log("ready");
    setTimeout(do_init, 2000);
});