function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $.get("/profile/AuthHandler", function (data) {
        if ("aa" == data.code) {
            location.href = "/login.html";
        }
        else if ("00" == data.code) {
            if (data.data.real_name && data.data.id_card) {
                $("#real-name").val(data.data.real_name);
                $("#id-card").val(data.data.id_card);
                $("#real-name").prop("disabled", true);
                $("#id-card").prop("disabled", true);
                $("#form-auth>input[type=submit]").hide();
            }
        }
    }, "json");
    $("#form-auth").submit(function (e) {
        e.preventDefault();
        if ($("#real-name").val() == "" || $("#id-card").val() == "") {
            $(".error-msg").show();
        }
        //var data = {};
        //$(this).serializeArray().map(function(x){data[x.name] = x.value;});
        //var jsonData = JSON.stringify(data);
        var real_name = $("#real-name").val();
        var id_card = $("#id-card").val();
        $.ajax({
            url: "/profile/AuthHandler",
            type: "POST",
            data: {real_name: real_name, id_card: id_card},
            //contentType: "application/json",
            dataType: "json",
            headers: {
                "X-XSRFTOKEN": getCookie("_xsrf")
            },
            success: function (data) {
                if ("00" == data.code) {
                    $(".error-msg").hide();
                    showSuccessMsg();
                    $("#real-name").prop("disabled", true);
                    $("#id-card").prop("disabled", true);
                    $("#form-auth>input[type=submit]").hide();
                }
            }
        });
    })

})

