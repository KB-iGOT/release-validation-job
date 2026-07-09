pipeline {
    agent any
    parameters {
        choice(
            name: 'REPOSITORY',
            choices: [
                'KB-iGOT/sunbird-data-products',
                'KB-iGOT/creation-portal',
                'KB-iGOT/sunbird-lms-jobs',
                'KB-iGOT/sunbird-lms-service',
                'KB-iGOT/sunbird-data-pipeline',
                'KB-iGOT/knowledge-mw-service',
                'KB-iGOT/sunbird-auth',
                'KB-iGOT/sunbird-learning-platform',
                'KB-iGOT/sunbird-lms-mw',
                'KB-iGOT/sunbird-ml-workbench',
                'KB-iGOT/sunbird-utils',
                'KB-iGOT/sunbird-analytics',
                'KB-iGOT/knowledge-platform',
                'KB-iGOT/sunbird-telemetry-service',
                'KB-iGOT/secor',
                'KB-iGOT/cbp-ai-ui',
                'KB-iGOT/sunbird-content-player',
                'KB-iGOT/print-service',
                'KB-iGOT/sunbird-content-editor',
                'KB-iGOT/sunbird-collection-editor',
                'KB-iGOT/sunbird-generic-editor',
                'KB-iGOT/sunbird-course-service',
                'KB-iGOT/sunbird-devops',
                'KB-iGOT/cert-service',
                'KB-iGOT/certificate-registry',
                'KB-iGOT/enc-service',
                'KB-iGOT/deterministic-chatbot',
                'KB-iGOT/sunbird-analytics-core',
                'KB-iGOT/sunbird-analytics-service',
                'KB-iGOT/sunbird-core-dataproducts',
                'KB-iGOT/sunbird-notification-service',
                'KB-iGOT/sunbird-desktop-app',
                'KB-iGOT/sunbird-report-service',
                'KB-iGOT/open-saber',
                'KB-iGOT/knowledge-platform-jobs',
                'KB-iGOT/sunbird-apimanager-util',
                'KB-iGOT/mvc-service',
                'KB-iGOT/sunbird-dial-service',
                'KB-iGOT/discussions-middleware',
                'KB-iGOT/sunbird-bot',
                'KB-iGOT/sunbird-nodebb',
                'KB-iGOT/knowledge-platform-db-extensions',
                'KB-iGOT/gotenberg',
                'KB-iGOT/ml-core-service',
                'KB-iGOT/ml-survey-service',
                'KB-iGOT/ml-projects-service',
                'KB-iGOT/ml-reports-service',
                'KB-iGOT/ml-analytics-service',
                'KB-iGOT/SunbirdEd-mobile-app',
                'KB-iGOT/data-pipeline',
                'KB-iGOT/inquiry-api-service',
                'KB-iGOT/sunbird-cb-devops',
                'KB-iGOT/sunbird-cb-adminportal',
                'KB-iGOT/sunbird-cb-creationportal',
                'KB-iGOT/sunbird-cb-orgportal',
                'KB-iGOT/sunbird-cb-scoring-engine',
                'KB-iGOT/sunbird-cb-network',
                'KB-iGOT/sunbird-cb-contentvalidation',
                'KB-iGOT/faq-assistant',
                'KB-iGOT/sunbird-cb-ext',
                'KB-iGOT/sunbird-cb-uiproxy',
                'KB-iGOT/sunbird-cb-workflow',
                'KB-iGOT/sunbird-cb-portal',
                'KB-iGOT/cb-pores-service',
                'KB-iGOT/sunbird-cb-frac',
                'KB-iGOT/kb-portal',
                'KB-iGOT/pdf-generator',
                'KB-iGOT/cb-ext-form-service',
                'KB-iGOT/sunbird-cb-portal-assets',
                'KB-iGOT/cb_external_enrollment_service',
                'KB-iGOT/cios-content-service',
                'KB-iGOT/cb-service-registry',
                'KB-iGOT/cb-discussion-service',
                'KB-iGOT/cb-community-service',
                'KB-iGOT/cb-integration-framework',
                'KB-iGOT/nlp-search',
                'KB-iGOT/sunbird-cb-staticweb',
                'KB-iGOT/discussion-metaupdate-service',
                'KB-iGOT/comment-tree-service',
                'KB-iGOT/cb-comment-service',
                'KB-iGOT/cb-ext-userprofile-service',
                'KB-iGOT/cb-notification-wrapper',
                'KB-iGOT/cb-search-service',
                'KB-iGOT/cb-ext-course-service',
                'KB-iGOT/custom-field-service',
                'KB-iGOT/cb-core-data',
                'KB-iGOT/sunbird-cb-multitenant-staticweb',
                'KB-iGOT/form-service',
                'KB-iGOT/cb-ext-assessment-service',
                'KB-iGOT/ai-cbp-mdo-service',
                'kb-igot/cb-notification-service',
                'KB-iGOT/id-mapping-service'
            ],
            description: 'Select Repository'
        )
        string(name:'OLD_RELEASE', defaultValue:'', description:'Old branch/tag')
        string(name:'CURRENT_RELEASE', defaultValue:'', description:'Current branch/tag')
    }
    stages {
        stage('Release Validation') {
            steps {
                sh '''
python3 release_validation.py \
  --repo "${REPOSITORY}" \
  --old "${OLD_RELEASE}" \
  --current "${CURRENT_RELEASE}"
'''
            }
        }
    }
}
