$(document).ready(function(){
    $.get("/profile/AuthHandler", function(data){
        if ("aa" == data.code) {
            location.href = "/login.html";
        } else if ("00" == data.code) {
            if ("" == data.data.real_name || "" == data.data.id_card || null == data.data.real_name || null == data.data.id_card) {
                $(".auth-warn").show();
                return;
            }
            $.get("/house/myhouse", function(result){
                $("#houses-list").html(template("houses-list-tmpl", {houses:result.data}));
            });
        }
    });
})