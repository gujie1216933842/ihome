function logout() {
    $.get("/profile/LogoutHandler", function(data){
        if ("00" == data.errcode) {
            location.href = "/";
        }
    })
}

$(document).ready(function(){
    $.get("/profile/LogoutHandler", function(data) {
        if ("aa" == data.code) {
            location.href = "/login.html";
        }
        else if ("00" == data.code) {
            $("#user-name").html(data.data.name);
            $("#user-mobile").html(data.data.mobile);
            if (data.data.avatar) {
                $("#user-avatar").attr("src", data.data.avatar);
            }
        }
    }, "json");
})