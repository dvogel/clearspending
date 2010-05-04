from django.db import models
from cfda.models import Program, Agency


class Metric(models.Model):
    
    fiscal_year = models.IntegerField(blank=False, null=False)
    agency = models.ForeignKey('cfda.Agency', blank=False, null=False)
    
    class Meta:
        abstract = True

class Consistency(Metric):
    
    TYPE_CHOICES = (
        (1, 'Grants'),
        (2, 'Loans and Loan Guarantees')
    )

    total_cfda_obligations = models.DecimalField(max_digits=21, decimal_places=2, blank=False, null=False)
    total_usa_obligations =  models.DecimalField(max_digits=21, decimal_places=2, blank=False, null=False)
    total_programs =  models.IntegerField(blank=False, null=False)
    non_reporting_programs = models.ManyToManyField(Program)
    non_reported_obligations = models.DecimalField(max_digits=21, decimal_places=2, blank=False, null=False)
    avg_under_pct = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    avg_over_pct = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    var_under_pct = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    var_over_pct = models.DecimalField(max_digits=20, decimal_places=4, null=True) 
    std_under_pct = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    std_over_pct = models.DecimalField(max_digits=20, decimal_places=4, null=True)
    type = models.IntegerField(blank=False, null=False, choices=TYPE_CHOICES)

    

    
class ProgramMetric(Metric):
    
    GRADE_CHOICES = (
        ('p', 'Pass'),
        ('o', 'Overreporting Obligations'),
        ('u', 'Underreporting Obligations'),
        ('n', 'Not reporting Obligations'),
        ('t', 'Late reporting'),
        ('c', 'Incomplete reporting')
    )

    program = models.ForeignKey('cfda.Program', blank=False, null=False)
    grade = models.TextField(choices=GRADE_CHOICES)


