import pytest
from unittest.mock import patch, Mock
from application.periodic_tasks.task_utilities.google_search import GoogleSearch


@pytest.fixture
def google_search_instance():
    # Mock the API key and engine ID
    with patch("os.getenv") as mock_getenv:
        mock_getenv.side_effect = lambda key: {
            "GOOGLE_SEARCH_API_KEY": "your_mocked_api_key",
            "GOOGLE_SEARCH_ENGINE_ID": "your_mocked_engine_id"
        }.get(key)
        yield GoogleSearch()


def test_successful_search(google_search_instance):
    # Mock the response of the requests.get call
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [{"link": "http://example.com"}]
        }
        mock_get.return_value = mock_response
        result = google_search_instance.search("test query")
    assert isinstance(result, dict)
    assert "items" in result


def mock_search_response(items, next_page_token=None):
    return {
        "items": items,
        "queries": {
            "nextPage": [{"startIndex": 11, "startPage": 2}]
        } if next_page_token else {}
    }


def test_pagination(google_search_instance):
    # Mock the responses for the requests.get calls
    with patch("requests.get") as mock_get:
        # First page
        mock_get.side_effect = [
            Mock(json=lambda: mock_search_response(
                [{"link": "http://example.com/1"}]))
        ]
        result = google_search_instance.search("test query")

        # Second page
        mock_get.side_effect = [
            Mock(json=lambda: mock_search_response(
                [{"link": "http://example.com/2"}], next_page_token="page2token"))
        ]
        result_next_page = google_search_instance.search("test query")

    assert isinstance(result, dict)
    assert "items" in result
    assert isinstance(result_next_page, dict)
    assert "items" in result_next_page
    assert result_next_page["items"][0]["link"] == "http://example.com/2"


def test_search_error_handling(google_search_instance):
    # Mock an error response from requests.get
    with patch("requests.get") as mock_get:
        mock_get.side_effect = Exception("Mocked error")

        try:
            result = google_search_instance.search("test query")
        except Exception as e:
            assert str(e) == "Mocked error"  # Assert the exception message
        else:
            pytest.fail("Expected an exception to be raised")
