# Generated by Django 3.2.9 on 2021-12-03 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('proxy_api', '0002_alter_proxy_proxy_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='proxy',
            name='proxy_id',
        ),
        migrations.AddField(
            model_name='proxy',
            name='id',
            field=models.BigAutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
    ]
