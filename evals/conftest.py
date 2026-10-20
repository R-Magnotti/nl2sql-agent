'''
fixtures for the eval suite. session-scoped on purpose: building an embedder is
the expensive part, so every case for a given (model, variant) shares one.
'''
import pytest

from evals.embedding import MODELS, Scored, load, score_all
from evals.dataset import VARIANTS
from evals.judging import JUDGES


@pytest.fixture(scope="session", params=MODELS, ids=MODELS)
def model(request):
    return request.param, load(request.param)


@pytest.fixture(scope="session", params=VARIANTS, ids=VARIANTS)
def scored(request, model):
    model_name, m = model
    return Scored(model_name, request.param,
                  score_all(m, request.param, model_name))


@pytest.fixture(scope="session", params=JUDGES, ids=JUDGES)
def judge(request):
    return JUDGES[request.param]
