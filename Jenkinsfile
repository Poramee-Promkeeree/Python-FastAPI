pipeline {
  agent {
    docker {
      image 'python:3.11'
      args '-v /var/run/docker.sock:/var/run/docker.sock'
    }
  }

  tools {
    jdk 'JDK'                // ชื่อต้องตรงกับที่ config ไว้
    // ไม่ต้องกำหนด scanner ใน tools; จะอ้างด้วยคำสั่ง 'tool' ตอนรัน
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
          apt-get update
          apt-get install -y openjdk-17-jdk
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
            def scannerHome = tool 'SonarQube Scanner'   // ชื่อต้องตรงกับที่ตั้งในรูปของคุณ
            sh """
              set -e
              export PATH=\"${scannerHome}/bin:\$PATH\"
              sonar-scanner
            """
          }
        }
      }
    }
  }

  post {
    always { echo 'Pipeline finished' }
  }
}
