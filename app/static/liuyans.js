$(document).ready(function () {
    $('.nav-tabs li').click(function () {
        $(this).addClass('active').siblings('li:not(".disabled")').removeClass('active');
        $('.nav-tabs .disabled').removeClass('active');
    })
})