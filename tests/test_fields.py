import pytest

from personal_assistant.models.fields import Address, Birthday, Email, Name, Phone, Tag


class TestName:
    def test_valid(self):
        assert Name("John").value == "John"

    def test_strips_whitespace(self):
        assert Name("  Andrew  ").value == "Andrew"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            Name("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            Name("   ")

    def test_setter_validates(self):
        field = Name("Valid")
        with pytest.raises(ValueError):
            field.value = ""


class TestPhone:
    def test_international_format(self):
        assert Phone("+380991112233").value == "+380991112233"

    def test_local_format(self):
        assert Phone("0991112233").value == "0991112233"

    def test_short_number_raises(self):
        with pytest.raises(ValueError):
            Phone("12345")

    def test_letters_raise(self):
        with pytest.raises(ValueError):
            Phone("phone12345")

    def test_wrong_country_code_raises(self):
        with pytest.raises(ValueError):
            Phone("+381991112233")


class TestEmail:
    def test_valid(self):
        assert Email("user@example.com").value == "user@example.com"

    def test_no_at_raises(self):
        with pytest.raises(ValueError):
            Email("userexample.com")

    def test_no_domain_raises(self):
        with pytest.raises(ValueError):
            Email("user@")

    def test_strips_whitespace(self):
        assert Email("  user@example.com  ").value == "user@example.com"


class TestAddress:
    def test_valid(self):
        assert Address("Kyiv, Main St 1").value == "Kyiv, Main St 1"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            Address("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            Address("   ")


class TestBirthday:
    def test_valid_past_date(self):
        assert Birthday("10.10.2000").value == "10.10.2000"

    def test_wrong_format_raises(self):
        with pytest.raises(ValueError):
            Birthday("2000-10-10")

    def test_future_date_raises(self):
        with pytest.raises(ValueError):
            Birthday("01.01.2099")

    def test_invalid_day_raises(self):
        with pytest.raises(ValueError):
            Birthday("32.13.2020")


class TestTag:
    def test_normalizes_to_lowercase(self):
        assert Tag("Python").value == "python"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            Tag("")

    def test_spaces_in_tag_raise(self):
        with pytest.raises(ValueError):
            Tag("hello world")

    def test_too_long_raises(self):
        with pytest.raises(ValueError):
            Tag("a" * 31)

    def test_allows_underscore_and_hyphen(self):
        assert Tag("my-tag_1").value == "my-tag_1"

    def test_equality_case_insensitive(self):
        assert Tag("python") == Tag("Python")

    def test_hash_consistent_with_equality(self):
        assert hash(Tag("python")) == hash(Tag("Python"))
