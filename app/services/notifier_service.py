from typing import Any
import yaml
from app.config.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()

class NotifierService:
    """
        NotifierService
        A service class for managing and checking project alerts based on configured thresholds.
        This service reads alert configurations from a YAML file and compares project metrics
        against defined thresholds to identify when alerts should be triggered.
        Attributes:
            logger: Logger instance for tracking service operations and errors.
        Methods:
            __init__(): Initializes the NotifierService and sets up logging.
            check_alerts(project_id: str, scores: dict[Any, Any]): 
                Checks if any project metrics fall below configured alert thresholds.
                Args:
                    project_id (str): The unique identifier for the project to check alerts for.
                    scores (dict[Any, Any]): A dictionary containing metric names as keys and 
                        their corresponding score values.
                Raises:
                    Logs an error message if any metric score is below its configured threshold.
        """

    def __init__(self):
        """
        Initialize the NotifierService.
        Sets up the logger instance for the service and logs the initialization event.
        """

        self.logger = get_logger(__name__)
        self.logger.info("NotifierService initialised")

    def check_alerts(self,project_id:str,scores:dict[Any, Any]):
        """
            Check if project metrics fall below configured alert thresholds.
            Loads alert threshold configuration from a YAML file and compares the provided
            metric scores against the thresholds for the specified project. Logs errors when
            any metric score falls below its configured threshold.
            Args:
                project_id (str): The unique identifier of the project to check alerts for.
                scores (dict[Any, Any]): A dictionary containing metric names as keys and their
                                         corresponding scores as values.
            Returns:
                None
            Raises:
                FileNotFoundError: If the alert configuration file at settings.project_alert_config_path
                                  does not exist.
                yaml.YAMLError: If the YAML file is malformed or cannot be parsed.
            Note:
                - Logs info messages for project lookup and configuration loading.
                - Logs error messages when metrics fall below their thresholds.
                - Uses a default threshold of 1.0 for metrics not provided in scores.
            """

        self.logger.info(f"checking alert for project_id: {project_id}")
        with open(file = settings.project_alert_config_path) as f:
            thresholds = yaml.safe_load(f)
        
        self.logger.info(f"threshold for project_id {project_id} = {thresholds}")
        project_rules = thresholds.get(project_id, {})

        for metric, threshold in project_rules.items():
            if scores.get(metric, 1) < threshold:
                self.logger.error(f"For project: {project_id} Metric: {metric} score is < than {threshold}.")
