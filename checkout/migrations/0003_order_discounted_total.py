# Generated by Django 3.2 on 2023-12-16 19:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0002_auto_20231207_1902'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='discounted_total',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
    ]
