"""Tests for teaching error mapping."""

import pytest
import requests
from mcp.shared.exceptions import McpError
from mcp.types import INTERNAL_ERROR, INVALID_PARAMS

from translator_component_toolkit.errors import (
    InvalidParameterError,
    format_choices,
    to_mcp_error,
    validate_choice,
)


def test_validate_choice_passes_for_valid_value():
    validate_choice("a", ["a", "b"], "param")  # should not raise


def test_validate_choice_enumerates_valid_values():
    with pytest.raises(InvalidParameterError) as exc:
        validate_choice("z", ["a", "b"], "api_name")
    msg = str(exc.value)
    assert "api_name" in msg
    assert "'a'" in msg and "'b'" in msg


def test_format_choices_is_bounded():
    rendered = format_choices([str(i) for i in range(50)], limit=20)
    assert "+30 more" in rendered


def test_invalid_parameter_error_maps_to_invalid_params():
    err = to_mcp_error(InvalidParameterError("bad"), "query_kp")
    assert isinstance(err, McpError)
    assert err.error.code == INVALID_PARAMS
    assert "query_kp" in err.error.message


def test_lookup_error_maps_to_invalid_params():
    err = to_mcp_error(LookupError("no match for 'AML'"), "lookup_name")
    assert err.error.code == INVALID_PARAMS
    assert "no match" in err.error.message


def test_request_exception_maps_to_internal_error_with_status():
    response = requests.Response()
    response.status_code = 503
    exc = requests.HTTPError("service unavailable")
    exc.response = response
    err = to_mcp_error(exc, "get_kp_info")
    assert err.error.code == INTERNAL_ERROR
    assert "HTTP 503" in err.error.message


def test_unknown_exception_maps_to_internal_error():
    err = to_mcp_error(RuntimeError("boom"), "normalize_nodes")
    assert err.error.code == INTERNAL_ERROR
    assert "boom" in err.error.message


def test_query_kp_adapter_validates_api_name():
    from translator_component_toolkit.schema import _query_knowledge_provider

    with pytest.raises(InvalidParameterError):
        _query_knowledge_provider("UnknownAPI", {}, {"Real API": "http://x"}, {})
