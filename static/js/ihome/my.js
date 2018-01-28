function logout() {
    $.get("/api/logout", function(data){
        if (0 == data.errcode) {
            location.href = "/";
        }
    })
}

$(document).ready(function(){
    $.get("/profile/ucenter", function(data) {
        if ("aa" == data.code) {
            location.href = "/login.html";
        }
        else if ("00" == data.errcode) {
            $("#user-name").html(data.data.name);
            $("#user-mobile").html(data.data.mobile);
            if (data.data.avatar) {
                $("#user-avatar").attr("src", data.data.avatar);
            }
        }
    }, "json");
})