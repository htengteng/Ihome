//模态框居中的控制
function centerModals(){
    $('.modal').each(function(i){   //遍历每一个模态框
        var $clone = $(this).clone().css('display', 'block').appendTo('body');    
        var top = Math.round(($clone.height() - $clone.find('.modal-content').height()) / 2);
        top = top > 0 ? top : 0;
        $clone.remove();
        $(this).find('.modal-content').css("margin-top", top-30);  //修正原先已经有的30个像素
    });
}

function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}

function submit_order() {
    var orderId = $(".modal-accept").attr("order-id")
    var action = "accept"
    $.post('/order/update_order/',
        {'order_id':orderId,'action':action},
        function (msg) {
            // alert(msg.code)
            location.reload()
    });
}
function reject_order() {
    var orderId = $(".modal-accept").attr("order-id")
    var action = "reject"
    $.post('/order/update_order/',
        {'order_id':orderId,'action':action},
        function (msg) {
            // alert(msg.code)
            location.reload()
    });
}
$(document).ready(function(){
    $('.modal').on('show.bs.modal', centerModals);      //当模态框出现的时候
    $(window).on('resize', centerModals);
    $(".order-accept").on("click", function(){
        var orderId = $(this).parents("li").attr("order-id");
        $(".modal-accept").attr("order-id", orderId);

    });
    $(".order-reject").on("click", function(){
        var orderId = $(this).parents("li").attr("order-id");
        $(".modal-reject").attr("order-id", orderId);
    });
});