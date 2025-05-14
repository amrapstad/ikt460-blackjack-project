import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

TABLES_DIR = os.path.join(ROOT_DIR, "OptimalTables")
CSV_DIR = os.path.join(ROOT_DIR, "CSV")
PLOTS_DIR = os.path.join(ROOT_DIR, "Plots")

EVALUATION_DIR = os.path.join(PLOTS_DIR, "Evaluation")
TRAINING_DIR = os.path.join(PLOTS_DIR, "Training")
