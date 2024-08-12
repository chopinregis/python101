pipeline {
    agent any

    environment {
        GITHUB_REPO = 'https://github.com/your-username/your-repo.git'
        BOOTSTRAP_SCRIPT = '18_Final_bootstrap.sh'
        APP_DIR = '/path/to/your/hospitalwebapp'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: "${GITHUB_REPO}"
            }
        }

        stage('Check for Changes') {
            steps {
                script {
                    def changes = sh(script: "git diff HEAD^ HEAD -- ${BOOTSTRAP_SCRIPT}", returnStatus: true)
                    if (changes == 0) {
                        echo "Changes detected in ${BOOTSTRAP_SCRIPT}"
                        env.SCRIPT_CHANGED = 'true'
                    } else {
                        echo "No changes in ${BOOTSTRAP_SCRIPT}"
                        env.SCRIPT_CHANGED = 'false'
                    }
                }
            }
        }

        stage('Update Application') {
            when {
                expression { env.SCRIPT_CHANGED == 'true' }
            }
            steps {
                script {
                    // Copy the updated bootstrap script to the application directory
                    sh "cp ${BOOTSTRAP_SCRIPT} ${APP_DIR}/"

                    // Run the bootstrap script
                    sh "cd ${APP_DIR} && sudo bash ${BOOTSTRAP_SCRIPT}"
                }
            }
        }

        stage('Restart Services') {
            when {
                expression { env.SCRIPT_CHANGED == 'true' }
            }
            steps {
                sh 'sudo systemctl restart hospital_queue'
                sh 'sudo systemctl restart nginx'
            }
        }
    }

    post {
        success {
            echo 'Pipeline executed successfully!'
        }
        failure {
            echo 'Pipeline failed. Please check the logs for details.'
        }
    }
}