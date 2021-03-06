function hrefBack() {
    history.go(-1);
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function decodeQuery() {
    var search = decodeURI(document.location.search);
    return search.replace(/(^\?)/, '').split('&').reduce(function (result, item) {
        values = item.split('=');
        result[values[0]] = values[1];
        return result;
    }, {});
}

function showErrorMsg(msg) {
    $(".popup>p").html(msg);
    $('.popup_con').fadeIn('fast', function () {
        setTimeout(function () {
            $('.popup_con').fadeOut('fast', function () {
            });
        }, 1000)
    });
}

$(document).ready(function () {
    $.get("/order/checklogin", function (data) {
        if ("00" != data.code) {
            location.href = "/login.html";
        }
    }, "json");
    $(".input-daterange").datepicker({
        format: "yyyy-mm-dd",
        startDate: "today",
        language: "zh-CN",
        autoclose: true
    });
    $(".input-daterange").on("changeDate", function () {
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();
        var sd = new Date(startDate);
        var ed = new Date(endDate);
        days = (ed - sd) / (1000 * 3600 * 24) + 1;
        var price = $(".house-text>p>span").html();
        var amount = (days-1) * parseFloat(price);
        $(".order-amount>span").html(amount.toFixed(2) + "(共" + (days-1) + "晚)");

    });
    var queryData = decodeQuery();
    var houseId = queryData["hid"];
    $.get("/house/info?house_id=" + houseId, function (data) {
        if ("00" == data.code) {
            $(".house-info>img").attr("src", data.data.images[0]);
            $(".house-text>h3").html(data.data.title);
            $(".house-text>p>span").html((data.data.price / 100.0).toFixed(0));
        }
    }, "json");
    $(".submit-btn").on("click", function (e) {
        var startDate = $("#start-date").val();
        var endDate = $("#end-date").val();
        var sd = new Date(startDate);
        var ed = new Date(endDate);
        days = (ed - sd) / (1000 * 3600 * 24);
        console.log(days);
        if( days == 0){
               return false;
        }
        if ($(".order-amount>span").html()) {
            $(this).prop("disabled", true);
            var startDate = $("#start-date").val();
            var endDate = $("#end-date").val();
            var data = {
                "house_id": houseId,
                "start_date": startDate,
                "end_date": endDate
            };
            $.ajax({
                url: "/order/order",
                type: "POST",
                data: JSON.stringify(data),
                contentType: "application/json",
                dataType: "json",
                headers: {
                    "X-XSRFTOKEN": getCookie("_xsrf"),
                },
                success: function (data) {
                    if ("aa" == data.code) {
                        location.href = "/login.html";
                    } else if ("04" == data.code || "05" == data.code || "07" == data.code) {
                        showErrorMsg(data.msg);
                    } else if ("00" == data.code) {
                        location.href = "/orders.html";
                    }
                }
            });
        }
    });
})
