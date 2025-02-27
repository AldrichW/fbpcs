# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

from typing import List
from unittest import TestCase
from unittest.mock import Mock
from validation import generate_from_body, ONE_OR_MORE_REQUIRED_FIELDS, ALL_REQUIRED_FIELDS

class TestValidation(TestCase):

    def test_validate_requires_header_row(self):
        body = Mock('body')
        body.iter_lines = self.mock_lines_helper(['bad,header,row','1,2,3'])
        result = generate_from_body(body)
        expected_all_fields = ','.join(sorted(ALL_REQUIRED_FIELDS))
        expected_one_or_more_fields = ','.join(sorted(ONE_OR_MORE_REQUIRED_FIELDS))
        self.assertRegex(result, f'Header row not valid, missing `{expected_all_fields}` required fields')
        self.assertRegex(result, f'Header row not valid, at least one of `{expected_one_or_more_fields}` is required')
        self.assertRegex(result, 'Validation processing stopped.')

    def test_validate_returns_number_of_rows(self):
        body = Mock('body')
        body.iter_lines = self.mock_lines_helper([
            'timestamp,currency_type,conversion_value,event_type,email,action_source,year,month,day,hour',
            '1631204619,usd,5,Purchase,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa11111111111111111111111111111111,website,2021,09,09,16',
            '1631204619,usd,5,Purchase,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa11111111111111111111111111111111,website,2021,09,09,16',
        ])
        result = generate_from_body(body)
        self.assertRegex(result, 'Total rows: 2')
        self.assertRegex(result, 'Valid rows: 2')

    def test_validate_returns_validation_counts(self):
        body = Mock('body')
        body.iter_lines = self.mock_lines_helper([
            'timestamp,currency_type,conversion_value,event_type,email,action_source,year,month,day,hour',
            ',,,,,,,,,',
            '1631204619,usd,5,Purchase,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa11111111111111111111111111111111,website,2021,09,09,16',
            ',,,,,,,,,',
            ',,,,,,,,,',
            '1631204619,usd,5,Purchase,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa11111111111111111111111111111111,website,2021,09,09,16',
        ])
        result = generate_from_body(body)
        self.assertRegex(result, 'Total rows: 5')
        self.assertRegex(result, 'Valid rows: 2')
        self.assertRegex(result, 'Rows with errors: 3')

    def test_validate_fails_when_one_required_field_is_empty(self):
        body = Mock('body')
        body.iter_lines = self.mock_lines_helper([
            'timestamp,currency_type,conversion_value,event_type,email,action_source,device_id,year,month,day,hour',
            ',usd,5,Purchase,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa11111111111111111111111111111111,website,bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb22222222222222222222222222222222,2021,09,09,16',
            '1631204619,,5,Purchase,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa11111111111111111111111111111111,website,bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb22222222222222222222222222222222,2021,09,09,16',
            '1631204619,usd,,Purchase,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa11111111111111111111111111111111,website,bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb22222222222222222222222222222222,2021,09,09,16',
            '1631204619,usd,5,,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa11111111111111111111111111111111,website,bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb22222222222222222222222222222222,2021,09,09,16',
            '1631204619,usd,5,Purchase,,website,,2021,09,09,16',
            '1631204619,usd,5,,aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa11111111111111111111111111111111,,bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb22222222222222222222222222222222,2021,09,09,16',
        ])
        result = generate_from_body(body)
        self.assertRegex(result, 'Total rows: 6')
        self.assertRegex(result, 'Rows with errors: 6')

    def test_validate_handles_quoted_csvs(self):
        body = Mock('body')
        body.iter_lines = self.mock_lines_helper([
            '"timestamp","currency_type","conversion_value","event_type","email","action_source","year","month","day","hour"',
            '"","","","","","","","","",""',
            '"1631204619","usd","5","Purchase","aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa11111111111111111111111111111111","website","2021","09","09","16"',
            '"","","","","","","","","",""',
        ])
        result = generate_from_body(body)
        self.assertRegex(result, 'Total rows: 3')
        self.assertRegex(result, 'Valid rows: 1')
        self.assertRegex(result, 'Rows with errors: 2')

    def mock_lines_helper(self, lines: List[str]) -> Mock:
        encoded_lines = list(map(lambda line: line.encode('utf-8'), lines))
        return Mock(return_value = encoded_lines)
