# Tripwire Battery RUL Workspace

Tripwire is the integrated team workspace for battery Remaining Useful Life (RUL) prediction, business valuation, and supporting analytics for the Enduraverse-26 hackathon.

This folder now combines three connected tracks:

- `business-relevance/`: business-facing certification, valuation, and fleet assessment layer
- `data/`: dataset generation and simulation utilities
- `models/`: model experimentation and packaged model deliverables

## What This Workspace Contains

### 1. Business Relevance

`business-relevance/` contains the business translation layer built on top of RUL outputs. It focuses on:

- converting technical battery health signals into decision-ready outputs
- fleet assessment and valuation workflows
- certification and reporting artifacts
- Streamlit-based business dashboard flows

Key files:

- `business-relevance/app.py`
- `business-relevance/config.py`
- `business-relevance/quickstart.py`
- `business-relevance/API_REFERENCE.md`
- `business-relevance/DELIVERY_SUMMARY.md`

### 2. Data Utilities

`data/` currently contains the synthetic battery data generator used to support experimentation and testing:

- `data/synthetic_battery_rul_sim.py`

This script is the starting point for generating or extending synthetic battery lifecycle data for model development.

### 3. Model Packages

`models/` contains three packaged model tracks, each organized as a standalone deliverable:

- `models/model-1-random-forest/`
- `models/model-2-hist-gradient-boosting/`
- `models/model-xg-boost/`

Each model package generally includes:

- `dashboard/`: Streamlit app entrypoint
- `data/`: example datasets and static analysis assets
- `docs/`: model-specific documentation
- `models/`: saved metadata or model artifacts
- `results/`: evaluation outputs and judge-facing reports
- `src/`: modeling and preprocessing logic
- `utils/`: helper modules
- `train_model.py`: training entrypoint
- `predict_rul.py`: prediction entrypoint
- `run_pipeline.py`: end-to-end pipeline runner

## Model Summary

### Model 1: Random Forest

`models/model-1-random-forest/` is the first packaged baseline for tabular battery RUL prediction.

Highlights:

- classical ensemble baseline
- packaged training and prediction flow
- dashboard wrapper for model-focused inspection
- includes generated outputs and supporting documentation

### Model 2: Hist Gradient Boosting

`models/model-2-hist-gradient-boosting/` is the second model package focused on a compact boosting-based tabular pipeline.

Highlights:

- stronger structured-data learner than the baseline
- packaged smoke-test style training and prediction flow
- same delivery layout as Model 1 for consistent judging and review

### Model 3: XGBoost

`models/model-xg-boost/` is the currently selected advanced model package and includes the lightened commit-ready project structure.

Highlights:

- end-to-end RUL pipeline
- train, predict, and dashboard entrypoints
- packaged docs and metadata
- selective `.gitignore` rules to exclude heavy generated artifacts from version control

## Recommended Entry Points

If you are exploring the workspace for the first time, use this order:

1. Read this file for the workspace overview
2. Open `business-relevance/README.md` for the product and valuation context
3. Open the relevant model package README inside `models/`
4. Run the package-specific training, prediction, or dashboard commands from the chosen model folder

## How To Run

There is no single root command for the entire Tripwire workspace because each model package is self-contained.

General workflow:

1. change into the model folder you want to run
2. create and activate a virtual environment
3. install that package's requirements
4. run training, prediction, or dashboard commands from inside that folder

Example for the XGBoost package:

```powershell
cd Teams\01-Tripwire\models\model-xg-boost
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python run_pipeline.py
python train_model.py --data data/example_midc_dataset.csv
python predict_rul.py --data data/example_midc_dataset.csv
streamlit run dashboard/app.py
```

Example for the business relevance dashboard:

```powershell
cd Teams\01-Tripwire\business-relevance
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

## Repository Notes

- Some model folders currently contain generated outputs, notebooks, cached files, and local virtual environments from experimentation.
- The XGBoost package has already been trimmed with package-local ignore rules so large generated artifacts do not need to be pushed.
- Shared top-level documentation should describe the workspace as a whole; model-specific README files should remain inside each model package.

## Suggested Navigation

- Workspace overview: `Teams/01-Tripwire/README.MD`
- Business track: `Teams/01-Tripwire/business-relevance/README.md`
- Data generator: `Teams/01-Tripwire/data/synthetic_battery_rul_sim.py`
- Model 1 package: `Teams/01-Tripwire/models/model-1-random-forest/README.md`
- Model 2 package: `Teams/01-Tripwire/models/model-2-hist-gradient-boosting/README.md`
- Model 3 package: `Teams/01-Tripwire/models/model-xg-boost/README.md`

## Current Shape Of The Deliverable

The merged Tripwire folder is not a single app. It is a combined hackathon workspace with:

- a business impact and certification layer
- a synthetic data generation layer
- multiple model tracks for comparison and final selection

That makes this README the workspace index, not the README for one model alone.
