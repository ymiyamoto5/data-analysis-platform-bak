import pandas as pd
from bentoml import BentoService, api, artifacts, env  # type: ignore
from bentoml.adapters import DataframeInput  # type: ignore
from bentoml.frameworks.sklearn import SklearnModelArtifact  # type: ignore


@env(infer_pip_packages=True)
@artifacts([SklearnModelArtifact("model")])
class ModelClassifier(BentoService):
    """
    A minimum prediction service exposing a Scikit-learn model
    """

    @api(input=DataframeInput(), batch=True)
    def predict(self, df: pd.DataFrame):
        """
        An inference API named `predict` with Dataframe input adapter, which codifies
        how HTTP requests or CSV files are converted to a pandas Dataframe object as the
        inference API function input
        """
        return self.artifacts.model.predict(df)
