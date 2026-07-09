pipeline {

    agent any

    stages {

        stage('Release Validation') {

            steps {

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