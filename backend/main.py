from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from fastapi import FastAPI, Query
from agbenchmark.start_benchmark import start
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


@app.get("/run_single_test")
def run_single_test(
    test: str = Query(...),
    mock: bool = Query(False),
    nc: bool = Query(False),
    cutoff: int = Query(None),
):
    return start(test=test, mock=mock, nc=nc, cutoff=cutoff)


@app.get("/run_suite")
def run_suite(
    suite: str = Query(...),
    mock: bool = Query(False),
    nc: bool = Query(False),
    cutoff: int = Query(None),
):
    return start(suite=suite, mock=mock, nc=nc, cutoff=cutoff)


@app.get("/run_by_category")
def run_by_category(
    category: str = Query(...),  # required
    mock: bool = Query(False),
    nc: bool = Query(False),
    cutoff: int = Query(None),
):
    return start(
        category=category,
        mock=mock,
        nc=nc,
        cutoff=cutoff,
    )


@app.get("/run/")
def run(
    category: Optional[list[str]] = Query(None),
    skip_category: Optional[list[str]] = Query(None),
    test: Optional[str] = None,
    maintain: Optional[bool] = False,
    improve: Optional[bool] = False,
    explore: Optional[bool] = False,
    mock: Optional[bool] = False,
    suite: Optional[str] = None,
    no_dep: Optional[bool] = False,
    nc: Optional[bool] = False,
    cutoff: Optional[int] = None,
):
    # Call the `start` function with appropriate parameters.
    # For simplicity, I'm just returning a message. You can replace this with the actual call.
    return {
        "message": "Generic run",
        "category": category,
        "skip_category": skip_category,
        "test": test,
        "maintain": maintain,
        "improve": improve,
        "explore": explore,
        "mock": mock,
        "suite": suite,
        "no_dep": no_dep,
        "nc": nc,
        "cutoff": cutoff,
    }
