import csv
import pipeline
import dataset
import argparse

equivalence_map = {
    'na': ('', 'na'),
    '': ('', 'na')
}

def compare_row(expected_index, expected_row, actual_index, actual_row, keys):
    all_true = True
    for k in keys:
        expected_value = expected_row.value_from_fieldname(expected_index, k)
        actual_value = actual_row.value_from_fieldname(actual_index, k)
        if expected_value in equivalence_map:
            all_true = all_true and actual_value in equivalence_map[expected_value]
        else:
            all_true = all_true and expected_value == actual_value
    return all_true

def compare(expected, actual, verbose):
    print(f'Comparing expected {expected} and current {actual}')

    with open(expected) as f:
        expected_ds = dataset.Dataset(f)
    expected_field_names = expected_ds.names_
    with open(actual) as f:
        actual_ds = dataset.Dataset(f)
    actual_field_names = actual_ds.names_

    # compare field names
    if expected_field_names == actual_field_names:
        print('field names are identical')
    else:
        print('WARNING: only in expected:', set(expected_field_names).difference(set(actual_field_names)))
        print('WARNING: only in actual:', set(actual_field_names).difference(set(expected_field_names)))

    common_fields = set(expected_field_names).intersection(set(actual_field_names))
    if verbose:
        print('common fields:', common_fields)

    # compare data content
    if expected_ds.row_count() == actual_ds.row_count():
        print(f'both files have {expected_ds.row_count()} rows')
    else:
        print(f'WARNING: expected file has {expected_ds.row_count()} rows, actual file has {actual_ds.row_count()} rows')

    disparities = 0
    for i in range(expected_ds.row_count()):
            if not compare_row(i, expected_ds, i, actual_ds, common_fields):
                disparities += 1

    if disparities > 0:
        print('WARNING: rows not equal')
    else:
        print('rows equal')

def validate(expected_patients_file_name, actual_patient_file_name,
             expected_assessments_file_name, actual_assessments_file_name, verbose=False):
    compare(expected_patients_file_name, actual_patient_file_name, verbose)
    compare(expected_assessments_file_name, actual_assessments_file_name, verbose)

def validate_full():
    filename = '/home/ben/covid/assessments_20200413050002_clean.csv'


    with open(filename) as asmt:
        csvr = csv.DictReader(asmt)
        fieldnames = csvr.fieldnames
        print(fieldnames)

        for ir, r in enumerate(csvr):
            if r['tested_covid_positive'] != '':
                print(ir, r['id'], r['patient_id'], r['tested_covid_positive'])

def show_rows(filename, fields_to_show):
    with open(filename) as f:
        ds = dataset.Dataset(f)
    # ds.parse_file()
    ds.sort(('patient_id', 'updated_at'))
    for i_f, f in enumerate(ds.fields_):
        if ds.value_from_fieldname(i_f, 'patient_id') == 'e88bfabe5b16897866f91deb8a7a90f2':
            pipeline.print_diagnostic_row(f'{i_f}:', ds, ds.fields_, i_f, fields_to_show)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-pe', '--patients_expected',
                        help='the location of the patient file produced by a correct version (currently v.0.1.2) of the pipeline')
    parser.add_argument('-pa', '--patients_actual',
                        help='the location of the patient file produced by the current version of the pipeline')
    parser.add_argument('-ae', '--assessments_expected',
                        help='the location of the assessments file produced by a correct version (currently v.0.1.2) of the pipeline')
    parser.add_argument('-aa', '--assessments_actual',
                        help='the location of the assessments file produced by the current version of the pipeline')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='increase verbosity')
    args = parser.parse_args()
    validate(args.patients_expected, args.patients_actual, args.assessments_expected, args.assessments_actual,
             verbose=args.verbose)