pipeline {
  agent none

  // ใช้ชื่อ Tool ให้ตรงกับ Global Tool Configuration:
  // JDK  -> ชื่อ "JDK" (Temurin/Adoptium 17 แนะนำ)
  // SonarQube Scanner -> ชื่อ "SonarQube Scanner"
  tools {
    jdk 'JDK'
  }

  environment {
    // ตั้งค่า SonarQube server ใน Jenkins เป็นชื่อ "SonarQube servers"
    // และผูก token ใน Server config แล้ว (ไม่ต้องประกาศ creds ตรงนี้)
  }

  stages {

    stage('Checkout') {
      agent {
        docker {
          image 'python:3.11'
          // ไม่ต้อง mount docker.sock ในสเตจนี้
          args '-u root --add-host=host.docker.internal:host-gateway'
        }
      }
      steps {
        git branch: 'main', url: 'https://github.com/Poramee-Promkeeree/Python-FastAPI.git'
      }
    }

    stage('Setup venv') {
      agent {
        docker {
          image 'python:3.11'
          args '-u root --add-host=host.docker.internal:host-gateway'
        }
      }
      steps {
        sh '''
          set -e
          python3 -m venv venv
          . venv/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
        '''
      }
    }

    stage('Run Tests & Coverage') {
      agent {
        docker {
          image 'python:3.11'
          args '-u root --add-host=host.docker.internal:host-gateway'
        }
      }
      steps {
        sh '''
          set -e
          export PYTHONPATH="$PWD"
          venv/bin/pytest --maxfail=1 --disable-warnings -q \
            --cov=app --cov-report=xml:coverage.xml
        '''
      }
    }

    stage('SonarQube Analysis') {
      agent {
        docker {
          image 'python:3.11'
          args '-u root --add-host=host.docker.internal:host-gateway'
        }
      }
      steps {
        withSonarQubeEnv('SonarQube servers') {
          script {
            // ดึง path ของเครื่องมือจาก Global Tool
            def scannerHome = tool 'SonarQube Scanner'
            def javaHome    = tool 'JDK'

            sh """
              set -e
              # สร้างไฟล์ค่าเริ่มต้นถ้ายังไม่มี
              if [ ! -f sonar-project.properties ]; then
                cat > sonar-project.properties <<'EOF'
sonar.projectKey=python-fastapi
sonar.projectName=python-fastapi
sonar.sources=app
sonar.tests=tests
sonar.python.version=3.11
sonar.python.coverage.reportPaths=coverage.xml
EOF
              fi

              export JAVA_HOME="${javaHome}"
              export PATH="${scannerHome}/bin:${javaHome}/bin:\$PATH"
              export PYTHONPATH="$PWD"

              # ถ้า SonarQube อยู่ในเครื่องเดียวกัน ให้ใช้ host.docker.internal:9001 ตามที่ตั้งไว้
              sonar-scanner -Dsonar.projectBaseDir="$PWD"
            """
          }
        }
      }
    }

    stage('Build Docker Image') {
      // ใช้ image ที่มี docker CLI มาแล้ว -> เร็วกว่า ไม่ต้อง apt install
      agent {
        docker {
          image 'docker:27-cli'
          args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
        }
      }
      steps {
        sh 'docker build -t fastapi-app:latest .'
      }
    }

    stage('Deploy Container') {
      agent {
        docker {
          image 'docker:27-cli'
          args '-u root -v /var/run/docker.sock:/var/run/docker.sock'
        }
      }
      steps {
        sh '''
          set -e
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
