pipeline {
  agent {
    docker {
      image 'python:3.11'
      args '-v /var/run/docker.sock:/var/run/docker.sock'
    }
  }

  environment {
    SONARQUBE = credentials('GlobalSonar')  // จะมีหรือไม่มีก็ได้
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

    // 🔧 เปลี่ยน agent เฉพาะสเตจนี้ให้ใช้ภาพ sonarsource/sonar-scanner-cli
    stage('SonarQube Analysis') {
      agent {
        docker {
          image 'sonarsource/sonar-scanner-cli:latest'
          // ไม่ต้อง mount docker.sock เพราะเราไม่เรียก docker ข้างในอีก
        }
      }
      steps {
        withSonarQubeEnv('SonarQube servers') {
          // ใช้ single-quoted heredoc เพื่อเลี่ยง Groovy interpolation warning ของ secret
          sh '''
            export PYTHONPATH="$PWD"
            sonar-scanner
          '''
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
