import os
from typing import List

import docker  # type: ignore
import mlflow  # type: ignore
import pandas as pd
from backend.app.api.endpoints import features
from backend.app.schemas import model
from backend.app.services.bento_service import ModelClassifier
from backend.elastic_manager.elastic_manager import ElasticManager
from fastapi import APIRouter
from mlflow.tracking import MlflowClient  # type: ignore
from sklearn.covariance import EllipticEnvelope  # type: ignore

router = APIRouter()
docker_client = docker.DockerClient(base_url="unix://run/docker.sock")

mlflow_server_uri = os.environ["mlflow_server_uri"]
mlflow_experiment_name = os.environ["mlflow_experiment_name"]

mlflow.set_tracking_uri(mlflow_server_uri)
mlflow.sklearn.autolog()

# TODO: 対応アルゴリズムの取得自動化
algorithms = [
    {
        "algorithm_name": "EllipticEnvelope",
        "params": [
            {"name": "contamination", "min": 0.01, "max": 0.5, "step": 0.01},
        ],
    },
]

models = {"EllipticEnvelope": EllipticEnvelope}


@router.get("/algorithm", response_model=List[model.Algorithm])
def fetch_algorithms():
    """対応している機械学習アルゴリズム一覧を返す"""

    return algorithms


@router.get("/algorithm/{algorithm_name}", response_model=model.Algorithm)
def fetch_algorithm(algorithm_name: str):
    """指定した機械学習アルゴリズム情報を返す"""

    algorithm = next((algo for algo in algorithms if algo["algorithm_name"] == algorithm_name), None)

    return algorithm


@router.get("/")
def fetch_models():
    """MLFlowに登録されたモデルの一覧を返す"""

    client = MlflowClient()
    return [m.name for m in client.list_registered_models()]


@router.get("/versions")
def fetch_versions(model: str):
    """指定したモデルのバージョン一覧を返す"""

    client = MlflowClient()
    return [mv.version for mv in client.search_model_versions(f"name='{model}'")]


@router.post("/")
def create(create_model: model.CreateModel):
    """モデルの作成"""
    mlflow.set_experiment(mlflow_experiment_name)

    feature = features.fetch_feature(machine_id=create_model.machine_id, target_dir=create_model.target_dir)
    X = pd.DataFrame(feature["data"])
    model = models[create_model.algorithm](**create_model.params)

    with mlflow.start_run() as run:
        model.fit(X)

    return {"res": "OK"}


@router.get("/containers")
def fetch_containers():
    imgs = [
        i.tags[0] for i in docker_client.images.list() if "bentoml/model-server" not in i.tags[0] and "docker.elastic.co" not in i.tags[0]
    ]

    containers = []
    for img in imgs:
        running_instance = [*filter(lambda c: c.image.tags[0] == img, docker_client.containers.list())]
        state, name = ["running", running_instance[0].name] if running_instance else ["stopping", ""]
        containers.append({"image": img, "state": state, "name": name})

    return {"data": containers}


@router.post("/container")
def create_container(create_container: model.CreateContainer):

    createModel = mlflow.sklearn.load_model(model_uri=f"models:/{create_container.model}/{create_container.version}")

    # Create a iris classifier service instance
    model_classifier_service = ModelClassifier()

    # Pack the newly trained model artifact
    model_classifier_service.pack("model", createModel)

    # Save the prediction service to disk for model serving
    saved_path = model_classifier_service.save()

    docker_client.images.build(path=saved_path, tag=create_container.tag_name.lower(), rm=True)
    # yatai_client = get_yatai_client()
    # yatai_client.repository.delete(prune=True)

    return {"data": "OK"}


@router.put("/container/run/{image}/{port}")
def container_state_change(image: str, port: str):
    ports = {"5000/tcp": str(port)}
    instance = docker_client.containers.run(image, auto_remove=True, detach=True, ports=ports)
    container = {"image": image, "state": "running", "name": instance.name}
    return {"data": container}


@router.put("/container/stop/{name}")
def container_stop(name: str):
    instance = docker_client.containers.get(name)
    instance.stop()
    container = {
        "image": instance.image.tags[0],
        "state": "stopping",
        "name": "",
    }
    return {"data": container}


@router.delete("/container/{image}")
def delete_container(image: str):
    docker_client.images.remove(image)

    return {"data": "OK"}


@router.post("/predict")
def predict_label(predict: model.Predict):
    df = ElasticManager.show_indices()
    indices = df["index"][df["index"].str.contains(f"^shots-{predict.machine_id}-{predict.target_dir}-.+-point$")]

    data = {}
    for ind in indices:
        query = {"query": {"match": {"shot_number": predict.shot}}}
        docs = ElasticManager.es.search(index=ind, body=query)
        feature_name = ind.split("-")[-2]
        data.update({f"{d['_source']['load']}_{feature_name}-point": d["_source"]["value"] for d in docs["hits"]["hits"]})

    createModel = mlflow.sklearn.load_model(model_uri=f"models:/{predict.model}/{predict.version}")
    df = pd.DataFrame.from_dict(data, orient="index").T
    result = createModel.predict(df).tolist()

    return {"data": data, "label": result}
