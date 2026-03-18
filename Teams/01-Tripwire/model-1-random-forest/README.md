# Model 1 Random Forest

This package is the final Model 1 bundle for the battery RUL hackathon workspace. It is organized as a standalone deliverable with the same visible project layout pattern used across the team packages, while the underlying runtime logic is delegated to the shared repository code in [src](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\src).

## Purpose

This bundle represents the Stage 1 final model track:

- model family: tabular supervised learning
- final selected estimator: `random_forest`
- primary usage: package-level training/prediction smoke flow, dashboard launch, and judge-facing structure

The package is intended to look and behave like an independent model workspace, but it is still structurally linked to the shared project codebase.

## Technical Summary

- package name: `model-1-random-forest`
- selected estimator: `random_forest`
- prediction task: battery remaining useful life in cycles
- expected target column: `rul_cycles`
- default packaged example input: [data/example_midc_dataset.csv](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\data\example_midc_dataset.csv)

The bundle pipeline follows this order:

1. load and map battery-cycle columns
2. clean missing values
3. add normalized battery features
4. generate derived feature columns
5. compute health-score proxy
6. ensure `rul_cycles` exists
7. run the packaged training wrapper
8. save processed CSV and bundle metadata outputs

## Data Contract

The packaged loader expects a battery-cycle CSV that can be mapped into the canonical fields below:

- `battery_id`
- `cycle`
- `cell_voltage`
- `pack_current`
- `cell_temperature`
- `soc`
- `dod`
- `c_rate`
- `soh_pct`
- `rul_cycles`

The packaged preprocessing path maps these into the engineered tabular representation used by the shared Model 1 logic, including:

- cycle position fields
- voltage/current/temperature summaries
- SOH-to-capacity conversion
- rolling capacity statistics
- operating cohort/load-profile tags
- hybrid stress descriptors such as:
  - `recent_capacity_slope_5`
  - `recent_capacity_slope_10`
  - `temperature_stress_cum`
  - `dod_stress_cum`
  - `c_rate_stress_cum`
  - `physics_proxy_rul`
  - `life_fraction`

## What The Bundle Scripts Do

### [run_pipeline.py](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\run_pipeline.py)

This is the main packaged pipeline entrypoint. It mirrors the same top-level style used in the reference project:

- loads the CSV
- prints the mapped columns
- runs cleaning and feature creation
- calls `train_rul_model(...)`
- writes [results/pipeline_processed.csv](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\results\pipeline_processed.csv)

Current bundle behavior:

- it writes model metadata to [models/rul_model.json](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\models\rul_model.json)
- it does **not** yet write a real local `rul_model.pkl`

### [train_model.py](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\train_model.py)

Thin wrapper that calls the packaged pipeline.

### [predict_rul.py](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\predict_rul.py)

Bundle-local prediction smoke path:

- loads a CSV
- maps and normalizes it
- returns a prediction table
- writes [results/predictions.csv](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\results\predictions.csv)

Current bundle behavior:

- this is a scaffold prediction path
- it is not yet using a trained local serialized model artifact
- the current smoke path mirrors RUL through the wrapper flow so the bundle can be exercised end-to-end

### [dashboard/app.py](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\dashboard\app.py)

Launches the shared Streamlit dashboard with focus on Model 1.

## Bundle Structure

- [dashboard](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\dashboard): packaged Streamlit entrypoint
- [data](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\data): packaged datasets and static assets
- [docs](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\docs): bundle documentation
- [models](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\models): bundle metadata outputs
- [notebooks](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\notebooks): notebook placeholder
- [results](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\results): packaged outputs
- [src](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\src): Abhinav-style module names with wrapper implementations
- [utils](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\utils): utility wrappers
- [model-1-random-forest/results](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\model-1-random-forest\results): nested self-named results placeholder for layout parity

## Files Written During The Smoke Run

After running the package from inside its folder:

```powershell
python run_pipeline.py
python predict_rul.py
```

the bundle produced:

- [results/pipeline_processed.csv](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\results\pipeline_processed.csv)
- [models/rul_model.json](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\models\rul_model.json)
- [results/predictions.csv](C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest\results\predictions.csv)

Observed smoke-run metadata:

- `model_name`: `random_forest`
- `rows`: `1000`
- `artifact_written`: `False`

## Commands

Run the packaged pipeline:

```powershell
cd C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest
python run_pipeline.py
```

Run packaged prediction:

```powershell
cd C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest
python predict_rul.py
```

Launch the bundled dashboard:

```powershell
cd C:\Users\Saarthak\Downloads\DataHack\NASA-Battery-DataSet\model-1-random-forest
streamlit run dashboard\app.py
```

## Current Limitations

- no local `models/rul_model.pkl` yet
- prediction path is a scaffold smoke path, not final isolated bundle inference
- runtime depends on the shared repository `src` tree
- the package is structurally standalone but not yet artifact-isolated

## What Would Make This Fully Standalone Later

- save a real trained Random Forest pipeline to `models/rul_model.pkl`
- make `predict_rul.py` load only bundle-local artifacts
- make dashboard reads depend on bundle-local outputs rather than shared workspace state
