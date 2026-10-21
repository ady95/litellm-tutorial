from config_check import validate


def test_ok():
    cfg = {"model_list": [{"model_name": "fast", "litellm_params": {"model": "openai/gpt-6-luna", "api_key": "os.environ/OPENAI_API_KEY"}}]}
    assert validate(cfg) == []


def test_empty():
    assert validate({}) == ["model_list is empty"]
    assert validate({"model_list": []}) == ["model_list is empty"]


def test_entry_errors():
    cfg = {"model_list": [
        {"litellm_params": {"model": "gpt-6-luna", "api_key": "sk-plain"}},
        {"model_name": "x", "litellm_params": {}},
    ]}
    assert validate(cfg) == [
        "entry 0: missing model_name",
        "entry 0: model must have provider prefix",
        "entry 0: api_key must use os.environ/",
        "entry 1: missing litellm_params.model",
    ]


def test_duplicate():
    e = {"model_name": "fast", "litellm_params": {"model": "openai/a"}}
    assert validate({"model_list": [e, dict(e)]}) == ["entry 1: duplicate model_name fast"]
