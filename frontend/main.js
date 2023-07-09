var url_prefix = "http://localhost:8000/";

var usertype_array = ["用户", "管理员"];
var user_status_array = {
    'queueing': '排队',
    'charging': '充电',
    'idle': '空闲',
}
var charge_type_array = ['慢充', '快充']

function check_login() {
    return localStorage.getItem("charger-id") != null;
}

function get_user_id() {
    let id = localStorage.getItem("charger-id");
    if (id == null) {
        return 'None'
    } else {
        return id;
    }
}

function get_user_type() {
    let type = localStorage.getItem("charger-usertype");
    if (type == null) {
        return -1;
    } else {
        return parseInt(type);
    }
}

function is_admin() {
    let type = localStorage.getItem("charger-usertype");
    if (type == null || parseInt(type) == 0) {
        return false;
    } else {
        return true;
    }
}


$(document).ready(function () {
    if (check_login()) {
        let username = localStorage.getItem("charger-id");
        let usertype = localStorage.getItem("charger-usertype");

        $("#span-username").text(usertype_array[usertype] + ": " + username);
        $("#button-logout").show();
    }
});

function login(id, password, is_admin) {
    $.ajax({
        type: "POST",
        url: url_prefix + "user/login/",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            id: id,
            password: password,
            is_admin: is_admin
        }),
        // dataType: "json",
        success: function (data) {
            localStorage.setItem("charger-id", id);
            localStorage.setItem("charger-usertype", is_admin);
            window.location.reload();
        },
        error: function (data) {
            mdui.snackbar({
                message: "登录失败",
                position: "right-top"
            });
        }
    });
}

function register(id, password, is_admin) {
    $.ajax({
        type: "POST",
        url: url_prefix + "user/register/",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            id: id,
            password: password,
            is_admin: is_admin
        }),
        // dataType: "json",
        success: function (data) {
            //localStorage.setItem("charger-id", username);
            //localStorage.setItem("charger-usertype", is_admin);
            window.location.href = 'login.html';
        },
        error: function (data) {
            mdui.snackbar({
                message: "注册失败",
                position: "right-top"
            });
        }
    });
}

function get_user_info(id) {
    var res = null;
    $.ajax({
        type: "GET",
        url: url_prefix + "user/info/",
        data: {
            id: id
        },
        async: false,
        dataType: "json",
        success: function (data) {
            res = data;
        },
        error: function (data) {
            mdui.snackbar({
                message: "查询失败",
                position: "right-top"
            });
        }
    });

    if (res != null) {
        return res;
    }
}

function display_user_info(data) {
    $('#span-user-query-status').text(user_status_array[data.status]);
    $('#span-user-query-queue-number').text(data.queue_number);
    $('#span-user-query-waiting').text(data.waiting_in_front);
    let i = 0;
    for (i = 0; i < data['bills'].length; i++) {
        let tr = $('<tr></tr>');
        tr.append($('<td></td>').text(data['bills'][i]['bill_id']));
        tr.append($('<td></td>').text(data['bills'][i]['time']));
        tr.append($('<td></td>').text(data['bills'][i]['pile_id']));
        tr.append($('<td></td>').text(data['bills'][i]['volume']));
        tr.append($('<td></td>').text(data['bills'][i]['duration']));
        tr.append($('<td></td>').text(data['bills'][i]['begin_time']));
        tr.append($('<td></td>').text(data['bills'][i]['end_time']));
        tr.append($('<td></td>').text(data['bills'][i]['charging_fee']));
        tr.append($('<td></td>').text(data['bills'][i]['service_fee']));
        tr.append($('<td></td>').text(data['bills'][i]['overall']));
        $('#tbody-user-query').append(tr);
    }
    mdui.mutation()
}

function button_click_login() {
    let id = $("#input-id").val();
    let password = $("#input-password").val();
    let is_admin = $("#input-is-admin").is(":checked") ? 1 : 0;

    login(id, password, is_admin);
}

function button_click_register() {
    let id = $("#input-id").val();
    let password = $("#input-password").val();
    let is_admin = $("#input-is-admin").is(":checked") ? 1 : 0;

    register(id, password, is_admin);
}

function button_click_logout() {
    localStorage.removeItem("charger-id");
    localStorage.removeItem("charger-usertype");
    window.location.reload();
}

function button_click_charge() {
    $.ajax({
        type: "POST",
        url: url_prefix + "request/",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            id: get_user_id(),
            charge_volume: parseInt($("#input-charge-volume").val()),
            fast_charge: $("#input-charge-fast").is(":checked") ? 1 : 0
        }),
        dataType: "json",
        success: function (data) {
            mdui.snackbar({
                message: "请求成功",
                position: "right-top"
            });
        },
        error: function (data) {
            mdui.snackbar({
                message: "请求失败",
                position: "right-top"
            });
        }
    });
}

function button_click_modify_charge() {
    $.ajax({
        type: "POST",
        url: url_prefix + "request/modify/",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            id: get_user_id(),
            charge_volume: ($("#input-modify-charge-volume").val()),
            type_choice: $("#input-modify-charge-type").val(),
        }),
        dataType: "json",
        success: function (data) {
            mdui.snackbar({
                message: "修改成功",
                position: "right-top"
            });
        },
        error: function (data) {
            mdui.snackbar({
                message: "修改失败",
                position: "right-top"
            });
        }
    });
}

