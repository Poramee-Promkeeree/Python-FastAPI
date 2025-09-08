pipeline {
  agent {
    docker {
      image 'python:3.11'
      // รันเป็น root และต่อ docker.sock ของโฮสต์ เพื่อ build/run ได้
      args '-u 0:0 -v /var/run/docker.sock:/var/run/docker.sock'
    }
  }

  options { timestamps() }

  stages {

    stage('Install Base Tooling') {
      steps {
        sh '''
          set -eux
          apt-get update
          # ใช้ docker-cli พอ (เบากว่า docker.io) เพราะเราใช้ docker engine จากโฮสต์ผ่าน /var/run/docker.sock
          DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
            git wget unzip ca-certificates docker-cli default-jre-headless

          command -v git
          command -v docker
          docker --version
          java -version || true

          # ---- Install SonarScanner CLI ----
          SCAN_VER=7.2.0.5079
          BASE_URL="https://binaries.sonarsource.com/Distribution/sonar-scanner-cli"
          CANDIDATES="
            sonar-scanner-${SCAN_VER}-linux-x64.zip
            sonar-scanner-${SCAN_VER}-linux.zip
            sonar-scanner-cli-${SCAN_VER}-linux-x64.zip
            sonar-scanner-cli-${SCAN_VER}-linux.zip
          "
          rm -f /tmp/sonar.zip || true
          for f in $CANDIDATES; do
            URL="${BASE_URL}/${f}"
            echo "Trying: $URL"
            if wget -q --spider "$URL"; then
              wget -qO /tmp/sonar.zip "$URL"
              break
            fi
          done
          test -s /tmp/sonar.zip || { echo "Failed to download SonarScanner ${SCAN_VER}"; exit 1; }

          unzip -q /tmp/sonar.zip -d /opt
          SCAN_HOME="$(find /opt -maxdepth 1 -type d -name 'sonar-scanner*' | head -n1)"
          ln -sf "$SCAN_HOME/bin/sonar-scanner" /usr/local/bin/sonar-scanner
          sonar-scanner --version

          # ยืนยันว่า docker.sock ถูก mount มาแล้ว
          test -S /var/run/docker.sock || { echo "ERROR: /var/run/docker.sock not mounted"; exit 1; }
        '''
      }
    }

    stage('Checkout') {
      steps {
        git branch: 'main', url: 'https://github.com/Poramee-Promkeeree/Python-FastAPI.git'
      }
    }

    stage('Install Python Deps') {
      steps {
        sh '''
          set -eux
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install pytest pytest-cov
          # เผื่อบางโปรเจกต์ยังไม่มีไฟล์ __init__.py
          test -f app/__init__.py || touch app/__init__.py
        '''
      }
    }

    stage('Run Tests & Coverage') {
      steps {
        sh '''
          set -eux
          export PYTHONPATH="$PWD"
          pytest -q --cov=app --cov-report=xml tests/ || pytest -q --cov=app --cov-report=xml
          ls -la
          test -f coverage.xml
        '''
      }
    }

    stage('SonarQube Analysis') {
      steps {
        // ชื่อ server ต้องตรงกับที่ตั้งไว้ใน Manage Jenkins → SonarQube servers
        withSonarQubeEnv('SonarQube servers') {
          sh '''
            set -eux
            # ถ้ามีไฟล์ sonar-project.properties ให้ใช้ไฟล์นั้น
            if [ -f sonar-project.properties ]; then
              sonar-scanner \
                -Dsonar.host.url="$SONAR_HOST_URL" \
                -Dsonar.login="$SONAR_AUTH_TOKEN"
            else
              # fallback ถ้าไม่มีไฟล์ properties
              sonar-scanner \
                -Dsonar.host.url="$SONAR_HOST_URL" \
                -Dsonar.login="$SONAR_AUTH_TOKEN" \
                -Dsonar.projectBaseDir="$PWD" \
                -Dsonar.projectKey=python-fastapi-poramee \
                -Dsonar.projectName="Python FastAPI (Poramee)" \
                -Dsonar.sources=app \
                -Dsonar.tests=tests \
                -Dsonar.python.version=3.11 \
                -Dsonar.python.coverage.reportPaths=coverage.xml \
                -Dsonar.sourceEncoding=UTF-8
            fi
          '''
        }
      }
    }

    // ต้องตั้ง webhook ใน SonarQube → http(s)://<JENKINS_URL>/sonarqube-webhook/
    stage('Quality Gate') {
      steps {
        timeout(time: 10, unit: 'MINUTES') {
          waitForQualityGate abortPipeline: true
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
          set -eux
          docker rm -f fastapi-app || true
          docker run -d --name fastapi-app -p 8000:8000 fastapi-app:latest
        '''
      }
    }
  }

  post { always { echo "Pipeline finished" } }
}
