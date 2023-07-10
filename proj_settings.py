import os



class MainSettings:
    PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))
    settings_dir = os.path.join(PROJECT_DIR, "settings")
    output_dir = os.path.join(PROJECT_DIR, 'output')
    settings_json_file_path =  os.path.join(settings_dir, "settings.json")
    # settings_file_path = os.path.join(settings_dir, "settings.csv")
    # settings_hsv_path = os.path.join(settings_dir, "settings_hsv.csv")

class SeedHealth:
    NORMAL_SEED = 'NORMAL_SEED'
    ABNORMAL_SEED = 'ABNORMAL_SEED'
    DEAD_SEED = 'DEAD_SEED'