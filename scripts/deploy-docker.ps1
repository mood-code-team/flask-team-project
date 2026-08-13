# Mood Code — Docker Hub build & push (Render Existing Image용)
# 사용: .\scripts\deploy-docker.ps1
# Docker Desktop이 Engine running 상태여야 합니다.

$ErrorActionPreference = "Stop"
$DockerHubUser = "gygs1090"
$ImageName = "${DockerHubUser}/mood-code:latest"

$dockerBin = "C:\Program Files\Docker\Docker\resources\bin"
if (Test-Path $dockerBin) {
    $env:Path = "$dockerBin;$env:Path"
}

$ProjectRoot = Split-Path $PSScriptRoot -Parent
Set-Location $ProjectRoot

Write-Host ">>> Docker engine 확인..."
docker info | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Docker Desktop을 실행하고 Engine running 상태가 될 때까지 기다린 뒤 다시 실행하세요." -ForegroundColor Red
    exit 1
}

Write-Host ">>> Docker Hub 로그인 (gygs1090)..."
docker login -u $DockerHubUser
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host ">>> 이미지 빌드: $ImageName"
docker build -t $ImageName .
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host ">>> Docker Hub push..."
docker push $ImageName
if ($LASTEXITCODE -ne 0) { exit 1 }

Write-Host ""
Write-Host "완료! Render Existing Image URL:" -ForegroundColor Green
Write-Host "  docker.io/$ImageName"
Write-Host ""
Write-Host "Render 환경 변수:" -ForegroundColor Yellow
Write-Host "  FLASK_ENV=production"
Write-Host "  SECRET_KEY=(Generate)"
Write-Host "  SOCIAL_DEMO_LOGIN=true"