function button_click_cancel_charge() {
    $.ajax({
        type: "POST",
        url: url_prefix + "request/end/",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            id: get_user_id(),
        }),
        // dataType: "json",
        success: function (data) {
            mdui.snackbar({
                message: "取消成功",
                position: "right-top"
            });
        },
        error: function (data) {
            mdui.snackbar({
                message: "取消失败",
                position: "right-top"
            });
        }
    });
}

function start_time() {
    $.ajax({
        type: "POST",
        url: url_prefix + "time/start/",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({}),
        dataType: "json",
        success: function (data) {
            mdui.snackbar({
                message: "请求成功",
                position: "right-top"
            });
        },
        error: function () {
            mdui.snackbar({
                message: "请求失败",
                position: "right-top"
            });
        }
    });
}

function pause_time() {
    $.ajax({
        type: "POST",
        url: url_prefix + "time/pause/",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({}),
        dataType: "json",
        success: function (data) {
            mdui.snackbar({
                message: "请求成功",
                position: "right-top"
            });
        },
        error: function () {
            mdui.snackbar({
                message: "请求失败",
                position: "right-top"
            });
        }
    });
}

function set_time() {
    $.ajax({
        type: "GET",
        url: url_prefix + "time/set/",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            set_time_sec: $("#input-set-time").val()
        }),
        dataType: "json",
        success: function (data) {
            mdui.snackbar({
                message: "请求成功",
                position: "right-top"
            });
        },
        error: function (data) {
            mdui.snackbar({
                message: "请求失败",
                position: "right-top"
            });
        }
    });
}


function get_admin_info() {
    let res = null
        $.ajax({
        type: "GET",
        url: url_prefix + "pile/admin/",
        data: {},
        dataType: "json",
        async: false,
        success: function (data) {
            res = data
            //callback(data);
        },
        error: function (data) {
            mdui.snackbar({
                message: "查询失败",
                position: "right-top"
            });
        }
    });
    return res
}

function display_admin_info(data) {
    $('#span-admin-query-time').text(data['time']);
    $('#span-admin-query-time-speed').text(data['time_speed']);

    let i = 0;
    for (i = 0; i < data['reports'].length; i++) {
        let tr = $('<tr></tr>');
        tr.append($('<td></td>').text(data['reports'][i]['pile_id']));
        tr.append($('<td></td>').text(data['reports'][i]['working']));
        tr.append($('<td></td>').text(data['reports'][i]['charging_count']));
        tr.append($('<td></td>').text(data['reports'][i]['charging_duration']));
        tr.append($('<td></td>').text(data['reports'][i]['charging_volume']));
        tr.append($('<td></td>').text(data['reports'][i]['charging_fee']));
        tr.append($('<td></td>').text(data['reports'][i]['service_fee']));
        tr.append($('<td></td>').text(data['reports'][i]['overall']));

        $('#tbody-admin-query').append(tr);
    }
    mdui.mutation()
}


function button_click_startup_charger() {
    $.ajax({
        type: "POST",
        url: url_prefix + "pile/startup/",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            pile_id: parseInt($("#input-charger-id-start").val())
        }),
        // dataType: "json",
        success: function (data) {
            mdui.snackbar({
                message: "请求成功",
                position: "right-top"
            });
        },
        error: function (data) {
            mdui.snackbar({
                message: "请求失败",
                position: "right-top"
            });
        }
    });
}

function button_click_shutdown_charger() {
    $.ajax({
        type: "POST",
        url: url_prefix + "pile/shutdown/",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            pile_id: parseInt($("#input-charger-id-end").val())
        }),
        // dataType: "json",
        success: function (data) {
            mdui.snackbar({
                message: "请求成功",
                position: "right-top"
            });
        },
        error: function (data) {
            mdui.snackbar({
                message: "请求失败",
                position: "right-top"
            });
        }
    });
}


function get_charger_info() {
    $.ajax({
        type: "GET",
        url: url_prefix + "pile/queue/",
        data: {
            pile_id: parseInt($("#input-charger-id").val())            
        },
        dataType: "json",
        success: function (data) {
            display_charger_info(data);
        },
        error: function (data) {
            mdui.snackbar({
                message: "请求失败",
                position: "right-top"
            });
        }
    });
}

function print_chargers() {
    $.ajax({
        type: "GET",
        url: url_prefix + "stat/",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
        }),
        //dataType: "json",
        success: function (data) {
            mdui.snackbar({
                message: "打印成功",
                position: "right-top"
            });
        },
        error: function (data) {
            mdui.snackbar({
                message: "打印失败",
                position: "right-top"
            });
        }
    });
}


function display_charger_info(data) {
    let i = 0;
    $('#tbody-charger-query').text('')
    for (i = 0; i < data['items'].length; i++) {
        let tr = $('<tr></tr>');
        tr.append($('<td></td>').text(data['items'][i]['user_id']));
        tr.append($('<td></td>').text(charge_type_array[data['items'][i]['mode']]));
        tr.append($('<td></td>').text(data['items'][i]['amount']));
        tr.append($('<td></td>').text(data['items'][i]['begin_wait']));
        $('#tbody-charger-query').append(tr);
    }
    mdui.mutation()
}

function button_click_charger_queue() {
    get_charger_info();
}