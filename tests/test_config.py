"""Tests for the shared HTTP timeout configuration."""

from unittest.mock import Mock, patch

from translator_component_toolkit import config, name_resolver, trapi


def test_default_timeout_when_env_unset():
    with patch.dict("os.environ", {}, clear=True):
        assert config.http_timeout() == config.DEFAULT_HTTP_TIMEOUT


def test_env_override_is_used():
    with patch.dict("os.environ", {"TCT_HTTP_TIMEOUT": "5"}, clear=True):
        assert config.http_timeout() == 5.0


def test_unparsable_env_falls_back_to_default():
    with patch.dict("os.environ", {"TCT_HTTP_TIMEOUT": "soon"}, clear=True):
        assert config.http_timeout() == config.DEFAULT_HTTP_TIMEOUT


def test_non_positive_env_falls_back_to_default():
    with patch.dict("os.environ", {"TCT_HTTP_TIMEOUT": "0"}, clear=True):
        assert config.http_timeout() == config.DEFAULT_HTTP_TIMEOUT


def test_get_call_passes_timeout():
    response = Mock()
    response.json.return_value = {"status": "ok"}
    with patch.object(name_resolver.requests, "get", return_value=response) as get:
        name_resolver.status()
    assert get.call_args.kwargs["timeout"] == config.DEFAULT_HTTP_TIMEOUT


def test_post_call_passes_timeout():
    response = Mock()
    response.status_code = 200
    response.json.return_value = {"message": {"knowledge_graph": {"edges": {"e00": {}}}}}
    with patch.object(trapi.requests, "post", return_value=response) as post:
        trapi.query("http://example/query", {"message": {}})
    assert post.call_args.kwargs["timeout"] == config.DEFAULT_HTTP_TIMEOUT


def test_call_honors_env_override():
    response = Mock()
    response.json.return_value = {"status": "ok"}
    with patch.dict("os.environ", {"TCT_HTTP_TIMEOUT": "1.5"}, clear=True):
        with patch.object(name_resolver.requests, "get", return_value=response) as get:
            name_resolver.status()
    assert get.call_args.kwargs["timeout"] == 1.5
