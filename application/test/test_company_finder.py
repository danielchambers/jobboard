import re
import pytest
from application.periodic_tasks.task_utilities.company_finder import CompanyFinder


generic_config = {
    'search_query': 'site:boards.greenhouse.io {}',
    'url_pattern': r"boards\.greenhouse\.io\/(?P<company_name>\w+)",
    'url_format': 'https://boards-api.greenhouse.io/v1/boards/{}/jobs/',
}

myworkdayjobs_config = {
    'search_query': 'site:myworkdayjobs.com {}',
    'url_pattern': r'(?P<company_name>\w+)\.(?P<company_region>\w+)\.myworkdayjobs\.com\/(?:[a-z]{2}-[A-Z]{2}\/)?(?P<company_uri>\w[\w\-]*|(?!.*\/)([^\/?#]+))',
    'url_format': 'https://{company_name}.{company_region}.myworkdayjobs.com/wday/cxs/{company_name}/{company_uri}/jobs',
}


@pytest.fixture
def generic_company_finder():
    return CompanyFinder("greenhouse", generic_config)


@pytest.fixture
def myworkdayjobs_company_finder():
    return CompanyFinder("myworkdayjobs", myworkdayjobs_config)


def test_init_company_finder():
    platform = "greenhouse"
    platform_config = generic_config
    finder = CompanyFinder(platform, platform_config)
    assert finder.platform == platform
    assert finder.platform_config == platform_config
    assert finder.unique_companies == set()
    assert finder.companies == []


def test_parse_invalid_platform_config(generic_company_finder):
    generic_company_finder.platform_config = None
    links = ["https://example.com/company1"]
    with pytest.raises(ValueError, match=f"Invalid job board: {generic_company_finder.platform}"):
        generic_company_finder.parse(links)


def test_generic_parse_valid_links(generic_company_finder):
    links = [
        'https://boards.greenhouse.io/florenceeu/jobs/4293156005',
        'https://boards.greenhouse.io/theroom/jobs/4933606',
        'https://boards.greenhouse.io/inworldai/jobs/4048091007',
        'https://boards.greenhouse.io/mercury/jobs/4956856004'
    ]
    companies = generic_company_finder.parse(links)
    assert len(companies) == 4
    assert companies[0]['name'] == "florenceeu"
    assert companies[1]['name'] == "theroom"
    assert companies[2]['name'] == "inworldai"
    assert companies[3]['name'] == "mercury"


def test_generic_parse_invalid_links(generic_company_finder):
    links = [
        "https://invalid-link.com",
        'https://boards.greenhouse.io/florenceeu/jobs/4293156005',
    ]
    companies = generic_company_finder.parse(links)
    assert len(companies) == 1
    assert companies[0]['name'] == "florenceeu"
    assert companies[0]['url'] == "https://boards-api.greenhouse.io/v1/boards/florenceeu/jobs/"
    assert companies[0]['platform'] == "greenhouse"


def test_process_company_match(generic_company_finder):
    link = 'https://boards.greenhouse.io/florenceeu/jobs/4293156005'
    config = generic_company_finder.platform_config
    match = re.search(config['url_pattern'], link)
    assert match
    generic_company_finder._process_company_match(match, config['url_format'])
    assert len(generic_company_finder.companies) == 1
    assert generic_company_finder.companies[0]['name'] == "florenceeu"
    assert generic_company_finder.companies[0]['url'] == "https://boards-api.greenhouse.io/v1/boards/florenceeu/jobs/"
    assert generic_company_finder.companies[0]['platform'] == "greenhouse"


def test_process_myworkdayjob_match(myworkdayjobs_company_finder):
    link = 'https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite/'
    config = myworkdayjobs_company_finder.platform_config
    match = re.search(config['url_pattern'], link)
    assert match
    myworkdayjobs_company_finder._process_myworkdayjob_match(match)
    assert len(myworkdayjobs_company_finder.companies) == 1
    print(myworkdayjobs_company_finder.companies)
    assert myworkdayjobs_company_finder.companies[0]['name'] == "nvidia"
    assert myworkdayjobs_company_finder.companies[0][
        'url'] == "https://nvidia.wd5.myworkdayjobs.com/wday/cxs/nvidia/NVIDIAExternalCareerSite/jobs"
    assert myworkdayjobs_company_finder.companies[0]['platform'] == "myworkdayjobs"


def test_process_myworkdayjob_match_invalid_match(myworkdayjobs_company_finder):
    match = None
    myworkdayjobs_company_finder._process_myworkdayjob_match(match)
    assert len(myworkdayjobs_company_finder.companies) == 0
