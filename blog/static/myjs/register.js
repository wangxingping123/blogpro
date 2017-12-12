/**
 * Created by Administrator on 2017/11/21.
 */
  //头像的预览功能
    $("#valid_file").change(function () {
      var ele_file = this.files[0];
        var reader = new FileReader();
        reader.readAsDataURL(ele_file);
        reader.onload = function () {
            $("#valid_img")[0].src = this.result
        }
    });

    $("#submit").click(function () {
        $(".error_user").html("");
        $(".error_pwd").html("");
        $(".error_pwd_repeat").html("");
        $(".error_email").html("");
        var formdata = new FormData();
        var portrait = $("input:file")[0].files[0];
        formdata.append("username", $(".username").val());
        formdata.append("password", $(".password").val());
        formdata.append("password_repeat", $(".password_repeat").val());
        formdata.append("email", $(".email").val());
        formdata.append("portrair", portrait);

        $.ajax({
            url: "/register/",
            type: "POST",
            headers: {"X-CSRFToken": $.cookie('csrftoken')},
            data: formdata,
            contentType: false,
            processData: false,
            success: function (data) {

                var data = JSON.parse(data);
                console.log(data["errors"]);
                if (data["flag"]) {
                    $(location).attr('href', 'http://127.0.0.1:8000/login/');
                }
                else {
                    //循环错误信息，在页面显示错误信息
                    $.each(data.errors,function (i,j) {
                        $("."+i).parent().next().html(j[0])

                    })

                }

            }


        })

    });
