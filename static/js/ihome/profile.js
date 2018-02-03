function showSuccessMsg() {
    $('.popup_con').fadeIn('fast', function() {
        setTimeout(function(){
            $('.popup_con').fadeOut('fast',function(){}); 
        },1000) 
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

$(document).ready(function () {
    $.get("/profile/ProfileShowEdit", function(data){
        if ("aa" == data.code) {
            location.href = "/login.html";
        }
        else if ("00" == data.code) {
            $("#user-name").val(data.data.nickname);
            if (data.data.avatar) {
                $("#user-avatar").attr("src", data.data.avatar);
            }
        }
    });
    $("#form-avatar").submit(function (e) {
        // 组织浏览器对于表单的默认行为
        e.preventDefault();
        $('.image_uploading').fadeIn('fast');
        var options = {
            url: "/profile/UploadHandler",
            method: "post",
            dataType: "json",
            headers: {
                "X-XSRFTOKEN": getCookie("_xsrf")
            },
            success: function (data) {
                if ("00" == data.code) {
                    $('.image_uploading').fadeOut('fast');
                    $("#user-avatar").attr("src", data.data)
                } else if ("aa" == data.code) {
                    location.href = "/login.html";
                }
            }
        };
        $(this).ajaxSubmit(options);
    });
    $("#form-name").submit(function(e){
        e.preventDefault();
        //var data = {};
        //$(this).serializeArray().map(function(x){data[x.name] = x.value;});
        //var jsonData = JSON.stringify(data);
        var name = $("#user-name").val();
        $.ajax({
            url:"/profile/NickNameEdit",
            type:"post",
            //data: jsonData,
            data: {name:name},
            //contentType: "application/json", 注:这段代码一定要注释,否则ajax请求会报400错误
            dataType: "json",
            headers:{
                "X-XSRFTOKEN":getCookie("_xsrf"),
            },
            success: function (data) {
                if ("00" == data.code) {
                    $(".error-msg").hide();
                    showSuccessMsg(); // 展示保存成功的页面效果
                } else if ("cc" == data.code) {
                    $(".error-msg").show();
                } else if ("aa" == data.code) { // 4101代表用户未登录，强制跳转到登录页面
                    location.href = "/login.html";
                }
            }
        });
    })
})

