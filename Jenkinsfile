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
          python -m venv .venv
          . .venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov coverage
        '''
      }
    }

    stage('Run Tests & Coverage') {
      steps {
        sh '''
          . .venv/bin/activate
          export PYTHONPATH="${PYTHONPATH}:$(pwd)"
          pytest --cov=app --cov-report=xml:coverage.xml -q
        '''
      }
    }

    stage('SonarQube Analysis') {
      steps {
        script {
          def scannerHome = tool 'SonarQube Scanner'   // ชื่อตรงกับที่ตั้งใน Tools
          withSonarQubeEnv('SonarQube servers') {       // ตรงกับชื่อ server config
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
    always { echo "Pipeline finished" }
  }
}
