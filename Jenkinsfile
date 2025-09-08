pipeline {
  agent {
    docker {
      image 'python:3.11'
      args '-v /var/run/docker.sock:/var/run/docker.sock'
    }
  }

  environment {
    SONARQUBE = credentials('GlobalSonar')  // มี/ไม่มีบรรทัดนี้ก็ได้ เพราะ withSonarQubeEnv จะ inject token ให้อยู่แล้ว
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/Poramee-Promkeeree/Python-FastAPI.git'
      }
    }

    stage('Setup venv') {
      steps {
        sh '''
          python3 -m venv venv
          . venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
        '''
      }
    }

    stage('Run Tests & Coverage') {
      steps {
        sh '''
          export PYTHONPATH="$PWD"
          venv/bin/pytest --maxfail=1 --disable-warnings -q \
            --cov=app --cov-report=xml:coverage.xml
        '''
      }
    }

    stage('SonarQube Analysis') {
      steps {
        withSonarQubeEnv('SonarQube servers') { // ต้องตรงกับชื่อ Server ใน Jenkins
          script {
            def scannerHome = tool 'SonarQube Scanner' // ต้องตรงกับชื่อ Tool ที่ตั้งไว้
            sh """
              export PYTHONPATH="$PWD"
              "${scannerHome}/bin/sonar-scanner"
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
