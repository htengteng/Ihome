function logout() {
    $.get("/user/logout/", function(data){
        if (data.code == 200){
            location.href ='/user/login/'
        }
    })
}

$(document).ready(function(){
});
// $.get('//userinfo/',function (msg) {
//         $('#user-avatar').attr('src','/static/' + msg.data.avatar)
//         $('#user-name').text(msg.data.name)
//         $('#user-mobile').text(msg.data.phone)
//
//     });


$.get('/user/userinfo/',function (msg) {
        console.log(msg.data.avatar)
        $('#user-avatar').attr('src',msg.data.avatar)
        $('#user-name').text(msg.data.name)
        $('#user-mobile').text(msg.data.phone)

    });
