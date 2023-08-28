from application.periodic_tasks.task_utilities.company_finder import CompanyFinder


def test_no_results():
    results = []
    platform = 'greenhouse'
    platform_config = {
        'search_query': 'site:boards.greenhouse.io {}',
        'url_pattern': r"boards\.greenhouse\.io\/(?P<company_name>\w+)",
        'url_format': 'https://boards-api.greenhouse.io/v1/boards/{}/jobs/',
    }
    company_finder = CompanyFinder(platform, platform_config)
    companies = company_finder.parse(results)
    assert len(companies) == 0


def test_greenhouse_results():
    results = ['https://boards.greenhouse.io/florenceeu/jobs/4293156005', 'https://boards.greenhouse.io/theroom/jobs/4933606',
               'https://boards.greenhouse.io/inworldai/jobs/4048091007', 'https://boards.greenhouse.io/mercury/jobs/4956856004']
    platform = 'greenhouse'
    platform_config = {
        'search_query': 'site:boards.greenhouse.io {}',
        'url_pattern': r"boards\.greenhouse\.io\/(?P<company_name>\w+)",
        'url_format': 'https://boards-api.greenhouse.io/v1/boards/{}/jobs/',
    }
    company_finder = CompanyFinder(platform, platform_config)
    companies = company_finder.parse(results)
    assert len(companies) == 4
    assert companies[0]['name'] == "florenceeu"
    assert companies[0]['url'] == "https://boards-api.greenhouse.io/v1/boards/florenceeu/jobs/"
    assert companies[0]['platform'] == "greenhouse"


def test_lever_results():
    results = ['https://jobs.lever.co/octoenergy/37eeec91-cec2-40e3-9b5e-808971f5d790', 'https://jobs.lever.co/lumeto/376aec07-9a68-46f0-a83f-03b52e11d9f2',
               'https://jobs.lever.co/octoenergy/4b7fed29-e318-4f85-9639-7a4d53455b09', 'https://jobs.lever.co/octoenergy/dfe481ab-3b68-4fd0-bd99-0ee2ea980909']
    platform = 'lever'
    platform_config = {
        'search_query': 'site:jobs.lever.co {}',
        'url_pattern': r"jobs\.lever\.co\/(?P<company_name>\w+)",
        'url_format': 'https://jobs.lever.co/v0/postings/{}/?mode=json',
    }
    company_finder = CompanyFinder(platform, platform_config)
    companies = company_finder.parse(results)
    assert len(companies) == 2
    assert companies[0]['name'] == "octoenergy"
    assert companies[0]['url'] == "https://jobs.lever.co/v0/postings/octoenergy/?mode=json"
    assert companies[0]['platform'] == "lever"


def test_careerpuck_results():
    results = ['https://app.careerpuck.com/job-board/lyft', 'https://app.careerpuck.com/job-board/coursehero/job/5024252',
               'https://app.careerpuck.com/job-board/coursehero/job/5024250', 'https://app.careerpuck.com/job-board/trustly/job/5cb3a67b-70a7-4946-b826-41813142c26e']
    platform = 'careerpuck'
    platform_config = {
        'search_query': 'site:app.careerpuck.com/job-board/ {}',
        'url_pattern': r"app\.careerpuck\.com\/job-board\/(?P<company_name>\w+)",
        'url_format': 'https://api.careerpuck.com/v1/public/job-boards/{}',
    }
    company_finder = CompanyFinder(platform, platform_config)
    companies = company_finder.parse(results)
    assert len(companies) == 3
    assert companies[0]['name'] == "lyft"
    assert companies[0]['url'] == "https://api.careerpuck.com/v1/public/job-boards/lyft"
    assert companies[0]['platform'] == "careerpuck"


def test_ashbyhq_results():
    results = ['https://jobs.ashbyhq.com/Keyrock/1b2e9707-b81d-4018-8db4-6683d8811d4c', 'https://jobs.ashbyhq.com/firstbase/b10f4228-750f-454d-822f-787d6936902d',
               'https://jobs.ashbyhq.com/productperfect/4fc1be0a-92d0-4946-b5d7-e902ba3ef3ec', 'https://jobs.ashbyhq.com/outliant/a9e4c641-631a-4fbb-a234-fc0773184d62']
    platform = 'ashbyhq'
    platform_config = {
        'search_query': 'site:jobs.ashbyhq.com {}',
        'url_pattern': r"jobs\.ashbyhq\.com\/(?P<company_name>\w+)",
        'url_format': 'https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams',
    }
    company_finder = CompanyFinder(platform, platform_config)
    companies = company_finder.parse(results)
    assert len(companies) == 4
    assert companies[0]['name'] == "Keyrock"
    assert companies[0]['url'] == "https://jobs.ashbyhq.com/api/non-user-graphql?op=ApiJobBoardWithTeams"
    assert companies[0]['platform'] == "ashbyhq"


def test_myworkdayjobs_results():
    results = ['https://rappi.wd3.myworkdayjobs.com/es/Rappi_jobs/job/COL-Bogot/Backend-Developer-Nodejs_JR103653', 'https://relx.wd3.myworkdayjobs.com/de-DE/LexisNexisLegal/job/Sr-Backend-Developer-Remote_R18434-1', 'https://valeo.wd3.myworkdayjobs.com/valeo_jobs/job/Prague/SW-Backend-Developer-with-Python_REQ2023018389',
               'https://harman.wd3.myworkdayjobs.com/pl-PL/HARMAN/job/Bangalore---Karnataka-India---EOIZ-Industrial-Area/Sr-Java-Backend-Developer_R-29109-2023', 'https://valeo.wd3.myworkdayjobs.com/it-IT/valeo_jobs/job/SW-Backend-Developer-with-Python_REQ2023018389']
    platform = 'myworkdayjobs'
    platform_config = {
        'search_query': 'site:myworkdayjobs.com {}',
        'url_pattern': r'(?P<company_name>\w+)\.(?P<company_region>\w+)\.myworkdayjobs\.com\/(?:[a-z]{2}-[A-Z]{2}\/)?(?P<company_uri>\w[\w\-]*|(?!.*\/)([^\/?#]+))',
        'url_format': 'https://{company_name}.{company_region}.myworkdayjobs.com/wday/cxs/{company_name}/{company_uri}/jobs',
    }
    company_finder = CompanyFinder(platform, platform_config)
    companies = company_finder.parse(results)
    assert len(companies) == 4
    assert companies[0]['name'] == "rappi"
    assert companies[0]['url'] == "https://rappi.wd3.myworkdayjobs.com/wday/cxs/rappi/es/jobs"
    assert companies[0]['platform'] == "myworkdayjobs"
