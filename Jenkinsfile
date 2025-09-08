pipeline {
  agent {
    docker {
      image 'python:3.11'
      // รันเป็น root + ใช้ docker.sock ของโฮสต์
      args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
    }
  }

  environment {
    SONARQUBE = credentials('GlobalSonar') // จะมีหรือไม่ก็ได้
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/Poramee-Promkeeree/Python-FastAPI.git'
      }
    }

    // ติดตั้ง docker CLI ใน agent (ครั้งแรกเท่านั้น; subsequent runs จะ cache layer ของ container ไว้)
    stage('Prepare tools (docker CLI)') {
      steps {
        sh '''
          set -e
          if ! command -v docker >/dev/null 2>&1; then
            apt-get update
            apt-get install -y docker.io
          fi
          docker --version
        '''
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
        withSonarQubeEnv('SonarQube servers') {
          script {
            def WS = pwd()
            // ใช้ single quotes เพื่อลด Groovy interpolation warning ของ secret
            sh '''
              set -e
              export PYTHONPATH="$PWD"
              docker run --rm \
                -e SONAR_HOST_URL="$SONAR_HOST_URL" \
                -e SONAR_LOGIN="$SONAR_AUTH_TOKEN" \
                -v "$PWD:/usr/src" \
                -w /usr/src \
                sonarsource/sonar-scanner-cli:latest \
                sonar-scanner
            '''
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
