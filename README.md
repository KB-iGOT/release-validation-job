# Release Validation Job

This repository contains a Python script and a Jenkins pipeline for validating release differences between branches, tags, or releases.

## Files

- [release_validation.py](release_validation.py)
- [Jenkinsfile](Jenkinsfile)

## Supported Modes

The script supports two modes:

1. Single repository comparison
2. Batch comparison from a CSV file

## Single Repository Example

```bash
python3 release_validation.py \
  --repo KB-iGOT/cbp-ai-ui \
  --old cbrelease-4.8.33 \
  --current cbrelease-4.8.37
```

## Batch CSV Example

```bash
python3 release_validation.py \
  --csv comparisons.csv \
  --report-file report.txt
```

## CSV Format

```csv
repo,old,current
KB-iGOT/cbp-ai-ui,cbrelease-4.8.33,cbrelease-4.8.37
KB-iGOT/cbp-api,cbrelease-4.8.33,cbrelease-4.8.37
```

- `repo` is the GitHub repository in `owner/name` form, e.g. `https://github.com/KB-iGOT/sunbird-cb-staticweb.git` becomes `kb-igot/sunbird-cb-staticweb`.
- `old` should be the production tag/release you are comparing from.
- `current` should be the UAT tag/release you are comparing to.

## Jenkins Usage

- For a single repository, fill the `REPOSITORY`, `OLD_RELEASE`, and `CURRENT_RELEASE` parameters.
- For batch validation, paste CSV content into `COMPARISON_CSV_CONTENT` before running the build.
- In Jenkins CSV mode, `old` means the production tag and `current` means the UAT tag.
- The generated report is archived as a Jenkins artifact with a timestamped filename.

## Mitigating Commit Differences

If the report identifies missing commits between `old` and `current`, follow these steps:

1. Review the report and identify repositories with missing commits.
2. Contact the respective repository owner or maintainer for each affected repo.
3. Share the commit-difference details from the report so they understand what changed.
4. Ask the repo owner to raise a pull request that merges the missing commits into the target branch or release.
5. Re-run the validation after the PR is merged to confirm the missing commits are resolved.
