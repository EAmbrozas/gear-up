# Generated by Django 3.2.23 on 2023-11-19 10:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_auto_20231119_1012'),
    ]

    operations = [
        migrations.AlterField(
            model_name='brand',
            name='name',
            field=models.CharField(editable=False, max_length=254),
        ),
    ]
