# Создание тестовых VFS
"minimal" | Out-File "file1.txt"
Compress-Archive -Path "file1.txt" -DestinationPath "minimal.zip"

# Создаем все файлы перед архивацией
"file1" | Out-File "files.txt"  
"text" | Out-File "text.txt"
"data" | Out-File "data.csv"
Compress-Archive -Path @("files.txt", "text.txt", "data.csv") -DestinationPath "files.zip"

New-Item -ItemType Directory -Path "deep/folder1/subfolder" -Force
New-Item -ItemType Directory -Path "deep/folder2/level2/level3" -Force
"root" | Out-File "deep/file1.txt"
"level1" | Out-File "deep/folder1/file2.txt" 
"level2" | Out-File "deep/folder1/subfolder/file3.txt"
"level3" | Out-File "deep/folder2/level2/level3/file4.txt"
Compress-Archive -Path "deep/*" -DestinationPath "deep.zip"

# Удаляем временные файлы
Remove-Item "file1.txt", "files.txt", "text.txt", "data.csv" -ErrorAction SilentlyContinue
Remove-Item "deep" -Recurse -Force