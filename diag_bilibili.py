import bilibili_toolman.bilisession.web as m

path = m.__file__
with open(path, encoding='utf-8') as f:
    lines = f.readlines()

# Print UploadVideo function - lines 343 to 430
for i in range(342, 430):
    if i < len(lines):
        print(f"{i+1:4d}: {lines[i].rstrip()}")
