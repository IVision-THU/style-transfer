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
    let last_upload_time = Date.now();

    $.ajax({
        url: "http://166.111.17.71:8000/style-transfer-realtime",
        method: "POST",
        data: formData,
        processData: false,
        contentType: false,
        cache: false,
        success: function (data) {
            $("#output-image > img").get(0).src =
                "data:image/jpeg;base64," + data;
            // let interval = Date.now() - last_upload_time;
            // if (interval < 50) {
            //     setTimeout(upload_image, 50 - interval);
            // } else {
            //     upload_image()
            // }
            upload_image()
        }
    });
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
            setTimeout(upload_image, 20);
        };
    }).catch(function (err) {
        console.log(err);
    })
}

$(document).ready(function() {
    adjust_layout();
    $(window).resize(adjust_layout);
    this.last_upload_time = Date.now();
    this.keep_uploading = true;
    config_camera();
});

