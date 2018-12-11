$(function() {
    $(document).ready(function () {
        $(".auth-warn").show();
    });
    // $('.btn btn-success').click(function () {
    //     alert("你好呀")
    //
    // })
    $.get('/user/authinfo/', function (msg) {
        if (msg.code == '200') {
            if (msg.data.id_name) {
                $('.auth-warn').hide();
                $('#houses-list').show()
            } else {
                $('.wuth-warn').show();
                $('#houses-list').hide()
            }
        }
    });


    $.get('/house/housing/', function (msg) {
        if (msg.code == '200') {
            var house_str = '';
            for (var i = 0; i < msg.house_list.length; i++) {
                var house_li = '<li>>';
                house_li += '<div class="house-title"><h3>房屋ID:' + msg.house_list[i].id + '——' + msg.house_list[i].title + '</h3></div>';
                house_li += '<div class="house-content"><img alt="" src=' + msg.house_list[i].image + '><div class="house-text"><ul>';
                house_li += '<li>位于:' + msg.house_list[i].area + '</li>' +
                    '<li>价格：￥' + msg.house_list[i].price + '/晚</li>' +
                    '<li>发布时间：' + msg.house_list[i].create_time + '</li>' +
                    '<li><a href="/house/detail/?house_id=' + msg.house_list[i].id + '">查看详情</a></li>' +
                    '<li><a href="/house/delected/?house_id=' + msg.house_list[i].id + '">删除</a></li>';
                house_li += '</ul></div></div></li>';
                house_str += house_li
            }
            $('#houses-list').append(house_str)
        }
    });
    $('.fa fa-copyright').click(function () {
        alert('你好')

    });

//
// $post('/house/delecting',function (msg) {
//     if(msg.code == '200'){
//         location.reload()
//     }
})
