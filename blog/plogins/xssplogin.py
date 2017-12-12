from bs4 import BeautifulSoup


def filter_xss(html_str):
    '''过滤xss攻击'''

   #定义合法标签
    valid_dict = {"p": ["id", "class"],
                  "img": ["id", "class","src","width","height"],
                  "a": ["id", "class", "href"],
                  "div": ["id", "class"],
                  "span": ["id", "class"],
                  "html": [],
                  "body": [],
                  "br": [],
                  "strong": [],
                  "b": [],
                  "h1": [],
                  "h2": [],
                  "h3": [],
                  "h4": [],

                  }
    #实例化对象
    soup = BeautifulSoup(html_str, "html.parser")  # soup  ----->  document

    #循环soup对象得到一个个标签对象
    for ele in soup.find_all():
        # 过滤非法标签
        if ele.name not in valid_dict:
            ele.decompose()  #删除非法标签
        # 过滤非法属性

        else:
            attrs = ele.attrs  #获取标签属性
            l = []
            for k in attrs:
                if k not in valid_dict[ele.name]:  #判断标签属性是否合法
                    l.append(k)

            for i in l:
                del attrs[i]    #删除不合法的标签属性


    return soup.decode()  #返回过滤后的字符串