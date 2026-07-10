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
                        sh "rm -f '${env.WORKSPACE}/release_validation_report_*.txt'"
                        def useSingleRepo = params.REPOSITORY?.trim() && params.OLD_RELEASE?.trim() && params.CURRENT_RELEASE?.trim()
                        def csvPath = ''
                        def csvParam = params.COMPARISON_CSV

                        env.REPORT_FILE_NAME = reportFileName

                        if (useSingleRepo) {
                            echo "Using single-repo inputs from Jenkins parameters"
                        } else {
                            def candidatePaths = []

                            if (csvParam != null && csvParam != '') {
                                echo "Found file parameter: ${csvParam}"
                                candidatePaths << csvParam.toString()

                                try {
                                    if (csvParam.metaClass.respondsTo(csvParam, 'getLocation')) {
                                        def location = csvParam.getLocation()
                                        if (location) {
                                            candidatePaths << location.toString()
                                        }
                                    }
                                } catch (Exception ignored) {}

                                try {
                                    if (csvParam.metaClass.respondsTo(csvParam, 'getFile')) {
                                        def fileRef = csvParam.getFile()
                                        if (fileRef) {
                                            candidatePaths << fileRef.absolutePath
                                        }
                                    }
                                } catch (Exception ignored) {}
                            }

                            if (!csvPath && candidatePaths) {
                                for (path in candidatePaths) {
                                    if (path && new File(path).exists()) {
                                        csvPath = path
                                        break
                                    }
                                }
                            }

                            if (!csvPath && params.COMPARISON_CSV_CONTENT?.trim()) {
                                writeFile file: "${env.WORKSPACE}/comparisons.csv", text: params.COMPARISON_CSV_CONTENT
                                csvPath = "${env.WORKSPACE}/comparisons.csv"
                            }

                            if (!csvPath) {
                                def foundCsv = sh(script: "find '${env.WORKSPACE}' -type f -name '*.csv' | sort | tail -n 1", returnStdout: true).trim()
                                if (foundCsv) {
                                    csvPath = foundCsv
                                }
                            }

                            if (!csvPath) {
                                def workspaceRoot = new File(env.WORKSPACE ?: '.')
                                def csvFiles = []
                                workspaceRoot.eachFileRecurse { file ->
                                    if (file.isFile() && file.name.toLowerCase().endsWith('.csv')) {
                                        csvFiles << file
                                    }
                                }
                                if (csvFiles) {
                                    csvFiles.sort { it.lastModified() }
                                    csvPath = csvFiles[-1].absolutePath
                                }
                            }

                            if (csvPath) {
                                echo "Using CSV file: ${csvPath}"
                            } else {
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