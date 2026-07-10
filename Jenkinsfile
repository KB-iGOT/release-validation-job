pipeline {

    agent any

    parameters {
        string(name: 'REPOSITORY', defaultValue: '', description: 'Repository in owner/name format for single-repo validation')
        string(name: 'OLD_RELEASE', defaultValue: '', description: 'Previous release/branch/tag for single-repo validation')
        string(name: 'CURRENT_RELEASE', defaultValue: '', description: 'Current release/branch/tag for single-repo validation')
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

                        // remove any previous report files in the workspace
                        sh "find '${env.WORKSPACE}' -maxdepth 1 -type f -name 'release_validation_report_*.txt' -delete"

                        def useSingleRepo = params.REPOSITORY?.trim() && params.OLD_RELEASE?.trim() && params.CURRENT_RELEASE?.trim()
                        def csvPath = ''

                        env.REPORT_FILE_NAME = reportFileName

                        if (useSingleRepo) {
                            echo "Using single-repo inputs from Jenkins parameters"
                        } else {
                            echo "CSV content parameter length: ${params.COMPARISON_CSV_CONTENT?.size() ?: 0}"

                            // require pasted CSV content now that file upload support is not used
                            if (params.COMPARISON_CSV_CONTENT?.trim()) {
                                writeFile file: "${env.WORKSPACE}/comparisons.csv", text: params.COMPARISON_CSV_CONTENT
                                csvPath = "${env.WORKSPACE}/comparisons.csv"
                                // show a short preview for debugging
                                sh "echo '--- CSV preview (first 200 lines):' && sed -n '1,200p' '${csvPath}' || true"
                            }

                            if (csvPath) {
                                echo "Resolved CSV path: ${csvPath}"
                            } else {
                                echo "No CSV file found in workspace"
                            }
                        }

                        if (useSingleRepo) {
                            sh """
                            python3 release_validation.py \
                              --repo \"${params.REPOSITORY}\" \
                              --old \"${params.OLD_RELEASE}\" \
                              --current \"${params.CURRENT_RELEASE}\" \
                              --report-file \"${reportFile}\"
                            """
                        } else if (csvPath) {
                            sh """
                            python3 release_validation.py \
                              --csv \"${csvPath}\" \
                              --report-file \"${reportFile}\"
                            """
                        } else {
                            error('Provide single-repo values or paste CSV content into COMPARISON_CSV_CONTENT before running the build.')
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