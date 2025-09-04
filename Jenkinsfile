pipeline {
  agent {
    docker {
      image 'python:3.11'
      args '-v /var/run/docker.sock:/var/run/docker.sock'
    }
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
        sh 'pytest --cov=app --cov-report=xml:coverage.xml -q'
      }
    }

    stage('SonarQube Analysis') {
      steps {
        script {
          // ดึง path ของ SonarQube Scanner จาก Jenkins Tools
          def scannerHome = tool 'SonarQube Scanner'   // ต้องตรงกับชื่อที่ตั้งไว้ใน Manage Jenkins → Tools

          // ใช้ server ชื่อให้ตรงกับที่ตั้งค่าใน Configure System → SonarQube servers
          withSonarQubeEnv('SonarQube servers') {
            sh """
              "${scannerHome}/bin/sonar-scanner" \
                -Dsonar.python.coverage.reportPaths=coverage.xml
            """
          }
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
