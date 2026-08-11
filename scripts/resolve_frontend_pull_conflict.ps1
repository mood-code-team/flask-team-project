# frontend pull 충돌 자동 해결 (gallery 2파일 → 원격/frontend 버전 채택)
# 사용: powershell -File scripts/resolve_frontend_pull_conflict.ps1

$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

Write-Host "[1/4] git status"
git status --short

$conflictFiles = @("routes/gallery.py", "services/gallery_service.py")
$inMerge = Test-Path ".git/MERGE_HEAD"

if (-not $inMerge) {
    $hasMarkers = Select-String -Path $conflictFiles -Pattern "^<<<<<<< " -ErrorAction SilentlyContinue
    if (-not $hasMarkers) {
        Write-Host "진행 중인 merge 충돌이 없습니다. 필요하면 git pull team frontend 먼저 실행하세요."
    }
}

Write-Host "[2/4] gallery 충돌 → frontend(원격) 버전으로 통일"
foreach ($file in $conflictFiles) {
    if (-not (Test-Path $file)) { continue }
    git checkout --theirs $file 2>$null
    if ($LASTEXITCODE -ne 0) {
        git checkout --ours $file 2>$null
    }
    git add $file
}

if ($inMerge) {
    Write-Host "[3/4] merge commit"
    git commit -m "merge: frontend pull 충돌 해결 (gallery 원격 기준)"
} else {
    Write-Host "[3/4] merge commit 생략 (MERGE_HEAD 없음)"
}

$stash = git stash list 2>$null
if ($stash) {
    Write-Host "[4/4] git stash pop"
    git stash pop
    if ($LASTEXITCODE -ne 0) {
        Write-Host "stash pop에서 추가 충돌이 있으면 VS Code에서 해결 후 git add / git commit 하세요."
        exit 1
    }
} else {
    Write-Host "[4/4] stash 없음 — skip"
}

Write-Host "완료. 서버 재시작 후 / /gallery /category/light 확인하세요."
