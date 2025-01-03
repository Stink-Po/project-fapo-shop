# Generated by Django 5.1.1 on 2024-12-27 18:10

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('shop', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('Send', 'در حال ارسال'), ('Processing', 'درحال پردازش'), ('Fail', 'ناموفق')], default='Processing', max_length=10)),
                ('track_id', models.CharField(blank=True, max_length=30, null=True)),
                ('first_name', models.CharField(max_length=250)),
                ('last_name', models.CharField(max_length=250)),
                ('phone', models.CharField(blank=True, max_length=100, null=True)),
                ('address', models.CharField(max_length=250, null=True)),
                ('email', models.EmailField(blank=True, max_length=254, null=True)),
                ('postal_code', models.CharField(max_length=20)),
                ('province', models.CharField(blank=True, max_length=255, null=True)),
                ('city', models.CharField(max_length=250)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('discount_code', models.CharField(blank=True, max_length=35, null=True)),
                ('post_follow_up', models.CharField(blank=True, max_length=100, null=True)),
                ('discount_amount', models.PositiveIntegerField(default=0)),
                ('paid', models.BooleanField(default=False)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='OrderItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('color', models.CharField(blank=True, max_length=255, null=True)),
                ('price', models.PositiveIntegerField(default=0)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('discount', models.PositiveIntegerField(default=0)),
                ('color_obj', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='shop.productcolor')),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='items', to='orders.order')),
                ('product', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_items', to='shop.product')),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timestamp', models.DateTimeField(blank=True, null=True)),
                ('card_number', models.CharField(blank=True, max_length=50, null=True)),
                ('status', models.CharField(blank=True, max_length=150, null=True)),
                ('amount', models.PositiveIntegerField(blank=True, default=0, null=True)),
                ('track_id', models.CharField(blank=True, max_length=30, null=True)),
                ('ref_number', models.CharField(blank=True, max_length=150, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('result', models.CharField(blank=True, max_length=250, null=True)),
                ('message', models.TextField(blank=True, null=True)),
                ('order', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment', to='orders.order')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payment', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='order',
            index=models.Index(fields=['-created'], name='orders_orde_created_743fca_idx'),
        ),
    ]
