from django.db import models


class Directory(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    description = models.CharField(blank=True, max_length=300)
    creation_date = models.DateField()
    owner = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    availability_flag = models.BooleanField()
    timestamp_validity = models.ForeignKey('TimeValidity', null=True, on_delete=models.SET_NULL)
    is_placed_in = models.ForeignKey('Directory', blank=True, null=True, on_delete=models.SET_NULL)


class File(models.Model):
    name = models.CharField(max_length=100, primary_key=True)
    description = models.CharField(blank=True, max_length=300)
    creation_date = models.DateField()

    code = models.FileField(upload_to='files/')

    owner = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    availability_flag = models.BooleanField()
    timestamp_validity = models.ForeignKey('TimeValidity', null=True, on_delete=models.SET_NULL)
    is_placed_in = models.ForeignKey('Directory', null=True, on_delete=models.SET_NULL)


class FileSection(models.Model):
    name = models.CharField(blank=True, max_length=100)
    description = models.CharField(blank=True, max_length=300)
    creation_date = models.DateField()

    line_from = models.IntegerField(default=-1)
    line_to = models.IntegerField(default=-1)

    section_category = models.ForeignKey('SectionCategory', null=True, on_delete=models.SET_NULL)
    status = models.ForeignKey('SectionStatus', null=True, on_delete=models.SET_NULL)
    status_data = models.ForeignKey('StatusData', null=True, on_delete=models.SET_NULL)
    timestamp_validity = models.ForeignKey('TimeValidity', null=True, on_delete=models.SET_NULL)
    is_section_of = models.ForeignKey('File', null=True, on_delete=models.SET_NULL)
    is_subsection_of = models.ForeignKey('FileSection', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class SectionCategory(models.Model):
    available_categories = (
        ('PC', 'procedure'),
        ('PP', 'property'),
        ('LM', 'lemma'),
        ('AS', 'assertion'),
        ('IN', 'invariant'),
        ('PR', 'precondition'),
        ('PO', 'postcondition',)
    )
    category = models.CharField(max_length=2, choices=available_categories)
    timestamp_validity = models.ForeignKey('TimeValidity', null=True, on_delete=models.SET_NULL)

    def get_full_name(self):
        if self.category == 'PC':
            return 'procedure'
        if self.category == 'PP':
            return 'property'
        if self.category == 'LM':
            return 'lemma'
        if self.category == 'AS':
            return 'assertion'
        if self.category == 'IN':
            return 'invariant'
        if self.category == 'PR':
            return 'precondition'
        if self.category == 'PO':
            return 'postcondition'
        return None


class SectionStatus(models.Model):
    available_status = (
        ('PR', 'proved'),
        ('IN', 'invalid'),
        ('CE', 'counterexample'),
        ('UC', 'unchecked'),
    )
    status = models.CharField(max_length=2, choices=available_status)
    timestamp_validity = models.ForeignKey('TimeValidity', null=True, on_delete=models.SET_NULL)

    def get_full_name(self):
        if self.status == 'PR':
            return 'proved'
        if self.status == 'IN':
            return 'invalid'
        if self.status == 'CE':
            return 'counterexample'
        if self.status == 'UC':
            return 'unchecked'
        return None


class StatusData(models.Model):
    status_data_field = models.CharField(max_length=500)
    user = models.ForeignKey('User', null=True, on_delete=models.SET_NULL)
    timestamp_validity = models.ForeignKey('TimeValidity', null=True, on_delete=models.SET_NULL)


class User(models.Model):
    login = models.CharField(max_length=100)
    name = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    timestamp_validity = models.ForeignKey('TimeValidity', null=True, on_delete=models.SET_NULL)

    def __str__(self):
        return self.name


class TimeValidity(models.Model):
    creation_date = models.DateField()
    is_valid = models.BooleanField()
