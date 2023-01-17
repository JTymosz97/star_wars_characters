# Generated by Django 4.1.3 on 2023-01-14 16:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('characters_explorer', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='characters',
            name='characters_file',
        ),
        migrations.AddField(
            model_name='characters',
            name='file_name',
            field=models.CharField(default='', max_length=256, unique=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='characters',
            name='folder_path',
            field=models.CharField(default='', max_length=256),
            preserve_default=False,
        ),
    ]
