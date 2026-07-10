# Release Validation Job

Files:
- release_validation.py
- Jenkinsfile

The script now supports two modes:

1. Single repository comparison
2. Batch comparison from a CSV upload

Single repository example:

python3 release_validation.py --repo KB-iGOT/cbp-ai-ui --old cbrelease-4.8.33 --current cbrelease-4.8.37

Batch CSV example:

python3 release_validation.py --csv comparisons.csv --report-file report.txt

CSV format:

repo,old,current
KB-iGOT/cbp-ai-ui,cbrelease-4.8.33,cbrelease-4.8.37
KB-iGOT/cbp-api,cbrelease-4.8.33,cbrelease-4.8.37

Jenkins usage:
- For a single repository, fill REPOSITORY, OLD_RELEASE and CURRENT_RELEASE.
- For multiple repositories, either upload a CSV file using the COMPARISON_CSV parameter or paste CSV content into COMPARISON_CSV_CONTENT before running the build.
