# Generated by Django 5.1.3 on 2024-11-28 12:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vocab', '0002_category_alter_vocabulary_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='vocabulary',
            name='rating',
            field=models.IntegerField(default=0),
        ),
    ]
