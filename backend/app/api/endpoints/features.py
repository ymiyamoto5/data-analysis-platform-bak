import re

import pandas as pd
from backend.elastic_manager.elastic_manager import ElasticManager
from fastapi import APIRouter
from fastapi.exceptions import HTTPException

router = APIRouter()


@router.get("/list")
def fetch_features():
    """特徴量の一覧を返す"""

    df = ElasticManager.show_indices()
    indices = [*filter(None, [re.search(r"^shots-(.*)-(\d{14})-.*-point$", i) for i in df["index"]])]

    feature_list = set([ind.groups() for ind in indices])

    return {"data": feature_list}


@router.get("/")
def fetch_feature(machine_id: str, target_dir: str):
    df = ElasticManager.show_indices()
    indices = df["index"][df["index"].str.contains(f"^shots-{machine_id}-{target_dir}-.+-point$")]
    feature = {}
    for ind in indices:
        feature_label = re.search(rf"^shots-{machine_id}-{target_dir}-(.*-point$)", ind)
        if feature_label is not None:
            feature_label = feature_label.groups()[0]
        else:
            continue

        query = {"sort": {"shot_number": {"order": "asc"}}}
        docs = ElasticManager.scan_docs(index=ind, query=query, preserve_order=True)
        docs_df = pd.DataFrame(docs)
        feature.update({f"{load}_{feature_label}": docs_df[docs_df["load"] == load]["value"].tolist() for load in docs_df["load"].unique()})

    return {"data": feature}


@router.get("/raw/list")
def fetch_rawdata_list():
    df = ElasticManager.show_indices()
    indices = [*filter(None, [re.search(r"^shots-(.*)-(\d{14})-data$", i) for i in df["index"]])]

    data_list = set([ind.groups() for ind in indices])

    return {"data": data_list}


@router.get("/raw/length")
def fetch_number_of_shots(machine_id: str, target_dir: str):
    index = f"shots-{machine_id}-{target_dir}-data"
    query = {"aggs": {"shot_numbers": {"terms": {"field": "shot_number", "size": 1000}}}}
    docs = ElasticManager.es.search(index=index, body=query, size=0)

    shots = [d["key"] for d in docs["aggregations"]["shot_numbers"]["buckets"]]

    return {"shots": shots}


@router.get("/label")
def fetch_label(machine_id: str, target_dir: str):
    ind = f"shots-{machine_id}-{target_dir}-meta"
    query = {"sort": {"shot_number": {"order": "asc"}}}
    docs = ElasticManager.get_docs(index=ind, query=query)

    labels = [d["label"] for d in docs if "label" in d]

    if labels == []:
        raise HTTPException(status_code=500, detail="正解ラベルがありません")

    return {"labels": labels}
