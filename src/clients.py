import os
import csv
from typing import List, Callable
from datetime import datetime
import logging

from src.model import transform_data


class DataCollectionClient:
    """
    A client class for capturing model inputs/predictions and logging them 
    to CSV files.

    Each class instantiation creates a CSV file in the specified `storage_dir`
    with the date + time of instantiation in the file name. The idea is to create 
    a new CSV file for each app session to better separate requests.

    This is essentially a lightweight local filesystem 'database'. It is an in-memory + 
    local filesystem solution, so it's not a fault-tolerant storage system like a true 
    database.

    Attributes
    ----------
    columns : list of str
        The list of column names to be used in the CSV file.
    storage_path : str
        The full path to the storage file, including the timestamp.

    Methods
    -------
    collect(data)
        Collect data in file buffer. Flushes buffered data to disk when the buffer size 
        exceeds input parameter `buffer`.
    close()
        Flush buffer and close file.
    """

    def __init__(
        self, 
        columns: List[str], 
        storage_dir: str,
        logger: logging.Logger,
        transform_func: Callable = transform_data,
        buffer: int = 5
    ):
        """
        Initializes the client with the provided parameters and prepares a CSV 
        file for logging data.

        Parameters
        ----------
        columns : list of str
            The list of column names to be used in the CSV file.
        storage_dir : str
            The directory path where the CSV file will be stored.
        logger : logging.Logger
            Logger instance to logging messages.
        transform_func : Callable, optional
            A function to transform the data before logging it (default is 
            `transform_data`). This must be specific to the model being 
            monitored.
        buffer : int, default=5
            Max buffer size before flushing buffer to disk.
        """

        self.columns = columns

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.storage_path = os.path.join(
            storage_dir, 
            f"monitoring_data_{timestamp}.csv"
        )

        self._logger = logger
        self._transform = transform_func
        self._buffer = buffer
        self._buffer_size = 0
        self._file = open(self.storage_path, mode="a", newline="")
        self._writer = csv.writer(self._file)

        self._writer.writerow(columns)
        self._file.flush()

    def collect(self, data: dict):
        """
        Collect the observations and predictions in the CSV file.

        Parameters
        ----------
        data : dict
            A dictionary containing the data to be logged. The keys 
            should correspond to the feature names, and the values 
            should be lists of observations.

        Notes
        -----
        This method will transform the data using the provided `transform_func`, 
        then write the transformed data into the CSV file.
        """

        try:
            obs = len(data[self.columns[0]])
            new_data = self._transform(data, self.columns, obs)

            for data_row in new_data:
                self._writer.writerow(data_row)
                self._buffer_size += 1

            if self._buffer_size >= self._buffer:
                self._logger.info("DataCollectionClient buffer is full. Flushing data to disk.")
                self._file.flush()
                self._buffer_size = 0

        except Exception as e:
            self._logger.error(f"Error collecting data: {e}")

    def close(self):
        """Flush remaining buffer and close the file."""

        try:
            self._file.flush()
            self._file.close()
        except Exception as e:
            self._logger.error(f"Error closing DataCollectionClient: {e}")


class LoggingClient:
    """
    A client class to handle all logging. This class abstracts away all logging 
    configuration operations and manages log storage.

    A FileHandler is used by default to stream logs to a .log file. A StreamHandler 
    can be optionally added.

    Attributes
    ----------
    name : str
        The name of the logger.
    level : int
        The logging level.
    log_format : str
        The format of log messages.
    storage_path : str
        The path to the log file.
    console_logs : bool
        If logs are printed to the console.

    Proprties
    ---------
    logger
        Returns the logger instance.
    """

    def __init__(
        self, 
        name: str, 
        storage_dir: str, 
        level: int = logging.INFO,
        log_format: str = "%(asctime)s | File: %(filename)s | Level: %(levelname)s | Log: %(message)s",
        console_logs: bool = True
    ):
        """
        Initializes the LoggingClient instance.

        Parameters
        ----------
        name : str
            The name of the logger.
        storage_dir : str
            The directory where log files will be stored.
        level : int, optional
            The logging level (default is logging.INFO).
        log_format : str, optional
            The format for the log messages. Default is: 
            "%(asctime)s | Logger: %(name)s | Level: %(levelname)s | Log: %(message)s"
        console_logs : bool, default=False
            Optionally output logs to the console. This is useful for dev.
        """
        self.name = name
        self.level = level
        self.log_format = log_format
        self.console_logs = console_logs

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.storage_path = os.path.join(
            storage_dir, 
            f"app_{timestamp}.log"
        )

        self._logger = self._create_logger()

    @property
    def logger(self) -> logging.Logger:
        """
        Returns the logger instance.

        Returns
        -------
        logging.Logger
            The logger instance used for logging messages.
        """
        return self._logger

    def _create_logger(self) -> logging.Logger:
        """
        Creates a logger with a file handler (for logging to a file) and an optional
        stream handler (for logging to the console). Handlers are set to the specified 
        logging level and use the provided format.

        Returns
        -------
        logging.Logger
            The configured logger instance.
        """
        logger = logging.getLogger(self.name)
        logger.setLevel(self.level)

        fh = logging.FileHandler(self.storage_path)
        fh.setLevel(self.level)

        formatter = logging.Formatter(
            self.log_format, 
            datefmt="%Y-%m-%d_%H-%M-%S"
        )
        fh.setFormatter(formatter)

        logger.addHandler(fh)

        if self.console_logs:
            sh = logging.StreamHandler()
            sh.setLevel(self.level)
            sh.setFormatter(formatter)
            logger.addHandler(sh)

        return logger
