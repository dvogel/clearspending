from cfda.models import Program, ProgramObligation, Agency
from metrics.models import *
from django.shortcuts import render_to_response
from django.db.models import Count
from decimal import Decimal
import math

FISCAL_YEARS = [2009, 2008, 2007]

def get_css_color(pct, metric):
    if metric == 'con':  #consistency
        if pct > Decimal('50'): return 'bad'
        elif pct > Decimal('25'): return 'warn'
        else: return 'good'
    elif metric == 'timeliness':
        if pct < Decimal('.95'): return 'bad'
        else: return 'good'
    #completeness


def index(request, unit='dollars', fiscal_year=2009):
    #get top level agency stats 
    consistency = AgencyConsistency.objects.filter(fiscal_year=fiscal_year).order_by('agency__name')
    timeliness = AgencyTimeliness.objects.filter(fiscal_year=fiscal_year).order_by('agency__name')
#   completeness = AgencyCompleteness.objects.filter(fiscal_year=fiscal_year).order_by('agency__name')
    agencies = Agency.objects.all().order_by('name')
    table_data = []
    for a in agencies:

        number_programs = len(Program.objects.filter(agency=a))
        display_name = a.name
        if len(display_name) > 35: display_name = "%s..." % display_name[0:35]
        
        a_consistency = consistency.filter(agency=a)
        if len(a_consistency) > 0:
            a_consistency = a_consistency[0]
        else: a_consistency = None
        
        a_timeliness = timeliness.filter(agency=a)
        if a_timeliness:
            a_timeliness = a_timeliness[0]
        else: a_timeliness = None
        #a_completeness = completeness.filter(agency=a)[0]

        a_data = [a.code,
                  number_programs, 
                  a.name,
                  display_name]

        if a_consistency:
            over = a_consistency.__dict__['over_reported_'+unit]
            under = a_consistency.__dict__['under_reported_'+unit]
            non = a_consistency.__dict__['non_reported_'+unit]
            a_data.extend(over, get_css_color(over, 'con'), under, get_css_color(under, 'con'), non, get_css_color(non, 'con'))

        else:
            for i in range(0, 6):
                a_data.append(None)

        if a_timeliness:
            a_data.append(a_timeliness.__dict__['late_'+unit])
        else:
            a_data.append(None)
        #if a_completeness:
            #a_data.append(a_completeness.__dict__['completeness_failed_'+unit])

        table_data.append(a_data) 

    return render_to_response('scorecard_index.html', {'table_data': table_data, 'fiscal_year': "%s" % fiscal_year, 'unit':unit})

def agencyDetail(request, agency_id, unit='dollars', fiscal_year=2009):
    agency = Agency.objects.get(code=agency_id)
    programs = Program.objects.filter(agency=agency)
    consistency = AgencyConsistency.objects.get(agency=agency, fiscal_year=fiscal_year, type=1) # hack to filter out loans
    timeliness = AgencyTimeliness.objects.filter(agency=agency, fiscal_year=fiscal_year)
    #completeness

    top_level_numbers = {'underreported': consistency.__dict__['under_reported_' + unit],
                         'overreported': consistency.__dict__['over_reported_' + unit],
                         'nonreported': consistency.__dict__['non_reported_' + unit],
                        }
    if len(timeliness) > 0:
        top_level_numbers['late'] = timeliness[0].__dict__['late' + unit]
    
    #build data structure to easily display in template 
    table_data = []
    types = [None, "grants", "loans"]
    for p in programs:
        obligation = ProgramConsistency.objects.filter(fiscal_year=fiscal_year, program=p)
        timeliness = ProgramTimeliness.objects.filter(fiscal_year=fiscal_year, program=p)
        completeness = ProgramCompleteness.objects.filter(fiscal_year=fiscal_year, program=p)
        for ob in obligation:
            over = ob.__dict__['over_reported_'+unit]
            under = math.fabs(float(ob.__dict__['under_reported_'+unit] or 0))
            non = math.fabs(float(ob.__dict__['non_reported_'+unit] or 0))
            display_name = p.program_title
            if len(display_name) > 35: display_name = "%s..." % display_name[0:32]
            row = [ p.program_number,
                    p.id,
                    "%s <br />(%s)" % (display_name, types[ob.type]),
                    over,
                    get_css_color(over, 'con',),
                    under,
                    get_css_color(under, 'con'),
                    non,
                    get_css_color(non, 'con')
                    ]

            if len(timeliness) > 0:
               row.append(timeliness[0].__dict__['late_'+unit])
            if len(completeness) > 0:
               row.append(completeness[0].__dict__['completeness_'+unit])

            table_data.append(row)

    return render_to_response('agency_detail.html', {'top_level_numbers': top_level_numbers, 'table_data': table_data, 'fiscal_year': fiscal_year, 'unit': unit, 'agency_name': agency.name})

def programDetail(request, program_id, unit):
    consistency_block = programDetailConsistency(program_id, unit)
    #TO DO:  get html block for consistency and timeliness
    return render_to_response('program_detail.html', {'consistency':consistency_block}) 
    


def getConsistencyDisplay(obligation, unit):
    if unit == 'percent':
        return '%s' % obligation.weighted_delta
    else:
        return '%s' % obligation.delta

def programDetailConsistency(program_id, unit):
    #returns a chunk of HTML showing the detailed consistency stats for this program
    types = [1, 2] # 1=grants, 2=loans,guarantees,insurance
    program = Program.objects.get(id=program_id)
    program_obligations = ProgramObligation.objects.filter(program=program).order_by('fiscal_year')
    html = []
    if program_obligations:
        for ty in types:
            obligations = program_obligations.filter(type=ty)
            if obligations:
                    html.append('<table class="consistency">')
                    html.append('<tr><td>Metric</td>')
                    for fy in FISCAL_YEARS: html.append('<th>' + str(fy) + '</th>')
                    html.append('</tr><tr><td>Overreported</td>')
                    for fy in FISCAL_YEARS:
                        #use predefined FY so it all looks standard
                        try:
                            p = obligations.filter(fiscal_year=fy)[0]
                        except Exception:
                            html.append('<td>&mdash;</td>')
                            continue
                        html.append('<td>')
                        if p.delta > 0:
                            html.append(getConsistencyDisplay(p, unit))
                        else:
                            html.append('&mdash;')
                        html.append('</td>')

                    html.append('</tr><tr><td>Underreported</td>')
                    for fy in FISCAL_YEARS:
                        try:
                            p = obligations.filter(fiscal_year=fy)[0]
                        except Exception:
                            html.append('<td>&mdash;</td>')
                            continue
                        html.append('<td>')
                        if -1 < p.delta < 0:
                            html.append(getConsistencyDisplay(p, unit))
                        else:
                            html.append('&mdash;')
                    
                    html.append('</tr><tr><td>Not reported</td>')
                    for fy in FISCAL_YEARS:
                        try:
                            p = obligations.filter(fiscal_year=fy)[0]
                        except Exception:
                            html.append('<td>&mdash;</td>')
                            continue
                        html.append('<td>')
                        if p.delta == -1:
                            html.append(getConsistencyDisplay(p, unit))
                        else:
                            html.append('&mdash;')

                    html.append('</tr></table>')
                
    return ''.join(html)    
