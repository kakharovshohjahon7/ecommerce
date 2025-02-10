from django.db import models
from decimal import Decimal
from django import forms
from phonenumber_field.modelfields import PhoneNumberField
import phonenumbers
from django.contrib.auth.models import User


# Create your models here.


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    my_order = models.PositiveIntegerField(default=0, blank=False, null=False)

    class Meta:
        abstract = True


class Category(BaseModel):
    title = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['my_order']
        verbose_name = 'category'
        verbose_name_plural = "categories"


class Product(BaseModel):
    class RatingChoice(models.IntegerChoices):
        ONE = 1
        TWO = 2
        THREE = 3
        FOUR = 4
        FIVE = 5

    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=14, decimal_places=2)
    discount = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='media/products/')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, related_name='products', null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1, null=True, blank=True)
    stock = models.BooleanField(default=False   )
    favorite = models.BooleanField(default=False)
    rating = models.PositiveIntegerField(choices=RatingChoice.choices, default=RatingChoice.ONE.value)

    @property
    def get_absolute_url(self):
        return self.image.url

    @property
    def discounted_price(self):
        self.new_price = self.price
        if self.discount > 0:
            self.new_price = Decimal(self.price) * Decimal((1 - self.discount / 100))
        return Decimal(self.new_price).quantize(Decimal('0'))

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['my_order']
        verbose_name = 'product'
        verbose_name_plural = 'products'

class Img(BaseModel):
    image = models.ImageField(upload_to='media/img/')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)

    @property
    def get_absolute_url(self):
        return self.image.url

class Specification(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name



class Attribute(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AttributeValue(models.Model):
    value = models.CharField(max_length=255)

    def __str__(self):
        return self.value


class ProductAttribute(models.Model):
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,related_name='product_attributes', null=True, blank=True)
    attribute = models.ForeignKey(Attribute, on_delete=models.SET_NULL, null=True, blank=True)
    attribute_value = models.ForeignKey(AttributeValue, on_delete=models.SET_NULL, null=True, blank=True)


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    shipping_address = models.TextField()
    billing_address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Order(BaseModel):
    full_name = models.CharField(max_length=255, null=True, blank=True)
    phone_number = PhoneNumberField(region="UZ")
    quantity = models.PositiveIntegerField(default=1)
    order_date = models.DateTimeField(auto_now_add=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'{self.full_name} => {self.phone_number}'

class Comment(BaseModel):
    full_name = models.CharField(max_length=255, null=True, blank=True)
    email = models.EmailField()
    content = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                    related_name='comments',
                                    null=True, blank=True)
    is_negative = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.full_name} => {self.created_at}'

    class Meta:
        ordering = ['-created_at']

    def calculate_total_price(self):
        self.total_price = self.product.price * self.quantity
        self.save()

    def is_product_available(self):
        if self.product.is_available():
            return True
        return False