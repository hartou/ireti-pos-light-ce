# Generated for I18N-015: localized product and department names

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='name_fr',
            field=models.CharField(blank=True, help_text='French translation of product name', max_length=125, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='name_es',
            field=models.CharField(blank=True, help_text='Spanish translation of product name', max_length=125, null=True),
        ),
        migrations.AddField(
            model_name='department',
            name='department_name_fr',
            field=models.CharField(blank=True, help_text='French translation of department name', max_length=32, null=True),
        ),
        migrations.AddField(
            model_name='department',
            name='department_name_es',
            field=models.CharField(blank=True, help_text='Spanish translation of department name', max_length=32, null=True),
        ),
    ]