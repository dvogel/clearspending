#!/bin/python

from completeness.metrics import *
import re

re_non_nummeric = re.compile(r'[^\d]')
re_good_date = re.compile(r'\d{4}\-\d{2}\-\d{2}')

@boolean
def cfda_program_num_not_multi(row):
    return row['cfda_program_num'].strip()!='MU.LTI'

@boolean
def cfda_program_num_not_none(row):
    return row['cfda_program_num'].strip()!='00.000'
    
@boolean
def cfda_program_num_is_descriptive(row):
    return cfda_program_num_not_none(row) and cfda_program_num_not_multi(row) and len(row['cfda_program_num'].strip())>0
    
@boolean
def recipient_name_not_empty(row):
    return len(row['recipient_name'].strip()) > 0

@integer
def recipient_name_length(row):
    return len(row['recipient_name'].strip())

@boolean
def recipient_city_code_not_empty():
    return len(row['recipient_city_code'].strip()) > 0
    
@boolean
def recipient_city_name_not_empty(row):
    return len(row['recipient_city_name'].strip())>0

@boolean
def recipient_county_code_not_empty_or_too_long(row):
    x = row['recipient_county_code'].strip()
    return len(x)>0 and len(x)<=3
    
@boolean
def recipient_county_name_not_empty(row):
    return recipient_city_name_not_empty(row)

@boolean
def recipient_state_code_not_empty(row):
    return len(row['recipient_state_code'].strip())>0

@integer
def recipient_state_code_length(row):
    return len(row['recipient_state_code'].strip())
    
@boolean
def recipient_zip_code_not_empty(row):
    return len(row['recipient_zip'].strip())>0

@integer
def recipient_zip_code_length(row):
    return len(row['recipient_zip'].strip())

@boolean
def recipient_zip_code_is_numeric(row):
    return re_non_nummeric.search(row['recipient_zip']) is None

@boolean
def recipient_type_is_not_empty(row):
    return len(row['recipient_type'].strip())>0

@boolean
def action_type_is_not_empty(row):
    return len(row['action_type'].strip())>0

@boolean
def recipient_cong_district_is_not_empty(row):
    return len(row['recipient_cong_district'].strip())>0
    
@boolean
def federal_agency_code_is_not_empty(row):
    return len(row['agency_code'])>0

@integer
def federal_agency_code_length(row):
    return len(row['agency_code'])

@boolean
def federal_award_id_is_not_empty(row):
    return len(row['federal_award_id'].strip())>0

@boolean
def federal_funding_amount_is_not_empty(row):
    return len(row['fed_funding_amount'].strip())>0

@boolean
def federal_funding_amount_is_numeric(row):
    return re_non_nummeric.search(row['fed_funding_amount']) is None

@boolean
def obligation_action_date_is_not_empty(row):
    return len(row['obligation_action_date'])>0

@boolean
def obligation_action_date_is_properly_formatted(row):
    return not (re_good_date.match(row['obligation_action_date']) is None)

@boolean
def assistance_type_is_not_empty(row):
    return len(row['assistance_type'])>0

@boolean
def record_type_is_not_empty(row):
    return len(row['record_type'])>0

@boolean
def principal_place_code_not_empty(row):
    return len(row['principal_place_code'])>0

@boolean
def principal_place_state_not_empty(row):
    return len(row['principal_place_state'].strip())>0

@integer
def principal_place_state_length(row):
    return len(row['principal_place_state'].strip())

@boolean
def principal_place_cc_not_empty(row):
    return len(row['principal_place_cc'].strip())>0

@integer
def principal_place_cc_length(row):
    return len(row['principal_place_cc'].strip())
