import subprocess
string="git -C /Users/jim/Desktop/SP-REDBACK-BACKEND/TeamSPBackend/resource/repo/https:--admin:123@github.com-jim1997-COMP90082_Software_Project_Database_Backend tag"
result=subprocess.getoutput(string).split()
print("result::: ",result)