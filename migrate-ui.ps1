# PowerShell script to migrate new UI to frontend-react

Write-Host "Starting UI migration..." -ForegroundColor Green

# Step 1: Backup current frontend-react
Write-Host "`n1. Backing up current frontend-react..." -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "frontend-react-backup-$timestamp"

if (Test-Path "frontend-react") {
    Rename-Item "frontend-react" $backupPath
    Write-Host "   ✓ Current frontend backed up to: $backupPath" -ForegroundColor Green
}

# Step 2: Copy sample ui to frontend-react
Write-Host "`n2. Copying new UI to frontend-react..." -ForegroundColor Yellow
Copy-Item -Path "sample ui" -Destination "frontend-react" -Recurse
Write-Host "   ✓ New UI copied successfully" -ForegroundColor Green

# Step 3: Update index.html title
Write-Host "`n3. Updating index.html..." -ForegroundColor Yellow
$indexPath = "frontend-react/index.html"
$indexContent = Get-Content $indexPath -Raw
$indexContent = $indexContent -replace "AI-Powered Disaster Response App", "E-Commerce Fraud Detector"
$indexContent | Set-Content $indexPath
Write-Host "   ✓ index.html updated" -ForegroundColor Green

# Step 4: Create .env file
Write-Host "`n4. Creating .env file..." -ForegroundColor Yellow
$envContent = @"
VITE_API_URL=http://localhost:8000
"@
$envContent | Out-File -FilePath "frontend-react/.env" -Encoding UTF8
Write-Host "   ✓ .env file created" -ForegroundColor Green

# Step 5: Create vite-env.d.ts for TypeScript
Write-Host "`n5. Creating TypeScript environment..." -ForegroundColor Yellow
$viteEnvContent = @"
/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}
"@
$viteEnvContent | Out-File -FilePath "frontend-react/src/vite-env.d.ts" -Encoding UTF8
Write-Host "   ✓ TypeScript environment created" -ForegroundColor Green

# Step 6: Install dependencies
Write-Host "`n6. Installing dependencies..." -ForegroundColor Yellow
Set-Location "frontend-react"
npm install
Write-Host "   ✓ Dependencies installed" -ForegroundColor Green

# Step 7: Done
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Migration Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "1. Ensure backend is running: cd backend && python3 app.py"
Write-Host "2. Start frontend: cd frontend-react && npm run dev"
Write-Host "3. Open browser to: http://localhost:3000"
Write-Host "`nBackup location: $backupPath" -ForegroundColor Cyan

Set-Location ..
