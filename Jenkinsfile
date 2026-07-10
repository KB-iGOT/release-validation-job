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
                        def csvPath = ''
                        if (params.COMPARISON_CSV != null && params.COMPARISON_CSV != '') {
                            csvPath = params.COMPARISON_CSV.toString()
                        }

                        if (!csvPath && params.COMPARISON_CSV_CONTENT?.trim()) {
                            writeFile file: "${env.WORKSPACE}/comparisons.csv", text: params.COMPARISON_CSV_CONTENT
                            csvPath = "${env.WORKSPACE}/comparisons.csv"
                        }

                        if (csvPath) {
                            sh """
                            python3 release_validation.py \
                              --csv "${csvPath}" \
                              --report-file "${env.WORKSPACE}/release_validation_report.txt"
                            """
                        } else {
                            sh """
                            python3 release_validation.py \
                              --repo "${params.REPOSITORY}" \
                              --old "${params.OLD_RELEASE}" \
                              --current "${params.CURRENT_RELEASE}"
                            """
                        }
                    }
                }

            }

        }

    }

}