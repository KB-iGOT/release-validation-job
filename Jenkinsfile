pipeline {

    agent any

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