# Name      : conftest
# Author    : Patrick Cronin
# Date      : 19/08/2025
# Updated   : 19/08/2025
# Purpose   : Helping CI wipe it's bottom

import sys
import pytest

@pytest.fixture(autouse=True)
def _cleanup_modules():
    for name in ('website.views', 'website.models','website.userrolewrappers', 'website.auth', 'website.inspections', 'website.csp'):
        sys.modules.pop(name, None)
    yield
    for name in ('website.views', 'website.models','website.userrolewrappers', 'website.auth', 'website.inspections', 'website.csp'):
        sys.modules.pop(name, None)
