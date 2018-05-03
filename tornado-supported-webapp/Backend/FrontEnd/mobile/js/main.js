
let host = "";
let supported_style = ["mosaic", "candy", "starry-night", "udnie"];
var cur_style = 0;

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
    formData.append("model-name", supported_style[cur_style]);
    $("#render-time > i").text("uploading");
    $("#progress").css("display", "block");
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
            console.log(e);
            $("#render-time > i").text("Error occurs");
        },
        complete: function () {
            let progressBar = $("#progress");
            progressBar.css("width", "0");
            progressBar.css("display", "none");
        },
        xhr: function () {
            var xhr = $.ajaxSettings.xhr();
            xhr.upload.onprogress = function (e) {
                if (e.lengthComputable) {
                    $("#progress").css("width", e.loaded / e.total * 100 + "%");
                    console.log(e.loaded / e.total * 100);
                }
            };
            return xhr;
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
        document.body.onfocus = function () {
            document.body.onfocus = null;
            if (uploader.value.length === 0) {
                let btn = $("#take-photo");
                btn.prop("disabled", false);
                btn.css("opacity", 1);
            }
        }
    });
}

function switchStyle() {
    cur_style =(cur_style + 1) % supported_style.length;
    let cover_url = "/static/data/" + supported_style[cur_style] + "-mobile-bg.jpg";
    document.getElementById("full-container").style.backgroundImage
        = "url('" + cover_url + "')";
    $("#style-name").text(supported_style[cur_style])
}

function do_init() {
    hide_logo_show_function_panel();
    config_camera();

    $("#display-img").click(function (e) {
        let btn = $("#take-photo");
        if (!btn.prop("disabled")) {
            switchStyle();
        }
    });
}


$(document).ready(function () {
    console.log("ready");
    setTimeout(do_init, 2000);
});