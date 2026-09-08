from csv_file_parser import clean_city_record, clean_coordinate


def test_clean_city_record_strips_whitespace_and_title_cases():
    assert clean_city_record("  new york  ") == "New York"


def test_clean_city_record_removes_special_characters():
    assert clean_city_record("chicago!!") == "Chicago"


def test_clean_city_record_collapses_multiple_spaces():
    assert clean_city_record("los    angeles") == "Los Angeles"


def test_clean_city_record_idempotent_on_already_clean_input():
    assert clean_city_record("Tokyo") == "Tokyo"


def test_clean_city_record_empty_string():
    assert clean_city_record("") == ""


def test_clean_city_record_only_special_characters():
    assert clean_city_record("!@#$%^&*()") == ""


def test_clean_coordinate_strips_whitespace():
    assert clean_coordinate("  40.7128  ") == "40.7128"


def test_clean_coordinate_preserves_decimal_point():
    assert clean_coordinate("-74.0060") == "-74.0060"


def test_clean_coordinate_removes_special_characters():
    assert clean_coordinate("40.7128!@#") == "40.7128"


def test_clean_coordinate_collapses_multiple_spaces():
    assert clean_coordinate("40.7128   ") == "40.7128"


def test_clean_coordinate_empty_string():
    assert clean_coordinate("") == ""
