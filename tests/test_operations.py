import unittest

import numpy as np
from io import BytesIO

import h5py

from exetera.core import session
from exetera.core import fields
from exetera.core import persistence as per
from exetera.core import operations as ops
from exetera.core import utils


class TestSafeMap(unittest.TestCase):

    def _impl_safe_map_index_values(self, indices, values, map_indices,
                                    expected_indices, expected_values, empty_value):
        map_filter = map_indices != ops.INVALID_INDEX
        actual_indices, actual_values =\
            ops.safe_map_indexed_values(indices, values, map_indices, map_filter, empty_value)

        self.assertTrue(np.array_equal(actual_indices, expected_indices))
        self.assertTrue(np.array_equal(actual_values, expected_values))

    def test_safe_map_index_values(self):
        self._impl_safe_map_index_values(
            np.asarray([0, 1, 3, 6, 10, 15, 15, 20, 24, 27, 29, 30], dtype=np.int32),
            np.frombuffer(b'abbcccddddeeeeeggggghhhhiiijjk', dtype='S1'),
            np.asarray([0, 4, 10, ops.INVALID_INDEX, 8, 2, 1, ops.INVALID_INDEX, 6, 5, 9]),
            np.asarray([0, 1, 6, 7, 8, 11, 14, 16, 17, 22, 22, 24]),
            np.frombuffer(b'aeeeeekxiiicccbbxgggggjj', dtype='S1'), b'x')

    def test_safe_map_index_values_zero_empty(self):
        self._impl_safe_map_index_values(
            np.asarray([0, 1, 3, 6, 10, 15, 15, 20, 24, 27, 29, 30], dtype=np.int32),
            np.frombuffer(b'abbcccddddeeeeeggggghhhhiiijjk', dtype='S1'),
            np.asarray([0, 4, 10, ops.INVALID_INDEX, 8, 2, 1, ops.INVALID_INDEX, 6, 5, 9]),
            np.asarray([0, 1, 6, 7, 7, 10, 13, 15, 15, 20, 20, 22]),
            np.frombuffer(b'aeeeeekiiicccbbgggggjj', dtype='S1'), b'')

    def _impl_safe_map_values(self, values, map_indices, expected_values, empty_value):
        map_filter = map_indices != ops.INVALID_INDEX
        actual_values = ops.safe_map_values(values, map_indices, map_filter, empty_value)

        self.assertTrue(np.array_equal(actual_values, expected_values))

    def test_safe_map_values(self):
        self._impl_safe_map_values(
            np.asarray([1, 3, 6, 10, 15, 21, 28, 36, 45, 55]),
            np.asarray([1, 8, 2, 7, ops.INVALID_INDEX, 0, 9, 1, 8]),
            np.asarray([3, 45, 6, 36, -1, 1, 55, 3, 45]), -1)

    def test_safe_map_values(self):
        self._impl_safe_map_values(
            np.asarray([1, 3, 6, 10, 15, 21, 28, 36, 45, 55]),
            np.asarray([1, 8, 2, 7, ops.INVALID_INDEX, 0, 9, 1, 8]),
            np.asarray([3, 45, 6, 36, 0, 1, 55, 3, 45]), 0)

