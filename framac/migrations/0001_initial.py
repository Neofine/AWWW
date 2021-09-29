# Generated by Django 3.1.7 on 2021-04-12 17:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Directory',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=300)),
                ('creation_date', models.DateField()),
                ('availability_flag', models.BooleanField()),
                ('is_placed_in', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.directory')),
            ],
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('name', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('description', models.CharField(blank=True, max_length=300)),
                ('creation_date', models.DateField()),
                ('code', models.FileField(upload_to='files/')),
                ('availability_flag', models.BooleanField()),
                ('is_placed_in', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.directory')),
            ],
        ),
        migrations.CreateModel(
            name='TimeValidity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('creation_date', models.DateField()),
                ('is_valid', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('login', models.CharField(max_length=100)),
                ('password', models.CharField(max_length=100)),
                ('timestamp_validity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.timevalidity')),
            ],
        ),
        migrations.CreateModel(
            name='StatusData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_data_field', models.CharField(max_length=500)),
                ('timestamp_validity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.timevalidity')),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.user')),
            ],
        ),
        migrations.CreateModel(
            name='SectionStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('PR', 'proved'), ('IN', 'invalid'), ('CE', 'counterexample'), ('UC', 'unchecked')], max_length=2)),
                ('timestamp_validity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.timevalidity')),
            ],
        ),
        migrations.CreateModel(
            name='SectionCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('category', models.CharField(choices=[('PC', 'procedure'), ('PP', 'property'), ('LM', 'lemma'), ('AS', 'assertion'), ('IN', 'invariant'), ('PR', 'precondition'), ('PO', 'postconditions')], max_length=2)),
                ('timestamp_validity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.timevalidity')),
            ],
        ),
        migrations.CreateModel(
            name='FileSection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100)),
                ('description', models.CharField(blank=True, max_length=300)),
                ('creation_date', models.DateField()),
                ('code_or_comment', models.CharField(max_length=3000)),
                ('is_section_of', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.file')),
                ('is_subsection_of', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.filesection')),
                ('section_category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.sectioncategory')),
                ('status', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.sectionstatus')),
                ('status_data', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.statusdata')),
                ('timestamp_validity', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.timevalidity')),
            ],
        ),
        migrations.AddField(
            model_name='file',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.user'),
        ),
        migrations.AddField(
            model_name='file',
            name='timestamp_validity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.timevalidity'),
        ),
        migrations.AddField(
            model_name='directory',
            name='owner',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.user'),
        ),
        migrations.AddField(
            model_name='directory',
            name='timestamp_validity',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='framac.timevalidity'),
        ),
    ]
