import logging
import os
from datetime import datetime

class LogManager:
    def __init__(self, prefix="app_M1", log_dir="Logs"):
        self.log_dir = log_dir
        os.makedirs(self.log_dir, exist_ok=True)

        self.date_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_filename = os.path.join(self.log_dir, f"{prefix}_{self.date_time_str}.log")
        self._configure_logging()
    
    def _configure_logging(self):
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename=self.log_filename,
            filemode='a',
            encoding="utf-8"  # 添加 encoding="utf-8"
        )
    
    @staticmethod
    def get_logger():
        return logging.getLogger()

# # 使用示例
# if __name__ == "__main__":
#     log_manager = LogManager()
#     logger = log_manager.get_logger()
#     logger.info("logger 初始化成功！")