class TestAggregation(unittest.TestCase):

    def test_non_indexed_apply_spans(self):
        values = np.asarray([1, 2, 3, 3, 2, 1, 1, 2, 2, 1, 1], dtype=np.int32)
        spans = np.asarray([0, 3, 6, 8, 10, 11], dtype=np.int32)
        dest = np.zeros(len(spans)-1, dtype=np.int32)
        ops.apply_spans_index_of_min(spans, values, dest)
        self.assertTrue(np.array_equal(dest, np.asarray([0, 5, 6, 9, 10], dtype=np.int32)))
        ops.apply_spans_index_of_max(spans, values, dest)
        self.assertTrue(np.array_equal(dest, np.asarray([2, 3, 7, 8, 10], dtype=np.int32)))
        ops.apply_spans_index_of_first(spans, dest)
        self.assertTrue(np.array_equal(dest, np.asarray([0, 3, 6, 8, 10], dtype=np.int32)))
        ops.apply_spans_index_of_last(spans, dest)
        self.assertTrue(np.array_equal(dest, np.asarray([2, 5, 7, 9, 10], dtype=np.int32)))


    def test_non_indexed_apply_spans_filter(self):
        values = np.asarray([1, 2, 3, 3, 2, 1, 1, 2, 2, 1, 1], dtype=np.int32)
        spans = np.asarray([0, 3, 6, 8, 10, 11], dtype=np.int32)
        dest = np.zeros(len(spans)-1, dtype=np.int32)
        flt = np.zeros(len(spans)-1, dtype=np.int32)
        ops.apply_spans_index_of_min_filter(spans, values, dest, flt)
        self.assertTrue(np.array_equal(dest, np.asarray([0, 5, 6, 9, 10], dtype=np.int32)))
        self.assertTrue(np.array_equal(flt, np.asarray([1, 1, 1, 1, 1], dtype=np.bool)))
        ops.apply_spans_index_of_max_filter(spans, values, dest, flt)
        self.assertTrue(np.array_equal(dest, np.asarray([2, 3, 7, 8, 10], dtype=np.int32)))
        self.assertTrue(np.array_equal(flt, np.asarray([1, 1, 1, 1, 1], dtype=np.bool)))
        ops.apply_spans_index_of_first_filter(spans, dest, flt)
        self.assertTrue(np.array_equal(dest, np.asarray([0, 3, 6, 8, 10], dtype=np.int32)))
        self.assertTrue(np.array_equal(flt, np.asarray([1, 1, 1, 1, 1], dtype=np.bool)))
        ops.apply_spans_index_of_last_filter(spans, dest, flt)
        self.assertTrue(np.array_equal(dest, np.asarray([2, 5, 7, 9, 10], dtype=np.int32)))
        self.assertTrue(np.array_equal(flt, np.asarray([1, 1, 1, 1, 1], dtype=np.bool)))

        spans = np.asarray([0, 3, 3, 6, 8, 8, 10, 11], dtype=np.int32)
        dest = np.zeros(len(spans)-1, dtype=np.int32)
        flt = np.zeros(len(spans)-1, dtype=np.int32)
        ops.apply_spans_index_of_min_filter(spans, values, dest, flt)
        self.assertTrue(np.array_equal(dest, np.asarray([0, 0, 5, 6, 0, 9, 10], dtype=np.int32)))
        self.assertTrue(np.array_equal(flt, np.asarray([1, 0, 1, 1, 0, 1, 1], dtype=np.bool)))
        ops.apply_spans_index_of_max_filter(spans, values, dest, flt)
        self.assertTrue(np.array_equal(dest, np.asarray([2, 0, 3, 7, 0, 8, 10], dtype=np.int32)))
        self.assertTrue(np.array_equal(flt, np.asarray([1, 0, 1, 1, 0, 1, 1], dtype=np.bool)))
        ops.apply_spans_index_of_first_filter(spans, dest, flt)
        self.assertTrue(np.array_equal(dest, np.asarray([0, 0, 3, 6, 0, 8, 10], dtype=np.int32)))
        self.assertTrue(np.array_equal(flt, np.asarray([1, 0, 1, 1, 0, 1, 1], dtype=np.bool)))
        ops.apply_spans_index_of_last_filter(spans, dest, flt)
        self.assertTrue(np.array_equal(dest, np.asarray([2, 0, 5, 7, 0, 9, 10], dtype=np.int32)))
        self.assertTrue(np.array_equal(flt, np.asarray([1, 0, 1, 1, 0, 1, 1], dtype=np.bool)))


    def test_ordered_map_valid_stream(self):
        s = session.Session()
        bio = BytesIO()
        with h5py.File(bio, 'w') as hf:
            map_field = np.asarray([0, 0, 0, 1, 1, 3, 3, 3, 3, 5, 5, 5, 5,
                                    ops.INVALID_INDEX, ops.INVALID_INDEX, 7, 7, 7],
                                   dtype=np.int64)
            data_field = np.asarray([-1, -2, -3, -4, -5, -6, -8, -9], dtype=np.int32)
            f_map_field = s.create_numeric(hf, "map_field", "int64")
            f_map_field.data.write(map_field)
            f_data_field = s.create_numeric(hf, "data_field", "int32")
            f_data_field.data.write(data_field)

            result_field = np.zeros(len(map_field), dtype=np.int32)
            ops.ordered_map_valid_stream(f_data_field, f_map_field, result_field, 4)
            expected = np.asarray([-1, -1, -1, -2, -2, -4, -4, -4, -4, -6, -6, -6, -6, 0, 0, -9, -9, -9],
                                  dtype=np.int32)
            self.assertTrue(np.array_equal(result_field, expected))


    def test_ordered_map_to_right_both_unique(self):
        raw_ids = [0, 1, 2, 3, 5, 6, 7, 9]
        a_ids = np.asarray(raw_ids, dtype=np.int64)
        b_ids = np.asarray([1, 2, 3, 4, 5, 7, 8, 9], dtype=np.int64)
        results = np.zeros(len(b_ids), dtype=np.int64)
        ops.ordered_map_to_right_both_unique(b_ids, a_ids, results)
        expected = np.array([1, 2, 3, ops.INVALID_INDEX, 4, 6, ops.INVALID_INDEX, 7],
                            dtype=np.int64)
        self.assertTrue(np.array_equal(results, expected))

    def test_ordered_map_to_right_right_unique(self):
        raw_ids = [0, 1, 2, 3, 5, 6, 7, 9]
        a_ids = np.asarray(raw_ids, dtype=np.int64)
        b_ids = np.asarray([1, 2, 3, 4, 5, 7, 8, 9], dtype=np.int64)
        results = np.zeros(len(b_ids), dtype=np.int64)
        ops.ordered_map_to_right_right_unique(b_ids, a_ids, results)
        expected = np.array([1, 2, 3, ops.INVALID_INDEX, 4, 6, ops.INVALID_INDEX, 7],
                            dtype=np.int64)
        self.assertTrue(np.array_equal(results, expected))


    def test_ordered_map_to_right_left_unique_streamed(self):
        s = session.Session()
        bio = BytesIO()
        with h5py.File(bio, 'w') as hf:
            a_ids = np.asarray([0, 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18],
                               dtype=np.int64)
            b_ids = np.asarray([0, 1, 1, 2, 4, 5, 5, 6, 8, 9, 9, 10, 12, 13, 13, 14,
                                16, 17, 17, 18], dtype=np.int64)
            a_ids_f = s.create_numeric(hf, 'a_ids', 'int64')
            a_ids_f.data.write(a_ids)
            b_ids_f = s.create_numeric(hf, 'b_ids', 'int64')
            b_ids_f.data.write(b_ids)
            left_to_right_result = s.create_numeric(hf, 'left_result', 'int64')
            ops.ordered_map_to_right_right_unique_streamed(a_ids_f, b_ids_f,
                                                       left_to_right_result)
            expected = np.asarray([0, 1, 3, ops.INVALID_INDEX, 5, 7, ops.INVALID_INDEX, 8, 11,
                                   ops.INVALID_INDEX, 12, 13, ops.INVALID_INDEX, 16, 17, 19])
            self.assertTrue(np.array_equal(left_to_right_result.data[:], expected))


    def test_ordered_inner_map_result_size(self):
        a_ids = np.asarray([0, 1, 2, 2, 3, 5, 5, 5, 6, 8], dtype=np.int64)
        b_ids = np.asarray([1, 1, 2, 3, 5, 5, 6, 7, 8, 8, 8], dtype=np.int64)
        result_size = ops.ordered_inner_map_result_size(a_ids, b_ids)
        self.assertEqual(15, result_size)
        result_size = ops.ordered_inner_map_result_size(b_ids, a_ids)
        self.assertEqual(15, result_size)


    def test_ordered_outer_map_result_size_both_unique(self):
        a_ids = np.asarray([0, 2, 3, 4, 6, 8, 9, 10], dtype=np.int32)
        b_ids = np.asarray([1, 3, 4, 5, 6, 7], dtype=np.int32)

        result_size = ops.ordered_outer_map_result_size_both_unique(a_ids, b_ids)
        self.assertEqual(11, result_size)

        result_size = ops.ordered_outer_map_result_size_both_unique(b_ids, a_ids)
        self.assertEqual(11, result_size)


    def test_ordered_inner_map_both_unique(self):
        a_ids = np.asarray([0, 1, 2, 3, 5, 6, 8], dtype=np.int64)
        b_ids = np.asarray([1, 2, 3, 5, 6, 7, 8], dtype=np.int64)
        result_size = ops.ordered_inner_map_result_size(a_ids, b_ids)

        a_map = np.zeros(result_size, dtype=np.int64)
        b_map = np.zeros(result_size, dtype=np.int64)
        ops.ordered_inner_map_both_unique(a_ids, b_ids, a_map, b_map)
        expected_a = np.array([1, 2, 3, 4, 5, 6], dtype=np.int64)
        expected_b = np.array([0, 1, 2, 3, 4, 6], dtype=np.int64)
        self.assertTrue(np.array_equal(a_map, expected_a))
        self.assertTrue(np.array_equal(b_map, expected_b))

        a_map = np.zeros(result_size, dtype=np.int64)
        b_map = np.zeros(result_size, dtype=np.int64)
        ops.ordered_inner_map_left_unique(a_ids, b_ids, a_map, b_map)
        expected_a = np.array([1, 2, 3, 4, 5, 6], dtype=np.int64)
        expected_b = np.array([0, 1, 2, 3, 4, 6], dtype=np.int64)
        self.assertTrue(np.array_equal(a_map, expected_a))
        self.assertTrue(np.array_equal(b_map, expected_b))

        a_map = np.zeros(result_size, dtype=np.int64)
        b_map = np.zeros(result_size, dtype=np.int64)
        ops.ordered_inner_map(a_ids, b_ids, a_map, b_map)
        expected_a = np.array([1, 2, 3, 4, 5, 6], dtype=np.int64)
        expected_b = np.array([0, 1, 2, 3, 4, 6], dtype=np.int64)
        self.assertTrue(np.array_equal(a_map, expected_a))
        self.assertTrue(np.array_equal(b_map, expected_b))

    def test_ordered_inner_map_left_unique(self):
        a_ids = np.asarray([0, 1, 2, 3, 5, 6, 8], dtype=np.int64)
        b_ids = np.asarray([1, 1, 2, 3, 5, 5, 6, 7, 8, 8, 8], dtype=np.int64)
        result_size = ops.ordered_inner_map_result_size(a_ids, b_ids)

        a_map = np.zeros(result_size, dtype=np.int64)
        b_map = np.zeros(result_size, dtype=np.int64)
        ops.ordered_inner_map_left_unique(a_ids, b_ids, a_map, b_map)
        expected_a = np.array([1, 1, 2, 3, 4, 4, 5, 6, 6, 6], dtype=np.int64)
        expected_b = np.array([0, 1, 2, 3, 4, 5, 6, 8, 9, 10], dtype=np.int64)
        self.assertTrue(np.array_equal(a_map, expected_a))
        self.assertTrue(np.array_equal(b_map, expected_b))

        a_map = np.zeros(result_size, dtype=np.int64)
        b_map = np.zeros(result_size, dtype=np.int64)
        ops.ordered_inner_map(a_ids, b_ids, a_map, b_map)
        expected_a = np.array([1, 1, 2, 3, 4, 4, 5, 6, 6, 6], dtype=np.int64)
        expected_b = np.array([0, 1, 2, 3, 4, 5, 6, 8, 9, 10], dtype=np.int64)
        self.assertTrue(np.array_equal(a_map, expected_a))
        self.assertTrue(np.array_equal(b_map, expected_b))

    def test_ordered_inner_map(self):
        a_ids = np.asarray([0, 1, 2, 2, 3, 5, 5, 5, 6, 8], dtype=np.int64)
        b_ids = np.asarray([1, 1, 2, 3, 5, 5, 6, 7, 8, 8, 8], dtype=np.int64)
        result_size = ops.ordered_inner_map_result_size(a_ids, b_ids)
        a_map = np.zeros(result_size, dtype=np.int64)
        b_map = np.zeros(result_size, dtype=np.int64)
        ops.ordered_inner_map(a_ids, b_ids, a_map, b_map)
        expected_a = np.array([1, 1, 2, 3, 4, 5, 5, 6, 6, 7, 7, 8, 9, 9, 9], dtype=np.int64)
        expected_b = np.array([0, 1, 2, 2, 3, 4, 5, 4, 5, 4, 5, 6, 8, 9, 10], dtype=np.int64)
        self.assertTrue(np.array_equal(a_map, expected_a))
        self.assertTrue(np.array_equal(b_map, expected_b))

    def test_ordered_inner_map_left_unique_streamed(self):
        s = session.Session()
        bio = BytesIO()
        with h5py.File(bio, 'w') as hf:
            a_ids = np.asarray([0, 1, 2, 3, 5, 6, 7, 8, 10, 11, 12, 13, 15, 16, 17, 18],
                               dtype=np.int64)
            b_ids = np.asarray([0, 1, 1, 2, 4, 5, 5, 6, 8, 9, 9, 10, 12, 13, 13, 14,
                                16, 17, 17, 18], dtype=np.int64)
            a_ids_f = s.create_numeric(hf, 'a_ids', 'int64')
            a_ids_f.data.write(a_ids)
            b_ids_f = s.create_numeric(hf, 'b_ids', 'int64')
            b_ids_f.data.write(b_ids)
            left_result = s.create_numeric(hf, 'left_result', 'int64')
            right_result = s.create_numeric(hf, 'right_result', 'int64')
            ops.ordered_inner_map_left_unique_streamed(a_ids_f, b_ids_f,
                                                       left_result, right_result)
            left_expected = np.asarray([0, 1, 1, 2, 4, 4, 5, 7, 8, 10, 11, 11, 13, 14, 14, 15], dtype=np.int32)
            self.assertTrue(np.array_equal(left_result.data[:], left_expected))
            right_expected = np.asarray([0, 1, 2, 3, 5, 6, 7, 8, 11, 12, 13, 14, 16, 17, 18, 19], dtype=np.int32)
            self.assertTrue(np.array_equal(right_result.data[:], right_expected))


    def test_ordered_get_last_as_filter_all_unique(self):
        field = np.asarray([b'ab', b'af', b'be', b'ez'])
        result = ops.ordered_get_last_as_filter(field)
        expected = np.asarray([True, True, True, True])
        self.assertTrue(np.array_equal(result, expected))


    def test_ordered_get_last_as_filter(self):
        field = np.asarray([b'ab', b'ab', b'af', b'be', b'be', b'ez', b'ez'])
        result = ops.ordered_get_last_as_filter(field)
        expected = np.asarray([False, True, True, False, True, False, True])
        self.assertTrue(np.array_equal(result, expected))


    def test_ordered_generate_journalling_indices(self):
        old = np.asarray([0, 0, 0, 1, 1, 2, 3, 3, 5, 5, 5], dtype=np.int32)
        new = np.asarray([0, 2, 3, 4, 5, 6], dtype=np.int32)
        old_i, new_i = ops.ordered_generate_journalling_indices(old, new)
        old_expected = np.asarray([2, 4, 5, 7, -1, 10, -1], dtype=np.int32)
        self.assertTrue(np.array_equal(old_i, old_expected))
        new_expected = np.asarray([0, -1, 1, 2, 3, 4, 5], dtype=np.int32)
        self.assertTrue(np.array_equal(new_i, new_expected))


    def test_compare_rows_for_journalling(self):
        old = np.asarray([0, 0, 0, 1, 1, 2, 3, 3, 5, 5, 5], dtype=np.int32)
        new = np.asarray([0, 2, 3, 4, 5, 6], dtype=np.int32)
        old_i, new_i = ops.ordered_generate_journalling_indices(old, new)

        old_expected = np.asarray([2, 4, 5, 7, -1, 10, -1], dtype=np.int32)
        self.assertTrue(np.array_equal(old_i, old_expected))
        new_expected = np.asarray([0, -1, 1, 2, 3, 4, 5], dtype=np.int32)
        self.assertTrue(np.array_equal(new_i, new_expected))

        old_data = np.asarray([0, 1, 2, 10, 11, 20, 30, 31, 50, 51, 52])
        new_data = np.asarray([2, 20, 31, 40, 52, 60])
        to_keep = np.zeros(len(new_i), dtype=np.bool)
        ops.compare_rows_for_journalling(old_i, new_i, old_data, new_data, to_keep)
        expected = np.asarray([False, False, False, False, True, False, True])
        self.assertTrue(np.array_equal(to_keep, expected))

        old_data = np.asarray([0, 1, 2, 10, 11, 20, 30, 31, 50, 51, 52])
        new_data = np.asarray([3, 21, 32, 41, 53, 61])
        to_keep = np.zeros(len(new_i), dtype=np.bool)
        ops.compare_rows_for_journalling(old_i, new_i, old_data, new_data, to_keep)
        expected = np.asarray([True, False, True, True, True, True, True])
        self.assertTrue(np.array_equal(to_keep, expected))


    def test_merge_journalled_entries(self):
        old = np.asarray([0, 0, 0, 1, 1, 2, 3, 3, 5, 5, 5], dtype=np.int32)
        new = np.asarray([0, 2, 3, 4, 5, 6], dtype=np.int32)
        old_i, new_i = ops.ordered_generate_journalling_indices(old, new)

        old_data = np.asarray([0, 1, 2, 10, 11, 20, 30, 31, 50, 51, 52])
        new_data = np.asarray([2, 20, 31, 40, 52, 60])
        to_keep = np.zeros(len(new_i), dtype=np.bool)
        ops.compare_rows_for_journalling(old_i, new_i, old_data, new_data, to_keep)

        dest = np.zeros(len(old) + to_keep.sum(), dtype=old.dtype)
        ops.merge_journalled_entries(old_i, new_i, to_keep, old_data, new_data, dest)
        expected = np.asarray([0, 1, 2, 10, 11, 20, 30, 31, 40, 50, 51, 52, 60], dtype=np.int32)
        self.assertTrue(np.array_equal(dest, expected))

        old_data = np.asarray([0, 1, 2, 10, 11, 20, 30, 31, 50, 51, 52])
        new_data = np.asarray([3, 21, 32, 40, 53, 60])
        to_keep = np.zeros(len(new_i), dtype=np.bool)
        ops.compare_rows_for_journalling(old_i, new_i, old_data, new_data, to_keep)

        dest = np.zeros(len(old) + to_keep.sum(), dtype=old.dtype)
        ops.merge_journalled_entries(old_i, new_i, to_keep, old_data, new_data, dest)
        expected = np.asarray([0, 1, 2, 3, 10, 11, 20, 21, 30, 31, 32, 40, 50, 51, 52, 53, 60], dtype=np.int32)
        self.assertTrue(np.array_equal(dest, expected))


    def test_merge_indexed_journalled_entries_count(self):
        old = np.asarray([0, 0, 0, 1, 1, 2, 3, 3, 5, 5, 5], dtype=np.int32)
        new = np.asarray([0, 2, 3, 4, 5, 6], dtype=np.int32)
        old_i, new_i = ops.ordered_generate_journalling_indices(old, new)

        old_inds = np.asarray([0, 2, 4, 6, 9, 12, 14, 17, 20, 23, 26, 29])
        old_vals = np.frombuffer(
            b''.join([b'aa', b'ab', b'ac', b'baa', b'bab', b'ca', b'daa', b'dab',
                      b'faa', b'fab', b'fac']), dtype='S1')
        expected_inds = np.asarray([0, 2, 4, 6, 9, 12, 14, 17, 20, 23, 26, 29], dtype=np.int32)
        expected_vals = np.asarray([b'a', b'a', b'a', b'b', b'a', b'c', b'b', b'a', b'a',
                                    b'b', b'a', b'b', b'c', b'a', b'd', b'a', b'a', b'd', b'a', b'b',
                                    b'f', b'a', b'a', b'f', b'a', b'b', b'f', b'a', b'c'], dtype='S1')
        self.assertTrue(np.array_equal(old_inds, expected_inds))
        self.assertTrue(np.array_equal(old_vals, expected_vals))


        new_inds = np.asarray([0, 2, 4, 7, 9, 12, 14])
        new_vals = np.frombuffer(
            b''.join([b'ad', b'cb', b'dac', b'ea', b'fad', b'ga']), dtype='S1')
        to_keep = np.zeros(len(new_i), dtype=np.bool)
        ops.compare_indexed_rows_for_journalling(old_i, new_i, old_inds, old_vals,
                                                 new_inds, new_vals, to_keep)

        count = ops.merge_indexed_journalled_entries_count(old_i, new_i, to_keep,
                                                           old_inds, new_inds)
        self.assertTrue(np.array_equal(count, 43))


    def test_merge_indexed_journalled_entries(self):
        old = np.asarray([0, 0, 0, 1, 1, 2, 3, 3, 5, 5, 5], dtype=np.int32)
        new = np.asarray([0, 2, 3, 4, 5, 6], dtype=np.int32)
        old_i, new_i = ops.ordered_generate_journalling_indices(old, new)

        old_inds = np.asarray([0, 2, 4, 6, 9, 12, 14, 17, 20, 23, 26, 29])
        old_vals = np.frombuffer(
            b''.join([b'aa', b'ab', b'ac', b'baa', b'bab', b'ca', b'daa', b'dab',
                      b'faa', b'fab', b'fac']), dtype='S1')
        expected_inds = np.asarray([0, 2, 4, 6, 9, 12, 14, 17, 20, 23, 26, 29], dtype=np.int32)
        expected_vals = np.asarray([b'a', b'a', b'a', b'b', b'a', b'c', b'b', b'a', b'a',
                                    b'b', b'a', b'b', b'c', b'a', b'd', b'a', b'a', b'd', b'a', b'b',
                                    b'f', b'a', b'a', b'f', b'a', b'b', b'f', b'a', b'c'], dtype='S1')
        self.assertTrue(np.array_equal(old_inds, expected_inds))
        self.assertTrue(np.array_equal(old_vals, expected_vals))
        new_inds = np.asarray([0, 2, 4, 7, 9, 12, 14])
        new_vals = np.frombuffer(
            b''.join([b'ad', b'cb', b'dac', b'ea', b'fad', b'ga']), dtype='S1')
        to_keep = np.zeros(len(new_i), dtype=np.bool)
        ops.compare_indexed_rows_for_journalling(old_i, new_i, old_inds, old_vals,
                                                 new_inds, new_vals, to_keep)

        dest_inds = np.zeros(len(old) + to_keep.sum() + 1, dtype=old.dtype)
        val_count = ops.merge_indexed_journalled_entries_count(old_i, new_i, to_keep,
                                                               old_inds, new_inds)
        dest_vals = np.zeros(val_count, dtype='S1')
        ops.merge_indexed_journalled_entries(old_i, new_i, to_keep, old_inds, old_vals,
                                             new_inds, new_vals, dest_inds, dest_vals)
        expected_inds = \
            np.asarray([0, 2, 4, 6, 8, 11, 14, 16, 18, 21, 24, 27, 29, 32, 35, 38, 41, 43],
                       dtype=np.int32)
        self.assertTrue(np.array_equal(dest_inds, expected_inds))
        expected_vals = \
            np.frombuffer(
                b''.join([b'aa', b'ab', b'ac', b'ad', b'baa', b'bab', b'ca', b'cb',
                          b'daa', b'dab', b'dac', b'ea' b'faa', b'fab', b'fac', b'fad', b'ga']),
                dtype='S1')
        self.assertTrue(np.array_equal(dest_vals, expected_vals))
        # old_data = np.asarray([0, 1, 2, 10, 11, 20, 30, 31, 50, 51, 52])
        # new_data = np.asarray([3, 21, 32, 40, 53, 60])
        # to_keep = np.zeros(len(new_i), dtype=np.bool)
        # ops.compare_rows_for_journalling(old_i, new_i, old_data, new_data, to_keep)
        #
        # dest = np.zeros(len(old_data) + to_keep.sum(), dtype=old.dtype)
        # ops.merge_journalled_entries(old_i, new_i, to_keep, old_data, new_data, dest)
        # expected = np.asarray([0, 1, 2, 3, 10, 11, 20, 21, 30, 31, 32, 40, 50, 51, 52, 53, 60], dtype=np.int32)
        # self.assertTrue(np.array_equal(dest, expected))


    def test_streaming_sort_merge(self):
        s = session.Session()
        bio = BytesIO()
        with h5py.File(bio, 'w') as hf:
            rs = np.random.RandomState(12345678)
            length = 105
            segment_length = 25
            chunk_length = 8
            src_values = np.arange(length, dtype=np.int32)
            src_values += 1000
            rs.shuffle(src_values)
            src_v_f = s.create_numeric(hf, 'src_values', 'int32')
            src_v_f.data.write(src_values)
            src_i_f = s.create_numeric(hf, 'src_indices', 'int64')
            src_i_f.data.write(np.arange(length, dtype=np.int64))

            for c in utils.chunks(length, segment_length):
                sorted_index = np.argsort(src_v_f.data[c[0]:c[1]])
                src_v_f.data[c[0]:c[1]] =\
                    s.apply_index(sorted_index, src_v_f.data[c[0]:c[1]])
                src_i_f.data[c[0]:c[1]] =\
                    s.apply_index(sorted_index, src_i_f.data[c[0]:c[1]])

            tgt_i_f = s.create_numeric(hf, 'tgt_values', 'int32')
            tgt_v_f = s.create_numeric(hf, 'tgt_indices', 'int64')
            ops.streaming_sort_merge(src_i_f, src_v_f, tgt_i_f, tgt_v_f,
                                     segment_length, chunk_length)

            self.assertTrue(np.array_equal(tgt_v_f.data[:], np.sort(src_values[:])))
            self.assertTrue(np.array_equal(tgt_i_f.data[:], np.argsort(src_values)))


    def test_is_ordered(self):
        arr = np.asarray([1, 2, 3, 4, 5])
        self.assertTrue(ops.is_ordered(arr))

        arr = np.asarray([5, 4, 3, 2, 1])
        self.assertFalse(ops.is_ordered(arr))

        arr = np.asarray([1, 2, 4, 3, 5])
        self.assertFalse(ops.is_ordered(arr))

        arr = np.asarray([1, 1, 1, 1, 1])
        self.assertTrue(ops.is_ordered(arr))
