/**
 * Created by Administrator on 2017/11/24.
 */

// 首页左侧菜单的鼠标悬浮和离开事件
$(".classify_name").mouseover(function () {
    $(this).next().slideDown(300)
});
$(".classify_name").parent().mouseleave(function () {
    $(this).children().next().slideUp(300)
})