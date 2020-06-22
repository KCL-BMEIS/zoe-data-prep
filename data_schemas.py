# Copyright 2020 KCL-BMEIS - King's College London
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np

import persistence


class FieldDesc:
    def __init__(self, field, strings_to_values, values_to_strings, to_datatype):
        self.field = field
        self.to_datatype = to_datatype
        self.strings_to_values = strings_to_values
        self.values_to_strings = values_to_strings

    def __str__(self):
        output = 'FieldDesc(field={}, strings_to_values={}, values_to_strings={})'
        return output.format(self.field, self.strings_to_values, self.values_to_strings)

    def __repr__(self):
        return self.__str__()


class FieldEntry:
    def __init__(self, field_desc, version_from, version_to=None):
        self.field_desc = field_desc
        self.version_from = version_from
        self.version_to = version_to

    def __str__(self):
        output = 'FieldEntry(field_desc={}, version_from={}, version_to={})'
        return output.format(self.field_desc, self.version_from, self.version_to)

    def __repr__(self):
        return self.__str__()


class DataSchemaVersionError(Exception):
    pass


def _build_map(value_list):
    inverse = dict()
    for ir, r in enumerate(value_list):
        inverse[r] = ir
    return inverse


class DataSchema:
    data_schemas = [1]
    na_value_from = ''
    na_value_to = ''
    leaky_boolean_to = [na_value_to, 'False', 'True']
    leaky_boolean_from = _build_map(leaky_boolean_to)


    field_writers = {
        'idtype': lambda g, cs, n, ts: persistence.FixedStringWriter2(g, cs, n, ts, 32),
        'datetimetype': lambda g, cs, n, ts: persistence.TimestampWriter2(g, cs, n, ts),
        'datetype': lambda g, cs, n, ts: persistence.TimestampWriter2(g, cs, n, ts),
        'indexedstringtype': lambda g, cs, n, ts: persistence.IndexedStringWriter2(g, cs, n, ts),
        'countrycodetype': lambda g, cs, n, ts: persistence.FixedStringWriter2(g, cs, n, ts, 2),
        'unittype': lambda g, cs, n, ts: persistence.FixedStringWriter2(g, cs, n, ts, 1),
        'categoricaltype': lambda g, cs, n, ts, stv: persistence.CategoricalWriter2(g, cs, n, ts, stv),
        'float32type': lambda g, cs, n, ts: persistence.NumericWriter2(
            g, cs, n, ts, 'float32', persistence.str_to_float, True),
        'uint16type': lambda g, cs, n, ts: persistence.NumericWriter2(
            g, cs, n, ts, 'uint16', persistence.str_to_int, True),
        'geocodetype': lambda g, cs, n, ts: persistence.FixedStringWriter2(g, cs, n, ts, 9)
    }

    patient_field_types = {
        'id': 'idtype',
        'created_at': 'datetimetype',
        'updated_at': 'datetimetype',
        'version': 'indexedstringtype',
        'country_code': 'countrycodetype',
        'reported_by_another': 'categoricaltype',
        'same_household_as_reporter': 'categoricaltype',
        'year_of_birth': 'float32type',
        'height_cm': 'float32type',
        'weight_kg': 'float32type',
        'gender': 'categoricaltype',
        'race_other': 'indexedstringtype',
        'ethnicity': 'categoricaltype',
        'profile_attributes_updated_at': 'datetimetype',
        'has_diabetes': 'categoricaltype',
        'has_heart_disease': 'categoricaltype',
        'has_lung_disease': 'categoricaltype',
        'is_smoker': 'categoricaltype',
        'does_chemotherapy': 'categoricaltype',
        'has_kidney_disease': 'categoricaltype',
        'housebound_problems': 'categoricaltype',
        'mobility_aid': 'categoricaltype',
        'limited_activity': 'categoricaltype',
        'takes_corticosteroids': 'categoricaltype',
        'takes_immunosuppressants': 'categoricaltype',
        'help_available': 'categoricaltype',
        'needs_help': 'categoricaltype',
        'unwell_month_before': 'categoricaltype',
        'still_have_past_symptoms': 'categoricaltype',
        'past_symptoms_days_ago': 'uint16type',
        'past_symptoms_changed': 'categoricaltype',
        'past_symptom_anosmia': 'categoricaltype',
        'past_symptom_shortness_of_breath': 'categoricaltype',
        'past_symptom_fatigue': 'categoricaltype',
        'past_symptom_fever': 'categoricaltype',
        'past_symptom_skipped_meals': 'categoricaltype',
        'past_symptom_persistent_cough': 'categoricaltype',
        'past_symptom_diarrhoea': 'categoricaltype',
        'past_symptom_chest_pain': 'categoricaltype',
        'past_symptom_hoarse_voice': 'categoricaltype',
        'past_symptom_abdominal_pain': 'categoricaltype',
        'past_symptom_delirium': 'categoricaltype',
        'already_had_covid': 'categoricaltype',
        'classic_symptoms': 'categoricaltype',
        'takes_blood_pressure_medications_pril': 'categoricaltype',
        'takes_any_blood_pressure_medications': 'categoricaltype',
        'need_inside_help': 'categoricaltype',
        'need_outside_help': 'categoricaltype',
        'contact_health_worker': 'categoricaltype',
        'is_in_uk_twins': 'categoricaltype',
        'is_pregnant': 'categoricaltype',
        'pregnant_weeks': 'uint16type',
        'period_stopped_age': 'uint16type',
        'period_status': 'categoricaltype',
        'period_frequency': 'categoricaltype',
        'ht_none': 'categoricaltype',
        'ht_combined_oral_contraceptive_pill': 'categoricaltype',
        'ht_progestone_only_pill': 'categoricaltype',
        'ht_mirena_or_other_coil': 'categoricaltype',
        'ht_depot_injection_or_implant': 'categoricaltype',
        'ht_hormone_treatment_therapy': 'categoricaltype',
        'ht_oestrogen_hormone_therapy': 'categoricaltype',
        'ht_testosterone_hormone_therapy': 'categoricaltype',
        'ht_pfnts': 'categoricaltype',
        'always_used_shortage': 'categoricaltype',
        'have_used_PPE': 'categoricaltype',
        'have_worked_in_hospital_care_facility': 'categoricaltype',
        'have_worked_in_hospital_clinic': 'categoricaltype',
        'have_worked_in_hospital_home_health': 'categoricaltype',
        'have_worked_in_hospital_inpatient': 'categoricaltype',
        'have_worked_in_hospital_other': 'categoricaltype',
        'have_worked_in_hospital_outpatient': 'categoricaltype',
        'have_worked_in_hospital_school_clinic': 'categoricaltype',
        'healthcare_professional': 'categoricaltype',
        'interacted_with_covid': 'categoricaltype',
        'is_carer_for_community': 'categoricaltype',
        'is_in_uk_biobank': 'categoricaltype',
        'is_in_uk_guys_trust': 'categoricaltype',
        'is_in_us_mass_general_brigham': 'categoricaltype',
        'is_in_us_nurses_study': 'categoricaltype',
        'is_in_us_stanford_diabetes': 'categoricaltype',
        'is_in_us_stanford_well': 'categoricaltype',
        'is_in_us_growing_up_today': 'categoricaltype',
        'is_in_us_stanford_nutrition': 'categoricaltype',
        'is_in_us_multiethnic_cohort': 'categoricaltype',
        'is_in_us_predict2': 'categoricaltype',
        'is_in_us_american_cancer_society_cancer_prevention_study_3': 'categoricaltype',
        'is_in_us_harvard_health_professionals': 'categoricaltype',
        'is_in_us_california_teachers': 'categoricaltype',
        'is_in_us_sister': 'categoricaltype',
        'is_in_us_agricultural_health': 'categoricaltype',
        'is_in_us_gulf': 'categoricaltype',
        'is_in_us_aspree_xt': 'categoricaltype',
        'is_in_us_bwhs': 'categoricaltype',
        'is_in_us_partners_biobank': 'categoricaltype',
        'is_in_us_mass_eye_ear_infirmary': 'categoricaltype',
        'is_in_us_chasing_covid': 'categoricaltype',
        'is_in_us_predetermine': 'categoricaltype',
        'is_in_us_environmental_polymorphisms': 'categoricaltype',
        'is_in_us_promise_pcrowd': 'categoricaltype',
        'is_in_us_colocare': 'categoricaltype',
        'is_in_us_covid_flu_near_you': 'categoricaltype',
        'is_in_us_md_anderson_d3code': 'categoricaltype',
        'is_in_us_hispanic_colorectal_cancer': 'categoricaltype',
        'is_in_us_colon_cancer_family_registry': 'categoricaltype',
        'is_in_us_louisiana_state_university': 'categoricaltype',
        'is_in_us_covid_siren': 'categoricaltype',
        'is_in_us_northshore_genomic_health_initiative': 'categoricaltype',
        'clinical_study_names': 'indexedstringtype',
        'clinical_study_institutions': 'indexedstringtype',
        'clinical_study_nct_ids': 'indexedstringtype',
        'never_used_shortage': 'categoricaltype',
        'sometimes_used_shortage': 'categoricaltype',
        'classic_symptoms_days_ago': 'uint16type',
        'interacted_patients_with_covid': 'categoricaltype',
        'smoked_years_ago': 'uint16type',
        'smoker_status': 'categoricaltype',
        'takes_aspirin': 'categoricaltype',
        'takes_blood_pressure_medications_sartan': 'categoricaltype',
        'has_cancer': 'categoricaltype',
        'cancer_clinical_trial_site': 'indexedstringtype',
        'cancer_type': 'indexedstringtype',
        'on_cancer_clinical_trial': 'categoricaltype',
        'last_asked_level_of_isolation': 'datetimetype',
        'ever_had_covid_test': 'categoricaltype',
        'bmi': 'float32type',
        'race_is_uk_asian': 'categoricaltype',
        'race_is_uk_black': 'categoricaltype',
        'race_is_uk_mixed_white_black': 'categoricaltype',
        'race_is_uk_mixed_other': 'categoricaltype',
        'race_is_uk_white': 'categoricaltype',
        'race_is_uk_chinese': 'categoricaltype',
        'race_is_uk_middle_eastern': 'categoricaltype',
        'race_is_us_indian_native': 'categoricaltype',
        'race_is_us_asian': 'categoricaltype',
        'race_is_us_black': 'categoricaltype',
        'race_is_us_hawaiian_pacific': 'categoricaltype',
        'race_is_us_white': 'categoricaltype',
        'race_is_other': 'categoricaltype',
        'race_is_prefer_not_to_say': 'categoricaltype',
        'vs_vitamin_d': 'categoricaltype',
        'vs_other': 'indexedstringtype',
        'vs_omega_3': 'categoricaltype',
        'vs_none': 'categoricaltype',
        'vs_vitamin_c': 'categoricaltype',
        'vs_pftns': 'categoricaltype',
        'vs_multivitamins': 'categoricaltype',
        'vs_garlic': 'categoricaltype',
        'vs_probiotics': 'categoricaltype',
        'vs_zinc': 'categoricaltype',
        'vs_asked_at': 'datetimetype',
        'has_asthma': 'categoricaltype',
        'has_eczema': 'categoricaltype',
        'has_hayfever': 'categoricaltype',
        'has_lung_disease_only': 'categoricaltype',
        'diabetes_type': 'categoricaltype',
        'diabetes_type_other': 'indexedstringtype',
        'diabetes_diagnosis_year': 'uint16type',
        'diabetes_treatment_none': 'categoricaltype',
        'diabetes_treatment_lifestyle': 'categoricaltype',
        'diabetes_treatment_basal_insulin': 'categoricaltype',
        'diabetes_treatment_rapid_insulin': 'categoricaltype',
        'diabetes_treatment_other_injection': 'indexedstringtype',
        'diabetes_oral_biguanide': 'categoricaltype',
        'diabetes_oral_dpp4': 'categoricaltype',
        'diabetes_oral_meglitinides': 'categoricaltype',
        'diabetes_oral_sglt2': 'categoricaltype',
        'diabetes_oral_sulfonylurea': 'categoricaltype',
        'diabetes_oral_thiazolidinediones': 'categoricaltype',
        'diabetes_oral_other_medication': 'categoricaltype',
        'diabetes_treatment_other_oral': 'indexedstringtype',
        'a1c_measurement_percent': 'float32type',
        'a1c_measurement_mmol': 'float32type',
        'zipcode': 'indexedstringtype',
        'se_postcode': 'indexedstringtype',
        'outward_postcode': 'indexedstringtype',
        'lsoa11cd': 'geocodetype',
        'msoa11cd': 'geocodetype',
        'ladcd': 'geocodetype',
        'lsoa11nm': 'indexedstringtype',
        'msoa11nm': 'indexedstringtype',
        'outward_postcode_latitude': 'float32type',
        'outward_postcode_longitude': 'float32type',
        'outward_postcode_town_area': 'indexedstringtype',
        'outward_postcode_region': 'indexedstringtype'
    }

    assessment_field_types = {
        'id': 'idtype',
        'patient_id': 'idtype',
        'created_at': 'datetimetype',
        'updated_at': 'datetimetype',
        'version': 'indexedstringtype',
        'country_code': 'countrycodetype',
        'health_status': 'categoricaltype',
        'date_test_occurred': 'datetype',
        'date_test_occurred_guess': 'categoricaltype',
        'fever': 'categoricaltype',
        'temperature': 'float32type',
        'temperature_unit': 'unittype',
        'persistent_cough': 'categoricaltype',
        'fatigue': 'categoricaltype',
        'shortness_of_breath': 'categoricaltype',
        'diarrhoea': 'categoricaltype',
        'diarrhoea_frequency': 'categoricaltype',
        'delirium': 'categoricaltype',
        'skipped_meals': 'categoricaltype',
        'location': 'categoricaltype',
        'treatment': 'indexedstringtype',
        'had_covid_test': 'categoricaltype',
        'tested_covid_positive': 'categoricaltype',
        'abdominal_pain': 'categoricaltype',
        'chest_pain': 'categoricaltype',
        'hoarse_voice': 'categoricaltype',
        'loss_of_smell': 'categoricaltype',
        'headache': 'categoricaltype',
        'headache_frequency': 'categoricaltype',
        'other_symptoms': 'indexedstringtype',
        'chills_or_shivers': 'categoricaltype',
        'eye_soreness': 'categoricaltype',
        'nausea': 'categoricaltype',
        'dizzy_light_headed': 'categoricaltype',
        'red_welts_on_face_or_lips': 'categoricaltype',
        'blisters_on_feet': 'categoricaltype',
        'sore_throat': 'categoricaltype',
        'unusual_muscle_pains': 'categoricaltype',
        'level_of_isolation': 'categoricaltype',
        'isolation_little_interaction': 'uint16type',
        'isolation_lots_of_people': 'uint16type',
        'isolation_healthcare_provider': 'uint16type',
        'always_used_shortage': 'categoricaltype',
        'have_used_PPE': 'categoricaltype',
        'never_used_shortage': 'categoricaltype',
        'sometimes_used_shortage': 'categoricaltype',
        'interacted_any_patients': 'categoricaltype',
        'treated_patients_with_covid': 'categoricaltype',
        'worn_face_mask': 'categoricaltype',
        'mask_cloth_or_scarf': 'categoricaltype',
        'mask_surgical': 'categoricaltype',
        'mask_not_sure_pfnts': 'categoricaltype',
        'mask_n95_ffp': 'categoricaltype',
        'mask_other': 'indexedstringtype',
        'typical_hayfever': 'categoricaltype',
    }

    test_field_types = {
        'id': 'idtype',
        'patient_id': 'idtype',
        'created_at': 'datetimetype',
        'updated_at': 'datetimetype',
        'version': 'indexedstringtype',
        'country_code': 'countrycodetype',
        'result': 'categoricaltype',
        'mechanism': 'indexedstringtype',
        'date_taken_specific': 'datetype',
        'date_taken_between_start': 'datetype',
        'date_taken_between_end': 'datetype'
    }

    # tuple entries
    # 0: name
    # 1: values_to_strings,
    # 2: string_to_values or None if it should be calculated from values_to_string
    # 3: inclusive version from
    # 4: exclusive version to
    patient_categorical_fields = [
        ('race_is_uk_white', ['False', 'True'], None, np.uint8, 1, None),
        ('need_inside_help', leaky_boolean_to, None, np.uint8, 1, None),
        ('on_cancer_clinical_trial', leaky_boolean_to, None, np.uint8, 1, None),
        ('race_is_uk_mixed_white_black', ['False', 'True'], None, np.uint8, 1, None),
        ('always_used_shortage', ['', 'all_needed', 'reused'], None, np.uint8, 1, None),
        ('sometimes_used_shortage', ['', 'all_needed', 'reused', 'not_enough'], None, np.uint8, 1, None),
        ('race_is_uk_asian', ['False', 'True'], None, np.uint8, 1, None),
        ('is_in_uk_twins', leaky_boolean_to, None, np.uint8, 1, None),
        ('have_worked_in_hospital_other', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_aspree_xt', leaky_boolean_to, None, np.uint8, 1, None),
        ('help_available', leaky_boolean_to, None, np.uint8, 1, None),
        ('have_worked_in_hospital_outpatient', leaky_boolean_to, None, np.uint8, 1, None),
        ('has_cancer', leaky_boolean_to, None, np.uint8, 1, None),
        ('past_symptom_hoarse_voice', leaky_boolean_to, None, np.uint8, 1, None),
        ('reported_by_another', ['False', 'True'], None, np.uint8, 1, None),
        ('is_in_us_colocare', leaky_boolean_to, None, np.uint8, 1, None),
        ('interacted_with_covid', ['', 'no', 'yes_suspected', 'yes_documented_suspected', 'yes_documented'], None, np.uint8, 1, None),
        ('race_is_other', ['False', 'True'], None, np.uint8, 1, None),
        ('period_frequency', ['', 'less_frequent', 'irregular', 'regular'], None, np.uint8, 1, None),
        ('have_used_PPE', ['', 'never', 'sometimes', 'always'], None, np.uint8, 1, None),
        ('is_in_us_predetermine', leaky_boolean_to, None, np.uint8, 1, None),
        ('takes_aspirin', leaky_boolean_to, None, np.uint8, 1, None),
        ('past_symptom_anosmia', leaky_boolean_to, None, np.uint8, 1, None),
        ('past_symptom_delirium', leaky_boolean_to, None, np.uint8, 1, None),
        ('same_household_as_reporter', leaky_boolean_to, None, np.uint8, 1, None),
        ('ht_oestrogen_hormone_therapy', leaky_boolean_to, None, np.uint8, 1, None),
        ('past_symptoms_changed', ['', 'much_better', 'little_better', 'same', 'little_worse', 'much_worse'], None, np.uint8, 1, None),
        ('past_symptom_chest_pain', leaky_boolean_to, None, np.uint8, 1, None),
        ('need_outside_help', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_bwhs', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_predict2', leaky_boolean_to, None, np.uint8, 1, None),
        ('gender', ['', '0', '1', '2', '3', '99999'], None, np.uint32, 1, None),
        ('have_worked_in_hospital_school_clinic', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_growing_up_today', leaky_boolean_to, None, np.uint8, 1, None),
        ('race_is_uk_black', ['False', 'True'], None, np.uint8, 1, None),
        ('race_is_uk_chinese', ['False', 'True'], None, np.uint8, 1, None),
        ('race_is_uk_mixed_other', ['False', 'True'], None, np.uint8, 1, None),
        ('race_is_us_black', ['False', 'True'], None, np.uint8, 1, None),
        ('classic_symptoms', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_covid_siren', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_carer_for_community', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_uk_guys_trust', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_stanford_well', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_multiethnic_cohort', leaky_boolean_to, None, np.uint8, 1, None),
        ('takes_blood_pressure_medications_pril', leaky_boolean_to, None, np.uint8, 1, None),
        ('race_is_prefer_not_to_say', ['False', 'True'], None, np.uint8, 1, None),
        ('have_worked_in_hospital_inpatient', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_agricultural_health', leaky_boolean_to, None, np.uint8, 1, None),
        ('interacted_patients_with_covid', ['', 'no', 'yes_suspected', 'yes_documented_suspected', 'yes_documented'], None, np.uint8, 1, None),
        ('past_symptom_fatigue', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_stanford_nutrition', leaky_boolean_to, None, np.uint8, 1, None),
        ('race_is_us_white', ['False', 'True'], None, np.uint8, 1, None),
        ('is_in_us_gulf', leaky_boolean_to, None, np.uint8, 1, None),
        ('ht_testosterone_hormone_therapy', leaky_boolean_to, None, np.uint8, 1, None),
        ('unwell_month_before', leaky_boolean_to, None, np.uint8, 1, None),
        ('has_lung_disease', leaky_boolean_to, None, np.uint8, 1, None),
        ('housebound_problems', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_american_cancer_society_cancer_prevention_study_3', leaky_boolean_to, None, np.uint8, 1, None),
        ('ht_depot_injection_or_implant', leaky_boolean_to, None, np.uint8, 1, None),
        ('takes_corticosteroids', leaky_boolean_to, None, np.uint8, 1, None),
        ('past_symptom_shortness_of_breath', leaky_boolean_to, None, np.uint8, 1, None),
        ('race_is_us_hawaiian_pacific', ['False', 'True'], None, np.uint8, 1, None),
        ('has_heart_disease', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_harvard_health_professionals', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_colon_cancer_family_registry', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_nurses_study', leaky_boolean_to, None, np.uint8, 1, None),
        ('ht_pfnts', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_chasing_covid', leaky_boolean_to, None, np.uint8, 1, None),
        ('period_status', ['', 'other', 'pfnts', 'never', 'not_currently', 'currently', 'pregnant', 'stopped'], None, np.uint8, 1, None),
        ('never_used_shortage', ['', 'not_available', 'not_needed'], None, np.uint8, 1, None),
        ('past_symptom_persistent_cough', leaky_boolean_to, None, np.uint8, 1, None),
        ('already_had_covid', leaky_boolean_to, None, np.uint8, 1, None),
        ('ht_progestone_only_pill', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_mass_eye_ear_infirmary', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_northshore_genomic_health_initiative', leaky_boolean_to, None, np.uint8, 1, None),
        ('past_symptom_diarrhoea', leaky_boolean_to, None, np.uint8, 1, None),
        ('past_symptom_fever', leaky_boolean_to, None, np.uint8, 1, None),
        ('takes_immunosuppressants',  leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_promise_pcrowd', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_uk_biobank', leaky_boolean_to, None, np.uint8, 1, None),
        ('have_worked_in_hospital_care_facility', leaky_boolean_to, None, np.uint8, 1, None),
        ('limited_activity', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_pregnant', leaky_boolean_to, None, np.uint8, 1, None),
        ('needs_help', leaky_boolean_to, None, np.uint8, 1, None),
        ('ever_had_covid_test', leaky_boolean_to, None, np.uint8, 1, None),
        ('have_worked_in_hospital_clinic', leaky_boolean_to, None, np.uint8, 1, None),
        ('ht_none', leaky_boolean_to, None, np.uint8, 1, None),
        ('contact_health_worker', leaky_boolean_to, None, np.uint8, 1, None),
        ('smoker_status', ['', 'never', 'not_currently', 'yes'], None, np.uint8, 1, None),
        ('has_kidney_disease', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_stanford_diabetes', leaky_boolean_to, None, np.uint8, 1, None),
        ('race_is_us_indian_native', ['False', 'True'], None, np.uint8, 1, None),
        ('past_symptom_abdominal_pain', leaky_boolean_to, None, np.uint8, 1, None),
        ('past_symptom_skipped_meals', leaky_boolean_to, None, np.uint8, 1, None),
        ('race_is_uk_middle_eastern', ['False', 'True'], None, np.uint8, 1, None),
        ('is_in_us_sister', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_partners_biobank', leaky_boolean_to, None, np.uint8, 1, None),
        ('does_chemotherapy', leaky_boolean_to, None, np.uint8, 1, None),
        ('ht_hormone_treatment_therapy', leaky_boolean_to, None, np.uint8, 1, None),
        ('healthcare_professional', [na_value_to, 'no', 'yes_does_not_interact', 'yes_does_not_treat', 'yes_does_interact', 'yes_does_treat'], None, np.uint8, 1, None),
        ('race_is_us_asian', ['False', 'True'], None, np.uint8, 1, None),
        ('is_in_us_md_anderson_d3code', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_mass_general_brigham', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_louisiana_state_university', leaky_boolean_to, None, np.uint8, 1, None),
        ('ethnicity', [na_value_to, 'prefer_not_to_say', 'not_hispanic', 'hispanic'], None, np.uint8, 1, None),
        ('still_have_past_symptoms', leaky_boolean_to, None, np.uint8, 1, None),
        ('takes_blood_pressure_medications_sartan', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_hispanic_colorectal_cancer', leaky_boolean_to, None, np.uint8, 1, None),
        ('ht_combined_oral_contraceptive_pill', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_california_teachers', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_environmental_polymorphisms', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_smoker', leaky_boolean_to, None, np.uint8, 1, None),
        ('is_in_us_covid_flu_near_you', leaky_boolean_to, None, np.uint8, 1, None),
        ('mobility_aid', leaky_boolean_to, None, np.uint8, 1, None),
        ('have_worked_in_hospital_home_health', leaky_boolean_to, None, np.uint8, 1, None),
        ('takes_any_blood_pressure_medications', leaky_boolean_to, None, np.uint8, 1, None),
        ('ht_mirena_or_other_coil', leaky_boolean_to, None, np.uint8, 1, None),
        ('has_diabetes', leaky_boolean_to, None, np.uint8, 1, None),
        ('diabetes_type', [na_value_to, 'pfnts', 'gestational', 'type_1', 'type_2', 'unsure', 'other'], None, np.uint8, 1, None),
        ('diabetes_treatment_none', leaky_boolean_to, None, np.uint8, 1, None),
        ('diabetes_treatment_lifestyle', leaky_boolean_to, None, np.uint8, 1, None),
        ('diabetes_treatment_basal_insulin', leaky_boolean_to, None, np.uint8, 1, None),
        ('diabetes_treatment_rapid_insulin', leaky_boolean_to, None, np.uint8, 1, None),
        ('diabetes_oral_biguanide', leaky_boolean_to, None, np.uint8, 1, None),
        ('diabetes_oral_dpp4', leaky_boolean_to, None, np.uint8, 1, None),
        ('diabetes_oral_meglitinides', leaky_boolean_to, None, np.uint8, 1, None),
        ('diabetes_oral_sglt2', leaky_boolean_to, None, np.uint8, 1, None),
        ('diabetes_oral_sulfonylurea', leaky_boolean_to, None, np.uint8, 1, None),
        ('diabetes_oral_thiazolidinediones', leaky_boolean_to, None, np.uint8, 1, None),
        ('diabetes_oral_other_medication', leaky_boolean_to, None, np.uint8, 1, None),
        ('vs_vitamin_d', leaky_boolean_to, None, np.uint8, 1, None),
        ('vs_omega_3', leaky_boolean_to, None, np.uint8, 1, None),
        ('vs_none', leaky_boolean_to, None, np.uint8, 1, None),
        ('vs_vitamin_c', leaky_boolean_to, None, np.uint8, 1, None),
        ('vs_pftns', leaky_boolean_to, None, np.uint8, 1, None),
        ('vs_multivitamins', leaky_boolean_to, None, np.uint8, 1, None),
        ('vs_garlic', leaky_boolean_to, None, np.uint8, 1, None),
        ('vs_probiotics', leaky_boolean_to, None, np.uint8, 1, None),
        ('vs_zinc', leaky_boolean_to, None, np.uint8, 1, None),
        ('has_asthma', leaky_boolean_to, None, np.uint8, 1, None),
        ('has_eczema', leaky_boolean_to, None, np.uint8, 1, None),
        ('has_hayfever', leaky_boolean_to, None, np.uint8, 1, None),
        ('has_lung_disease_only', leaky_boolean_to, None, np.uint8, 1, None),
        ('age_filter', [na_value_to, 'bad', 'missing'], None, np.uint8, 1, None),
        ('weight_filter', [na_value_to, 'bad', 'missing'], None, np.uint8, 1, None),
        ('height_filter', [na_value_to, 'bad', 'missing'], None, np.uint8, 1, None),
        ('bmi_filter', [na_value_to, 'bad', 'missing'], None, np.uint8, 1, None)
    ]
    assessment_categorical_fields = [
        ('health_status', [na_value_to, 'healthy', 'not_healthy'], None, np.uint8, 1, None),
        ('date_test_occurred_guess', [na_value_to, 'less_than_7_days_ago', 'over_1_week_ago', 'over_2_week_ago', 'over_3_week_ago', 'over_1_month_ago'], None, np.uint8, 1, None),
        ('fatigue', [na_value_to, 'no', 'mild', 'significant', 'severe'], None, np.uint8, 1, None),
        ('shortness_of_breath', [na_value_to, 'no', 'mild', 'significant', 'severe'], None, np.uint8, 1, None),
        ('abdominal_pain', leaky_boolean_to, None, np.uint8, 1, None),
        ('blisters_on_feet', leaky_boolean_to, None, np.uint8, 1, None),
        ('chest_pain', leaky_boolean_to, None, np.uint8, 1, None),
        ('chills_or_shivers', leaky_boolean_to, None, np.uint8, 1, None),
        ('delirium', leaky_boolean_to, None, np.uint8, 1, None),
        ('diarrhoea', leaky_boolean_to, None, np.uint8, 1, None),
        ('diarrhoea_frequency', [na_value_to, 'one_to_two', 'three_to_four', 'five_or_more'], None, np.uint8, 1, None),
        ('fever', leaky_boolean_to, None, np.uint8, 1, None),
        ('headache', leaky_boolean_to, None, np.uint8, 1, None),
        ('headache_frequency', [na_value_to, 'some_of_day', 'most_of_day', 'all_of_the_day'], None, np.uint8, 1, None),
        ('hoarse_voice', leaky_boolean_to, None, np.uint8, 1, None),
        ('loss_of_smell', leaky_boolean_to, None, np.uint8, 1, None),
        ('persistent_cough', leaky_boolean_to, None, np.uint8, 1, None),
        ('skipped_meals', leaky_boolean_to, None, np.uint8, 1, None),
        ('sore_throat', leaky_boolean_to, None, np.uint8, 1, None),
        ('unusual_muscle_pains', leaky_boolean_to, None, np.uint8, 1, None),
        ('always_used_shortage', [na_value_to, 'all_needed', 'reused'], None, np.uint8, 1, None),
        ('have_used_PPE', [na_value_to, 'never', 'sometimes', 'always'], None, np.uint8, 1, None),
        ('never_used_shortage', [na_value_to, 'not_needed', 'not_available'], None, np.uint8, 1, None),
        ('sometimes_used_shortage', [na_value_to, 'all_needed', 'reused', 'not_enough'], None, np.uint8, 1, None),
        ('treated_patients_with_covid', [na_value_to, 'no', 'yes_suspected', 'yes_documented_suspected', 'yes_documented'], None, np.uint8, 1, None),
        ('fatigue_binary', leaky_boolean_to, {na_value_from: 0, 'no': 1, 'mild': 2, 'significant': 2, 'severe': 2}, np.uint8, 1, None),
        ('shortness_of_breath_binary', leaky_boolean_to, {na_value_from: 0, 'no': 1, 'mild': 2, 'significant': 2, 'severe': 2}, np.uint8, 1, None),
        ('location', [na_value_to, 'home', 'hospital', 'back_from_hospital'], None, np.uint8, 1, None),
        ('level_of_isolation', [na_value_to, 'not_left_the_house', 'rarely_left_the_house', 'rarely_left_the_house_but_visited_lots', 'often_left_the_house'], None, np.uint8, 1, None),
        ('had_covid_test', leaky_boolean_to, None, np.uint8, 1, None),
        ('tested_covid_positive', [na_value_to, 'waiting', 'no', 'yes'], None, np.uint8, 1, None),
        ('had_covid_test_clean', leaky_boolean_to, None, np.uint8, 1, None),
        ('tested_covid_positive_clean', [na_value_to, 'waiting', 'no', 'yes'], None, np.uint8, 1, None),
        ('eye_soreness', leaky_boolean_to, None, np.uint8, 1, None),
        ('dizzy_light_headed', leaky_boolean_to, None, np.uint8, 1, None),
        ('nausea', leaky_boolean_to, None, np.uint8, 1, None),
        ('red_welts_on_face_or_lips', leaky_boolean_to, None, np.uint8, 1, None),
        ('interacted_any_patients', leaky_boolean_to, None, np.uint8, 1, None),
        ('worn_face_mask', [na_value_to, 'not_applicable', 'never', 'sometimes', 'most_of_the_time', 'always'], None, np.uint8, 1, None),
        ('mask_cloth_or_scarf', leaky_boolean_to, None, np.uint8, 1, None),
        ('mask_surgical', leaky_boolean_to, None, np.uint8, 1, None),
        ('mask_not_sure_pfnts', leaky_boolean_to, None, np.uint8, 1, None),
        ('mask_n95_ffp', leaky_boolean_to, None, np.uint8, 1, None),
        ('typical_hayfever', leaky_boolean_to, None, np.uint8, 1, None),
    ]
    test_categorical_fields = [
        ('result', ['waiting', 'failed', 'negative', 'positive'], None, np.uint8, 1, None),
    ]

    assessment_field_entries = dict()
    for cf in assessment_categorical_fields:
        entry = FieldEntry(FieldDesc(cf[0], _build_map(cf[1]) if cf[2] is None else cf[2], cf[1], cf[3]),
                           cf[4], cf[5])
        entry_list = \
            list() if assessment_field_entries.get(cf[0]) is None else assessment_field_entries[cf[0]]
        entry_list.append(entry)
        assessment_field_entries[cf[0]] = entry_list

    patient_field_entries = dict()
    for cf in patient_categorical_fields:
        entry = FieldEntry(FieldDesc(cf[0], _build_map(cf[1]) if cf[2] is None else cf[2], cf[1], cf[3]),
                           cf[4], cf[5])
        entry_list = \
            list() if patient_field_entries.get(cf[0]) is None else patient_field_entries[cf[0]]
        entry_list.append(entry)
        patient_field_entries[cf[0]] = entry_list


    test_field_entries = dict()
    for cf in test_categorical_fields:
        entry = FieldEntry(FieldDesc(cf[0], _build_map(cf[1]) if cf[2] is None else cf[2], cf[1], cf[3]),
                           cf[4], cf[5])
        entry_list = \
            list() if test_field_entries.get(cf[0]) is None else test_field_entries[cf[0]]
        entry_list.append(entry)
        test_field_entries[cf[0]] = entry_list


    def __init__(self, version):
        # TODO: field entries for patients!
        self.patient_categorical_maps = self._get_patient_categorical_maps(version)
        self.assessment_categorical_maps = self._get_assessment_categorical_maps(version)
        self.test_categorical_maps = self._get_test_categorical_maps(version)


    def _validate_schema_number(self, schema):
        if schema not in DataSchema.data_schemas:
            raise DataSchemaVersionError(f'{schema} is not a valid cleaning schema value')


    def _get_patient_categorical_maps(self, version):
        return self._get_categorical_maps(DataSchema.patient_field_entries, version)


    def _get_assessment_categorical_maps(self, version):
        return self._get_categorical_maps(DataSchema.assessment_field_entries, version)


    def _get_test_categorical_maps(self, version):
        return self._get_categorical_maps(DataSchema.test_field_entries, version)


    def _get_categorical_maps(self, field_entries, version):
        self._validate_schema_number(version)

        selected_field_entries = dict()
        # get fields for which the schema number is in range
        for fe in field_entries.items():
            for e in fe[1]:
                if version >= e.version_from and (e.version_to is None or version < e.version_to):
                    selected_field_entries[fe[0]] = e.field_desc
                    break

        return selected_field_entries


    def string_field_desc(self):
        return FieldDesc('', None, None, str)
