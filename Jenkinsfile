pipeline {
    agent any

    parameters {
        string(
            name: 'OLD_RELEASE',
            defaultValue: '',
            description: 'Old Branch/Tag'
        )

        string(
            name: 'CURRENT_RELEASE',
            defaultValue: '',
            description: 'Current Branch/Tag'
        )
    }

    stages {

        stage('Compare Releases') {

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