pipeline {
    agent {
        docker {
            image 'python:3.11'
            args '-v /var/run/docker.sock:/var/run/docker.sock'
        }
    }

    tools {
        // ต้องตรงกับชื่อที่ตั้งไว้ใน Jenkins → SonarQube Scanner installations
        sonarQubeScanner 'SonarQube Scanner'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/Poramee-Promkeeree/Python-FastAPI.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                  pip install --upgrade pip
                  pip install -r requirements.txt
                  pip install pytest pytest-cov coverage
                '''
            }
        }

        stage('Run Tests & Coverage') {
            steps {
                // สร้าง coverage.xml สำหรับ SonarQube
                sh 'pytest --cov=app --cov-report=xml:coverage.xml -q'
            }
        }

        stage('SonarQube Analysis') {
            steps {
                // ชื่อใน withSonarQubeEnv ต้องตรงกับ SonarQube servers ที่ตั้งค่าไว้ใน Jenkins
                withSonarQubeEnv('SonarQube servers') {
                    sh 'sonar-scanner'
                }
            }
        }

        stage('Build Docker Image') {
            steps {
                sh 'docker build -t fastapi-app:latest .'
            }
        }

        stage('Deploy Container') {
            steps {
                sh '''
                  docker rm -f fastapi-app || true
                  docker run -d --name fastapi-app -p 8000:8000 fastapi-app:latest
                '''
            }
        }
    }

    post {
        always {
            echo "Pipeline finished"
        }
    }
}
