# Generated by Django 3.2.4 on 2021-08-11 00:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_remove_student_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='image',
            field=models.ImageField(blank=True, upload_to='media'),
        ),
    ]
