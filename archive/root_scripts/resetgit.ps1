# Navigate to your project folder
Set-Location "C:\Path\To\Your\Repo"

# Remove the .git folder to delete all history
Remove-Item -Recurse -Force ".git"

# Reinitialize the Git repository
git init

# Optional: Add all current files and make a fresh commit
git add .
git commit -m "Initial commit after full reset"

# Optional: Set remote origin again if needed
# git remote add origin https://github.com/your/repo.git
# git push -u origin master --force