from django.db import models

# Create your models here.

# 用户
class User(models.Model):
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    email = models.EmailField()

    def __str__(self):
        return self.username

# 商品
class Goods(models.Model):
    name = models.CharField(max_length=100)
    price = models.FloatField()
    picture = models.FileField(upload_to='./upload/')
    desc = models.TextField()

    def __str__(self):
        return self.name


# 收货地址
class Address(models.Model):
    user = models.ForeignKey(User)  # 关联用户id
    address = models.CharField(max_length=50)  # 地址
    phone = models.CharField(max_length=15)  # 电话

    def __str__(self):
        return self.address


# 总订单
class Orders(models.Model):
    address = models.ForeignKey(Address)  # 关联送货地址id
    create_time = models.DateTimeField(auto_now=True)  # 创建时间
    status = models.BooleanField()  # 订单状态

    def __str__(self):
        return self.create_time


# 一个订单
class Order(models.Model):
    order = models.ForeignKey(Orders)  # 关联总订单id
    user = models.ForeignKey(User)  # 关联用户id
    goods = models.ForeignKey(Goods)  # 关联商品id
    count = models.IntegerField()  # 数量
