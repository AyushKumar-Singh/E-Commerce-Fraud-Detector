# PowerShell script to start frontend
Write-Host "Installing dependencies..." -ForegroundColor Green
Set-Location frontend-react
npm install

Write-Host "`nStarting development server..." -ForegroundColor Green
npm run dev
