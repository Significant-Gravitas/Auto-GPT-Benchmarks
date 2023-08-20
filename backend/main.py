from typing import Optional
import sys
import os

from pathlib import Path

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from fastapi import FastAPI, Query
from agbenchmark.start_benchmark import run_from_backend
from agbenchmark.utils.utils import find_absolute_benchmark_path
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = ["http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Change the current working directory to the benchmark path
home_path = find_absolute_benchmark_path()
os.chdir(home_path)


@app.get("/run_single_test")
def run_single_test(
    test: str = Query(...),
    mock: bool = Query(False),
    nc: bool = Query(False),
    cutoff: int = Query(None),
):
    return run_from_backend(test=test, mock=mock, nc=nc, cutoff=cutoff)


@app.get("/run_suite")
def run_suite(
    suite: str = Query(...),
    mock: bool = Query(False),
    nc: bool = Query(False),
    cutoff: int = Query(None),
):
    return run_from_backend(suite=suite, mock=mock, nc=nc, cutoff=cutoff)


@app.get("/run_by_category")
def run_by_category(
    category: list[str] = Query(...),  # required
    mock: bool = Query(False),
    nc: bool = Query(False),
    cutoff: int = Query(None),
):
    return run_from_backend(
        category=category,
        mock=mock,
        nc=nc,
        cutoff=cutoff,
    )


@app.get("/run")
def run(
    maintain: bool = Query(False),
    improve: bool = Query(False),
    explore: bool = Query(False),
    mock: bool = Query(False),
    no_dep: bool = Query(False),
    nc: bool = Query(False),
    category: list[str] = Query(None),
    skip_category: list[str] = Query(None),
    test: str = Query(None),
    suite: str = Query(None),
    cutoff: int = Query(None),
):
    return run_from_backend(
        maintain=maintain,
        improve=improve,
        explore=explore,
        mock=mock,
        no_dep=no_dep,
        nc=nc,
        category=category,
        skip_category=skip_category,
        test=test,
        suite=suite,
        cutoff=cutoff,
    )
