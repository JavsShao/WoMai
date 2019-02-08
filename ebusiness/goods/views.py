from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response, get_object_or_404

from goods.forms import UserForm, LoginForm

# Create your views here.
# 用户注册
from goods.models import User, Address, Goods
from goods.util import Util


def register(request):
    if request.method == 'POST':    # 判断表单是否提交状态
        uf = UserForm(request.POST) # 判断表单变量
        if uf.is_valid():           # 判断表单数据是否正确
            # 获取表单
            username = (request.POST.get('username')).strip()   # 获取用户名信息
            password = (request.POST.get('password')).strip()   # 获取密码信息
            email = (request.POST.get('email')).strip()         # 获取Email信息

            # 查找数据库中存在相同的用户名
            user_list = User.objects.filter(username=username)
            if user_list:
                # 如果存在,就报'用户名已经存在！', 并且回到注册页面
                return render_to_response('register.html', {'uf':uf, "error":"用户名已经存在！"})
            else:
                # 否则将表单写入数据库
                user = User()
                user.username = username
                user.password = password
                user.email = email
                user.save()
                # 返回登录页面
                uf = LoginForm()
                return render_to_response('index.html', {'uf':uf})
    else:   # 如果不是表单提交状态, 就显示表单信息
        uf = UserForm()
    return render_to_response('register.html', {'uf':uf})

# 显示首页
def index(request):
    uf = LoginForm()
    return render_to_response('index.html', {'uf':uf})

# 用户登录
def login_action(request):
    if request.method == 'POST':
        uf = LoginForm(request.POST)
        if uf.is_valid():
            # 寻找名为username和password的POST参数,而且如果参数没有提交,就返回一个空的字符串
            username = (request.POST.get('username')).strip()
            password = (request.POST.get('password')).strip()
            # 判断输入数据是否为空
            if username == '' or password =='':
                return render_to_response(request, "index.html", {'uf':uf, "error":"用户名和密码不能为空！"})
            else:
                # 判断用户名和密码是否正确
                user = User.objects.filter(username=username, password=password)
                if user:
                    response = HttpResponseRedirect('/goods_view/')
                    # 登录成功后跳转查看商品信息
                    request.session['username'] = username  # 将session信息写到服务器
                    return response
                else:
                    return render(request, "index.html", {'uf':uf, "error":'用户名或者密码错误！'})
        else:
            uf = LoginForm()
        return render_to_response('index.html', {'uf':uf})

def user_info(request):
    # 检查用户是否登录
    util = Util()
    username = util.check_user(request)
    # 如果没有登录,就跳转到首页
    if username == "":
        uf = LoginForm()
        return render(request, "index.html", {'uf':uf, "error":"请登录后再进入！"})
    else:
        # cont为当前购物车商品的数量
        count = util.cookies_count(request)
        # 获取登录用户信息
        user_list = get_object_or_404(User, username=username)
        # 获取登录用户收货地址的所有信息
        address_list = Address.objects.filter(user_id=user_list.id)
        return render(request, 'view_user.html', {"user":username,"user_info":user_list, "address":address_list, "count":count})

def chage_password(request):
    '''
    修改用户密码
    :param request:
    :return:
    '''
    util = Util()
    username = util.check_user(request)
    if username == "":
        uf = LoginForm()
        return render(request, "index.html", {'uf':uf, "error":"请登录后再进入"})
    else:
        count = util.cookies_count(request)
    # 获得当前登录用户的用户信息
    user_info = get_object_or_404(User, username=username)
    # 如果是提交表单, 就获取表单信息, 并且进行表单信息验证
    if request.method == 'POST':
        # 获取旧密码
        oldpassword = (request.POST.get("oldpassword", "")).strip()
        # 获取新密码
        newpassword = (request.POST.get("newpassword", "")).strip()
        # 获取新密码的确认密码
        checkpassword = (request.POST.get("checkpassword", "")).strip()
        # 如果旧密码不正确, 就报错误信息, 不允许修改
        if oldpassword != user_info.password:
            return render(request, "change_password.html", {'user':username, 'error':'原密码不正确, 请确定后重新输入！', 'count':count})
        # 如果旧密码与新密码相同,就报错误信息, 不允许修改
        elif oldpassword == newpassword:
            return render(request, "change_password.html", {'user':username, 'error':'新密码与旧密码相同,请重新输入！', 'count':count})
        # 如果新密码与确认密码不同,报错
        elif newpassword != checkpassword:
            return render(request, 'change_password.html', {'user':username, 'error':'两次输入的密码不同！', 'count':count})
        else:
            # 否则修改成功
            User.objects.filter(username=username).update(password=newpassword)
            return render(request, "change_password.html", {'user':username, 'error':'密码修改成功！请牢记密码！', 'count':count})
    else:
        return render(request, "change_password.html", {'user':username, 'count':count})


# 商品管理部分
def goods_view(request):
    '''
    查看商品信息
    :param request:
    :return:
    '''
    util = Util()
    username = util.check_user(request)
    if username == "":
        uf = LoginForm()
        return render(request, "index.html", {'uf':uf, "error":"请登录后再进入！"})
    else:
        # 获得所有商品信息
        good_list = Goods.objects.all()
        # 获得购物车物品数量
        count = util.cookies_count(request)

        # 翻页操作
        paginator = Paginator(good_list, 5)
        page = request.GET.get('page')
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            contacts = paginator.page(1)
        return render(request, "goods_view.html", {"user":username, "goodss":contacts, "count":count})

