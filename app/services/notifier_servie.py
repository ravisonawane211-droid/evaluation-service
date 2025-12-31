from typing import Any
import yaml
from app.config.config import get_settings
from app.utils.logger import get_logger

settings = get_settings()

class NotifierService:
    def __init__(self):
        self.logger = get_logger(__name__)
        self.logger.info("NotifierService initialised")

    def check_alerts(self,project_id:str,scores:dict[Any, Any]):
        self.logger.info(f"checking alert for project_id: {project_id}")
        with open(file = settings.project_alert_config_path) as f:
            thresholds = yaml.safe_load(f)
        
        self.logger.info(f"threshold for project_id {project_id} = {thresholds}")
        project_rules = thresholds.get(project_id, {})

        for metric, threshold in project_rules.items():
            if scores.get(metric, 1) < threshold:
                self.logger.error(f"For project: {project_id} Metric: {metric} score is < than {threshold}.")
