# Generated by Django 2.1.1 on 2019-05-22 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('media', '0006_auto_20190520_0909'),
    ]

    operations = [
        migrations.AddField(
            model_name='media',
            name='aeroplane',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='bench',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='bicycle',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='bird',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='boat',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='bus',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='car',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='cat',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='dog',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='fire_hydrant',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='motorbike',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='parking_meter',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='person',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='stop_sign',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='traffic_light',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='train',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='media',
            name='truck',
            field=models.IntegerField(default=0),
        ),
    ]
