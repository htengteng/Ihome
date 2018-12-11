/**
 * Created by tengteng on 18-12-5.
 */
 $(document).ready(function() {
            $.post('/order/pay_success'+document.location.search,
                function (msg) {
                    if (msg.code == 200) {
                        $("#htt").html("您的订单已成功支付，支付交易号：" + msg.trade_id)
                    }
                    else {
                        alert("出现错误")
                    }
                });
        });