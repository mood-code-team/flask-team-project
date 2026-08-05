# GitHub Issue 4개 일괄 등록 (gh CLI 로그인 필요)
# 사용: gh auth login 후 이 스크립트 실행

$repo = "mood-code-team/flask-team-project"
$root = Split-Path -Parent $PSScriptRoot

$issues = @(
    @{ Title = "[Backend] 팀장 — 인프라·DB·CSV import·PR 리뷰"; File = "issue-01-team-lead.md"; Labels = "backend,team-lead" },
    @{ Title = "[Backend] 2번 — 인증·회원 (Auth)"; File = "issue-02-auth.md"; Labels = "backend,auth" },
    @{ Title = "[Backend] 3번 — 주문·결제·혜택 (Commerce)"; File = "issue-03-commerce.md"; Labels = "backend,commerce" },
    @{ Title = "[Backend] 4번 — 카탈로그·검색·CX"; File = "issue-04-catalog-cx.md"; Labels = "backend,catalog" }
)

foreach ($issue in $issues) {
    $bodyFile = Join-Path $root "docs\github-issues\$($issue.File)"
    Write-Host "Creating: $($issue.Title)"
    gh issue create --repo $repo --title $issue.Title --body-file $bodyFile --label $issue.Labels
}

Write-Host "`nDone. Check: https://github.com/$repo/issues"
