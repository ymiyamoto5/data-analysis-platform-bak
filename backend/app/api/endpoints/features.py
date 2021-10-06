import re

import pandas as pd
from backend.elastic_manager.elastic_manager import ElasticManager
from fastapi import APIRouter

router = APIRouter()


@router.get("/list")
def fetch_features():
    """特徴量の一覧を返す"""

    df = ElasticManager.show_indices()
    indices = [
        *filter(
            None, [re.search(r"^shots-(.*)-(\d{14})-.*-point$", i) for i in df["index"]]
        )
    ]

    feature_list = set([ind.groups() for ind in indices])

    return {"data": feature_list}


@router.get("/")
def fetch_feature(machine_id: str, target_dir: str):
    df = ElasticManager.show_indices()
    indices = df["index"][
        df["index"].str.contains(f"^shots-{machine_id}-{target_dir}-.+-point$")
    ]
    feature = {}
    for ind in indices:
        feature_label = re.search(rf"^shots-{machine_id}-{target_dir}-(.*-point$)", ind)
        if feature_label is not None:
            feature_label = feature_label.groups()[0]
        else:
            continue

        query = {"sort": {"shot_number": {"order": "asc"}}}
        docs = ElasticManager.get_docs(index=ind, query=query)
        docs_df = pd.DataFrame(docs)
        feature.update(
            {
                f"{load}_{feature_label}": docs_df[docs_df["load"] == load][
                    "value"
                ].tolist()
                for load in docs_df["load"].unique()
            }
        )

    return {"data": feature}
