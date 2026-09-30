# Dataset Notes

## Source And Contents

The demo data was based on the [Pyaz Mandi Onion Quality Dataset](https://www.kaggle.com/datasets/ketsaa/pyaz-mandi-onion-quality-dataset). Dataset files are **not included in the current repository**. The local prototype copy previously inspected contained 1,233 images, 1,233 corresponding JSON metadata files, and a consolidated CSV with 1,233 rows and 24 columns.

The Kaggle data card says the images were collected from publicly accessible sources. It explicitly identifies the quality, grading, composition, price, location, and report attributes as **synthetically generated**, not manually verified visual ground truth. Do not use these attributes as validated labels or claim model accuracy from them. The Kaggle license is listed as **Unknown**; check rights and attribution requirements before redistribution or production use.

## CSV Schema

Each CSV row describes an image/report example. Images have no verified object-level bounding boxes or per-onion defect labels in this dataset.

| Field(s) | Meaning |
| --- | --- |
| `image_id` | Synthetic image record identifier. |
| `image_filename` | Image filename corresponding to an image in the Kaggle dataset. |
| `image_path` | Original machine-specific source path; not portable and should not be used to load local files. |
| `report_id` | Synthetic report identifier. |
| `date`, `time` | Synthetic report date and local-time text. |
| `location`, `latitude`, `longitude` | Synthetic location and coordinates; not verified capture geotags. |
| `quality_score`, `overall_grade` | Synthetic overall score and grade. |
| `grade_a_pct`, `urs_pct`, `damaged_pct`, `rotten_pct`, `sprouted_pct`, `undersized_pct` | Synthetic composition percentages; these describe generated metadata, not image annotations. |
| `grade_a_rate_min_rs_per_quintal`, `grade_a_rate_max_rs_per_quintal` | Synthetic Grade A indicative price range in INR per quintal. |
| `urs_rate_min_rs_per_quintal`, `urs_rate_max_rs_per_quintal` | Synthetic URS indicative price range in INR per quintal. |
| `expected_rate_min_rs_per_quintal`, `expected_rate_max_rs_per_quintal` | Synthetic expected price range in INR per quintal. |
| `attribute_source` | Metadata provenance marker; current rows use `synthetic_random_assignment`. |

The dataset's JSON metadata files repeat the row-level attributes for individual images, including the same synthetic-data caveats. They are not present in this repository.

## Use In Chayan

The dataset informed prototype/demo and experimentation work, but is not included in this repository. The current Next.js UI does not load it for inference: displayed scores, defect breakdowns, prices, annotations, and report examples are hardcoded in the app. The Keras files under `ML/models/` are likewise not connected to the app, and this repository does not provide an onion-model training/evaluation pipeline. A production dataset would need documented provenance, expert-verified labels, portable image references, and a held-out evaluation protocol.