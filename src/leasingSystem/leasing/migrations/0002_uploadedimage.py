# Generated by Django 3.2.16 on 2022-12-18 10:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leasing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UploadedImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='', verbose_name='Uploaded image')),
            ],
        ),
    ]
