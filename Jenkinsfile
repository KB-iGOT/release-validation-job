pipeline {

    agent any

    parameters {
        string(name: 'REPOSITORY', defaultValue: '', description: 'Repository in owner/name format for single-repo validation')
        string(name: 'OLD_RELEASE', defaultValue: '', description: 'Previous release/branch/tag for single-repo validation')
        string(name: 'CURRENT_RELEASE', defaultValue: '', description: 'Current release/branch/tag for single-repo validation')
        file(name: 'COMPARISON_CSV', description: 'Optional CSV upload with columns: repo, old, current')
        text(name: 'COMPARISON_CSV_CONTENT', defaultValue: '', description: 'Optional CSV content pasted directly in Jenkins; columns: repo, old, current')
    }

    stages {

        stage('Release Validation') {

            steps {

                withCredentials([
                    usernamePassword(
                        credentialsId: 'github-cred',
                        usernameVariable: 'GITHUB_USERNAME',
                        passwordVariable: 'GITHUB_TOKEN'
                    )
                ]) {
                    script {
                        def timestamp = new Date().format('yyyyMMdd_HHmmss')
                        def reportFileName = "release_validation_report_${timestamp}.txt"
                        def reportFile = "${env.WORKSPACE}/${reportFileName}"
                        def useSingleRepo = params.REPOSITORY?.trim() && params.OLD_RELEASE?.trim() && params.CURRENT_RELEASE?.trim()
                        def csvPath = ''
                        def csvParam = params.COMPARISON_CSV

                        env.REPORT_FILE_NAME = reportFileName

                        if (useSingleRepo) {
                            echo "Using single-repo inputs from Jenkins parameters"
                        } else {
                            if (csvParam != null && csvParam != '') {
                                if (csvParam instanceof String) {
                                    csvPath = csvParam
                                } else {
                                    try {
                                        csvPath = csvParam.getLocation()
                                    } catch (Exception ignored) {
                                        csvPath = ''
                                    }

                                    if (!csvPath) {
                                        try {
                                            csvPath = csvParam.getFile().absolutePath
                                        } catch (Exception ignored) {
                                            csvPath = ''
                                        }
                                    }
                                }
                            }

                            if (!csvPath && params.COMPARISON_CSV_CONTENT?.trim()) {
                                writeFile file: "${env.WORKSPACE}/comparisons.csv", text: params.COMPARISON_CSV_CONTENT
                                csvPath = "${env.WORKSPACE}/comparisons.csv"
                            }

                            if (csvPath) {
                                echo "Using uploaded CSV file: ${csvPath}"
                            }
                        }

                        if (useSingleRepo) {
                            sh """
                            python3 release_validation.py \
                              --repo "${params.REPOSITORY}" \
                              --old "${params.OLD_RELEASE}" \
                              --current "${params.CURRENT_RELEASE}" \
                              --report-file "${reportFile}"
                            """
                        } else if (csvPath) {
                            sh """
                            python3 release_validation.py \
                              --csv "${csvPath}" \
                              --report-file "${reportFile}"
                            """
                        } else {
                            error('Provide single-repo values or upload a CSV file before running the build.')
                        }
                    }
                }

            }

            post {
                always {
                    archiveArtifacts artifacts: "${env.REPORT_FILE_NAME}", allowEmptyArchive: true
                }
            }

        }

    }

}