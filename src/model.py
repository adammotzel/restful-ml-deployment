from typing import List, Dict, Iterable
import pickle as pkl

import pandas as pd


class ModelWrapper:
    """
    A wrapper class for a model to customize the `predict()` method.

    This class wraps a machine learning model to enable customized input 
    handling, specifically converting API request data (typically in JSON 
    format) into a Numpy array before passing it to the model (the wrapped 
    model's `predict()` method expects a Numpy array as input).

    Parameters
    ----------
    path : str
        File path to the fitted model object (pickled model file).
    """

    def __init__(self, path: str):
        """
        Initializes the model wrapper by loading the model from the provided 
        file path.

        Parameters
        ----------
        path : str
            File path to the fitted model object.
        """
        with open(path, "rb") as file:
            self.model = pkl.load(file)

        self.feature_names = [
            feat.replace(" ", "_") for feat in self.model.variable_names
        ]

    def predict(self, data: Dict[str, List[float]]) -> List[float]:
        """
        Perform inference on a dataset by converting the input data to a 
        numpy array and passing it to the model's `predict()` method.

        Parameters
        ----------
        data : dict of {str: list of float}
            Data to score. Each key represents a feature name, and the 
            corresponding value is a list of feature values. All lists in 
            the dictionary must be of equal length and non-empty.

        Example
        -------
        data = {
            "mean_radius": [1, 2, 3],
            "mean_texture": [1, 2, 3],
            "mean_perimeter": [1, 2, 3],
            ...
        }

        Returns
        -------
        list of float
            A list of predicted values. The length of this list will match 
            the length of the input feature arrays.
        """
        data_matrix = pd.DataFrame(data).to_numpy()
        return self.model.predict(data_matrix).flatten().tolist()


def transform_data(
        data: dict, 
        feature_order: Iterable[str], 
        observations: int
) -> List[List[str]]:
    """
    Custom function used to transform the API request payload into 
    lists of string values, to be written to a CSV file.

    Parameters
    ----------
    data : dict
        The API request data that will be passed to the model.
    feature_order : Iterable[str]
        Column order for writing the results to a CSV file.
    observations : int
        Number of observations in the request data.

    Returns
    -------
    List[List[str]]
        List of 'rows' for the CSV file.

    Example
    -------
    data = {
        "mean_radius": [12.34, 15.67, 10.11],
        "mean_texture": [19.54, 17.33, 18.45],
        "mean_perimeter": [78.12, 85.67, 70.22],
        "mean_area": [523.45, 600.34, 490.12]
    }

    >>> _tranform(data, data.keys(), 3)

    [
        [12.34, 19.54, 78.12, 523.45], 
        [15.67, 17.33, 85.67, 600.34], 
        [10.11, 18.45, 70.22, 490.12]
    ]

    """
    return [
        [
            str(data[feature][obs]) for feature in feature_order
        ] 
        for obs in range(observations)
    ]
