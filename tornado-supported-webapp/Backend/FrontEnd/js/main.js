let host = "";
let supported_style = ["mosaic", "candy", "starry-night", "udnie"];
var cur_style = 0;

function adjust_layout() {
    let height = $(window).height();
    $("#full-container").css("height", Math.max(height.value, 1080).toString() + "px");
    if (height < 1080) {
        // not 1080
        $("#image-panel")
            .css("padding-top", Math.max(height / 1080 * 190, 10).toString() + "px");
        $("#claim").css("margin-top", Math.max(height / 1080 * 100, 10).toString() + "px");
    } else {
        $("#image-panel").css("padding-top", "190px");
        $("#claim").css("margin-top", "100px");
    }
}

function upload_image() {
    let frame = captureVideoFrame("input-camera", 'jpeg');
    let formData = new FormData();
    formData.append("content-image", frame.blob, "content-image.jpeg");
    formData.append("model-name", supported_style[cur_style]);
    $.ajax({
        url: host + "/style-transfer-realtime",
        method: "POST",
        data: formData,
        processData: false,
        contentType: false,
        cache: false,
        success: function (data) {
            $("#output-image > img").get(0).src =
                "data:image/jpeg;base64," + data;
        },
        complete: function () {
            upload_image()
        }
    });
}

function hideInstructions() {
    $(".instruction").animate({opacity: 0}, 3000)
}

function config_camera() {
    let constraint = {
        audio: false,
        video: {width: 512, height: 512}
    };

    navigator.mediaDevices.getUserMedia(constraint).then(function (stream) {
        let video = $("#input-camera").get(0);
        video.srcObject = stream;
        video.onloadedmetadata = function (e) {
            video.play();
            hideInstructions();
            setTimeout(upload_image, 20);
        };
    }).catch(function (err) {
        console.log(err);
    })
}

function switchStyle() {
    cur_style =(cur_style + 1) % supported_style.length;
    let cover_url = "/static/data/" + supported_style[cur_style] + "-bg.jpg";
    document.getElementById("full-container").style.backgroundImage
        = "url('" + cover_url + "')";
}

$(document).ready(function() {
    adjust_layout();
    $(window).resize(adjust_layout);
    config_camera();
    $("#output-image > img").click(switchStyle);
});

