pipeline {
  agent {
    docker {
      image 'python:3.11'
      // รันเป็น root + ใช้ docker.sock ของโฮสต์
      args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
    }
  }

  options {
    // กัน Jenkins ทำ Declarative: Checkout SCM อีกรอบ (เรา checkout เองใน stage)
    skipDefaultCheckout(true)
  }

  environment {
    SONARQUBE = credentials('GlobalSonar')         // จะมีหรือไม่ก็ได้
    SONAR_SCANNER_IMAGE = 'sonarsource/sonar-scanner-cli:5.0.1'
  }

  stages {
    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/Poramee-Promkeeree/Python-FastAPI.git'
      }
    }

    // ติดตั้ง docker CLI (เล็ก/ไวกว่า docker.io)
    stage('Prepare docker CLI (lightweight)') {
      steps {
        sh '''
          set -e
          if ! command -v docker >/dev/null 2>&1; then
            apt-get update
            apt-get install -y --no-install-recommends docker-cli ca-certificates
            rm -rf /var/lib/apt/lists/*
          fi
          docker --version
        '''
      }
    }

    // อุ่นอิมเมจสแกนเนอร์ไว้ก่อน เพื่อลดเวลาที่สเตจ Sonar
    stage('Warm Sonar image') {
      steps {
        sh 'docker pull ${SONAR_SCANNER_IMAGE}'
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
      options { timeout(time: 15, unit: 'MINUTES') }
      steps {
        withSonarQubeEnv('SonarQube servers') {
          script {
            sh '''
              set -e
              export PYTHONPATH="$PWD"
              docker run --rm \
                --add-host=host.docker.internal:host-gateway \
                -e SONAR_HOST_URL="$SONAR_HOST_URL" \
                -e SONAR_LOGIN="$SONAR_AUTH_TOKEN" \
                -v "$PWD:/usr/src" \
                -w /usr/src \
                ${SONAR_SCANNER_IMAGE} sonar-scanner
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
