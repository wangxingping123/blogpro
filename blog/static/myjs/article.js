// 给文章点推荐或反对的Ajax请求的juqery代码
$(".article_up_down").click(function () {
    var this_tag = this;
    if ($("#login_user").val()) {
        $.ajax({
            url: "/blog/article_up/",
            type: "POST",
            data: {
                "csrfmiddlewaretoken": $("[name=csrfmiddlewaretoken]").val(),
                "article_id": $("#article_id").val(),
                "up_or_down": $(this_tag).children().last().text()
            },
            success: function (data) {
                var data = JSON.parse(data);
                if (data["flag"]) {
                    var count = parseInt($(this_tag).children().first().text());
                    $(this_tag).children().first().html(count + 1);
                    $(this_tag).parent().children().last().html(data["point"]).css("color", "red").delay(3000).fadeOut().show()


                }
                else {
                    $(this_tag).parent().children().last().html(data["point"]).css("color", "red").delay(3000).fadeOut().show()
                }
            }


        })
    }
    else {
        $(this_tag).parent().children().last().html("你还没登录请<a href='/login/'>登录</a>")
    }
});


//提交文章评论的ajax请求的jquery代码
$("#sub_comment").click(function () {
    var textarea=$("#article_comment_content").val();
    if (textarea) {
        var comment_content;
        if (parent_comment_id){
            var index=textarea.indexOf("\n");//获取索引值
            comment_content=textarea.slice(index+1)//根据索引截取用户评论的内容
        }
        else{
            comment_content=textarea
        }
        $.ajax({
            url: "/blog/article_comment",
            type: "POST",
            data: {
                "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
                "article_id": $("#article_id").val(),
                "comment_content": comment_content,
                "parent_comment_id":parent_comment_id
            },
            success: function (data) {
                $("#article_comment_content").val('');
                var data = JSON.parse(data);
                var s = '<div><p><a href="/blog/' + data["username"] + '">' + data["username"] + '</a></p><p class="article_con">' + data["comment_content"] + '</p></div>';
                $(".commentlist").append(s);

            }

        })
    }
    else {
        alert("请输入评论内容")
    }
});


//给文章的评论点推荐或反对的ajax请求的jquery代码
$(".comment_func").click(function () {
    var this_tag = this;
    $.ajax({
        url: "/blog/comment_up_down",
        type: "POST",
        data: {
            "csrfmiddlewaretoken": $("[name='csrfmiddlewaretoken']").val(),
            "comment_id": $(this_tag).parent().parent().parent().children().first().val(),
            "up_or_down": $(this_tag).text()
        },
        success: function (data) {
            var data = JSON.parse(data);
            if (data["flag"]) {
                $(this_tag).html(data["count"]);
                $(this_tag).parent().parent().next().text(data["point"]).css("color", "red");

            }
            else {
                $(this_tag).parent().parent().next().text(data["point"]).css("color", "red");
            }

        }

    })

});

//给文章评论的回复添加ajax请求的jquery代码

var parent_comment_id=null;
$(".replay_comment").click(function () {

    if ($("#login_user").val()){

        $("#article_comment_content").val('@'+$(this).attr("parent_comment_username")+'\n')
        parent_comment_id=$(this).attr("parent_comment_id")

    }
    else{

        location.href="/login/"
    }

})
