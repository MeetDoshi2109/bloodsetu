# BloodSetu local dev starter (PowerShell)
# Runs FastAPI backend on :8000 and React frontend on :5173

Write-Host "Starting BloodSetu..." -ForegroundColor Cyan

# Backend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "uvicorn backend:app --reload --port 8000" -WorkingDirectory $PSScriptRoot

# Frontend
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev" -WorkingDirectory $PSScriptRoot

Write-Host ""
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Green
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Green
Write-Host "API docs: http://localhost:8000/docs" -ForegroundColor Yellow
