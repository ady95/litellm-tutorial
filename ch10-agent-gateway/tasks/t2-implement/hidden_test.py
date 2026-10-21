from text_utils import slugify


def test_basic():
    assert slugify("Hello, World!") == "hello-world"


def test_collapse_and_strip():
    assert slugify("  --LiteLLM   Gateway--  ") == "litellm-gateway"


def test_numbers():
    assert slugify("Version 1.106.1 Release") == "version-1-106-1-release"


def test_non_ascii_removed():
    assert slugify("AI 게이트웨이 Gateway") == "ai-gateway"


def test_max_length_no_trailing_hyphen():
    assert slugify("abc def ghi", max_length=8) == "abc-def"


def test_empty():
    assert slugify("!!!") == ""
