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

        stage('Prepare Upload') {
            steps {
                script {
                    // look for an uploaded CSV in the master's workspace and stash it so agents can use it
                    def found = sh(script: "find '${env.WORKSPACE}' -maxdepth 1 -type f -name '*.csv' | sort | tail -n 1 || true", returnStdout: true).trim()
                    if (found) {
                        echo "Found uploaded CSV on master: ${found}"
                        sh "cp '${found}' '${env.WORKSPACE}/comparisons.csv'"
                        stash name: 'uploaded-csv', includes: 'comparisons.csv', allowEmpty: false
                    } else {
                        echo 'No uploaded CSV found on master.'
                    }
                }
            }
        }

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
                        sh "find '${env.WORKSPACE}' -maxdepth 1 -type f -name 'release_validation_report_*.txt' -delete"
                        def useSingleRepo = params.REPOSITORY?.trim() && params.OLD_RELEASE?.trim() && params.CURRENT_RELEASE?.trim()
                        def csvPath = ''
                        def csvParam = params.COMPARISON_CSV

                        env.REPORT_FILE_NAME = reportFileName

                        if (useSingleRepo) {
                            echo "Using single-repo inputs from Jenkins parameters"
                        } else {
                            echo "CSV parameter value: ${csvParam}"
                            echo "CSV content parameter length: ${params.COMPARISON_CSV_CONTENT?.size() ?: 0}"

                            def workspaceFiles = sh(script: "find '${env.WORKSPACE}' -maxdepth 1 -type f | sort", returnStdout: true).trim()
                            echo "Workspace files:\n${workspaceFiles}"

                            if (!csvPath && params.COMPARISON_CSV_CONTENT?.trim()) {
                                writeFile file: "${env.WORKSPACE}/comparisons.csv", text: params.COMPARISON_CSV_CONTENT
                                csvPath = "${env.WORKSPACE}/comparisons.csv"
                            }

                                // try to unstash a CSV that was prepared on the master node
                                try {
                                    unstash 'uploaded-csv'
                                    def unstashed = "${env.WORKSPACE}/comparisons.csv"
                                    if (new File(unstashed).exists()) {
                                        csvPath = unstashed
                                    }
                                } catch (Exception ignored) {
                                    // no stashed CSV available
                                }

                            if (!csvPath) {
                                def foundCsv = sh(script: "find '${env.WORKSPACE}' -type f -name '*.csv' | sort | tail -n 1", returnStdout: true).trim()
                                if (foundCsv) {
                                    csvPath = foundCsv
                                }
                            }

                            if (csvPath) {
                                echo "Resolved CSV path: ${csvPath}"
                                echo "Using CSV file: ${csvPath}"
                            } else {
                                echo "No CSV file found in workspace"
                                echo "No CSV file resolved from upload parameter"
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