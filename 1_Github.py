import requests
import json
import time
import pprint

def leerRepos(path):
    """Read repositories from txt file
    The format of txt must be:
        user/repository => alvaroarribasroyo/CesarCipher
    String->List
    """
    try:
        repos=[]
        file=open(path, "r")
        for line in file:
            repos.append(line.strip())
        file.close()
        return repos
    except:
        print("Invalid repositories.\Check your file repos.txt\n")
        print("The format of txt line must be:\nuser/repository => alvaroarribasroyo/CesarCipher")
        
def readCredential(name):
    """Read a github username and password of txt file
    The format of txt must be:
        username
        password
    Strng->String,String
    """
    try:
         file=open(name, "r")
         user=file.readline().strip()
         passw=file.readline().strip()
         file.close()
         return user,passw
    except:
        print("Invalid credentials\nCheck your txt file.")
        print("The format of passGit.txt must be:\n\tusername\npassword")
    
def auth():
    """Get at authenticated session to
    request github REST API
    void->void
    """
    global conn
    credential=readCredential("passGit.txt")
    conn.auth=(credential[0],credential[1])
    
def addToFile(path,text):
    """Add information into txt file.
    String,String->void"""
    try:
        file=open(path,'a')
        file.write(text)
        file.close
    except:
        print("Error in file",path,"\File does not exist or is in use.")
  
def exportRowCsv(path,row):
    """Export information stored in a list into txt file.The list represents one row
    String,List->void"""
    csvRow=""
    #If get a list
    if isinstance(row,list):
        for element in row:
            if element is not None:
                if element!=";":
                    csvRow+=element
                    csvRow+=";"
                else:
                    csvRow+=element
            else:
                csvRow+="null"
                csvRow+=";"
        csvRow+="\n"
        addToFile(path,csvRow)
    else:#If doesnt get a list
        if row is not None:
            if row!=";":
                csvRow+=row
                csvRow+=";"
            else:
                csvRow+=row
        else:
            csvRow+="null"
            csvRow+=";"
        csvRow+="\n"
        addToFile(path,csvRow)

def cleanFile(path):
    """Remove any text of the txt file selected.
    String->void"""
    file=open(path,'w')
    file.write("")
    file.close

##Common Methods##

def getAdditionsDeletions(weeks):
    """
    Get total additions and deletions of many weeks
    List->Int,Int
    """
    additions=0
    deletions=0
    for week in weeks:
        additions+=week["a"]
        deletions+=week["d"]
    return additions,deletions
        
def getAllContributors(server,repo):
    """Get all repo contributors id and
    their additions and deletions
    String,String->Dict
    """
    contributors={}
    url=server+"/repos/"+repo+"/stats/contributors"
    res=conn.get(url)
    dicres=json.loads(res.text)
    for contributor in dicres:
        additionDeletion=getAdditionsDeletions(contributor.get("weeks"))
        additions=str(additionDeletion[0])
        deletions=str(additionDeletion[1])
        commits=str(contributor.get("total"))
        #contributor will be -> author_id:(commit,additions,deletions)
        contributors[str(contributor.get("author").get("id"))]=(commits,additions,deletions)
    return contributors

def getAllDevelopers(server,repo):
    """Get all developers who have participate
    in a repo.This developers are contributors of repo.
    String,String->List
    """
    nameDevelopers=[]
    #Get all contributors of repository
    url=server+"/repos/"+repo+"/stats/contributors"
    res=conn.get(url)
    dicres=json.loads(res.text)
    for developer in dicres:
        nameDevelopers.append(developer.get("author").get("login"))
    return nameDevelopers

def getRepoId(server,repo):
    """Get repository id
    String,String->String
    """
    url=server+"/repos/"+repo
    res=conn.get(url)
    dicres=json.loads(res.text)
    repo_id=str(dicres.get("id"))
    return repo_id

def getAllBranches(server,repo):
    """Get the name of all repo branches
    String,String->List(name,sha)
    """
    branches=[]
    url=server+"/repos/"+repo+"/branches"
    res=conn.get(url)
    dicres=json.loads(res.text)
    for branch in dicres:
        branches.append((branch.get("name"),branch.get("commit").get("sha")))
    return branches
    
def getAllForks(server,repo):
    """Get all repo forks
    String,String->List
    """
    url=server+"/repos/"+repo+"/forks"
    res=conn.get(url)
    forks=json.loads(res.text)
    return forks

##Get Repos.csv##
    
def saveRepo(repoRow,path):
    """Export a row that represents
    a repo to csv file
    List,String->void
    """
    exportRowCsv(path,repoRow)
    
def getRepos(server,repos,path):
    """Get all repos of repos.txt
    String,List,String->Boolean
    """
    try:
        global conn
        cleanFile(path)
        for repo in repos:
            repoRow=[]
            url=server+"/repos/"+repo
            res=conn.get(url)
            dicres=json.loads(res.text)
            repoRow.append(str(dicres.get("id")))
            repoRow.append(dicres.get("name"))
            repoRow.append(dicres.get("language"))
            repoRow.append(str(dicres.get("size")))
            repoRow.append(str(dicres.get("subscribers_count")))
            repoRow.append(str(dicres.get("watchers_count")))
            saveRepo(repoRow,path)
        return True
    except:
        return False
            
##Get developers.csv##
        
def saveDeveloper(developerRow,path):
    """Export a row that represents
    a developer to csv file
    List,String->void
    """
    exportRowCsv(path,developerRow)

def getDevelopers(server,repos,path):
    """Get all developers information.
    String,List,String->Boolean
    """
    try: 
        global conn
        cleanFile(path)
        for repo in repos:
            developers=getAllDevelopers(server,repo)
            for developer in developers:
                developerRow=[]
                url=server+"/users/"+developer
                res=conn.get(url)
                dicres=json.loads(res.text)
                developerRow.append(str(dicres.get("id")))
                developerRow.append(dicres.get("login"))
                developerRow.append(dicres.get("email"))
                developerRow.append(dicres.get("location"))
                developerRow.append(str(dicres.get("public_repos")))
                developerRow.append(str(dicres.get("followers")))
                developerRow.append(str(dicres.get("following")))
                saveDeveloper(developerRow,path)
        return True
    except:
        return False
##Get contributor.csv##
            
def saveContributor(contributorRow,path):
    """Export a row that represents
    a contributor to csv file
    List,String->void
    """
    exportRowCsv(path,contributorRow)

def getContributors(server,repos,path):
    """Get all contributors of repo
    and their information.
    String,List,String->Boolean
    """
    try:
        global conn
        cleanFile(path)
        for repo in repos:
            repo_id=getRepoId(server,repo)
            #Get repo contributors
            contributors=getAllContributors(server,repo)
            for contributor in contributors:
                contributorRow=[]
                contributorRow.append(repo_id)
                contributorRow.append(contributor)#contributor_id key dict
                contributorRow.append(contributors[contributor][0])#commits
                contributorRow.append(contributors[contributor][1])#additions
                contributorRow.append(contributors[contributor][2])#deletions
                saveContributor(contributorRow,path)
        return True
    except:
        return False

##Get branches.csv##
            
def saveBranch(branchRow,path):
    """Export a row that represents
    a branch to csv file
    List,String->void
    """
    exportRowCsv(path,branchRow)
                          
def getBranches(server,repos,path):
    """Get all branches of repo
    and their information.
    String,List,String->Boolean
    """
    try:
        global conn
        cleanFile(path)
        for repo in repos:
            repo_id=getRepoId(server,repo)
            branches=getAllBranches(server,repo)
            for branch in branches:
                branchRow=[]
                url=server+"/repos/"+repo+"/branches/"+branch[0]
                res=conn.get(url)
                dicres=json.loads(res.text)
                branchRow.append(repo_id)
                branchRow.append(branch[0])#name
                branchRow.append(str(dicres.get("commit").get("author").get("id")))
                saveBranch(branchRow,path)
        return True
    except:
        return False
    
##Get commits.csv##

def saveCommit(commitRow,path):
    """Export a row that represents
    a commit to csv file
    List,String->void
    """
    exportRowCsv(path,commitRow)
                          
def getCommits(server,repos,path):
    """Get all commits of repo
    and their information.
    String,List,String->Boolean
    """
    try:
        global conn
        cleanFile(path)
        for repo in repos:
            commitRow=[]
            repo_id=getRepoId(server,repo)
            branches=getAllBranches(server,repo)
            for branch in branches:#For each branch
                moreResults=True#Flag to know if exist more commits
                latestSha=branch[1]#The branch latest sha
                while moreResults:#If there are more commits to retrieve in the branch
                    #Get the latest commits of the branch 
                    url=server+"/repos/"+repo+"/commits?per_page=100&sha="+latestSha
                    res=conn.get(url)
                    dicres=json.loads(res.text)
                    #Get commit information
                    for commit in dicres:
                        commitRow=[]
                        commitRow.append(repo_id)
                        commitRow.append(branch[0])#branch name
                        commitRow.append(commit.get("sha"))
                        try:
                            commitRow.append(str(commit.get("author").get("id")))
                        except:
                            author=commit.get("commit").get("author").get("name")
                            url=server+"/users/"+author
                            res=conn.get(url)
                            userX=json.loads(res.text)
                            commitRow.append(str(userX.get("id")))
                        commitRow.append(commit.get("commit").get("author").get("date"))
                        saveCommit(commitRow,path)
                    latestSha=dicres[len(dicres)-1].get("sha")#Get the new page latest sha
                    if len(dicres)<100:#If there are no more commits pages to retrieve
                        moreResults=False
        return True
    except:
        return False
    
##Get forks.csv##
    
def saveFork(forkRow,path):
    """Export a row that represents
    a fork to csv file
    List,String->void
    """
    exportRowCsv(path,forkRow)
                          
def getForks(server,repos,path):
    """Get all forks of repo
    and their information.
    String,List,String->Boolean
    """
    try:
        global conn
        cleanFile(path)
        for repo in repos:
            repo_id=getRepoId(server,repo)
            forks=getAllForks(server,repo)
            for fork in forks:
                forkRow=[repo_id]
                forkRow.append(str(fork.get("id")))
                forkRow.append(str(fork.get("owner").get("id")))
                forkRow.append(fork.get("created_at"))
                forkRow.append(str(fork.get("size")))
                forkRow.append(str(fork.get("watchers_count")))
                saveFork(forkRow,path)
        return True
    except:
        return False

##Get content.csv##
    
def saveSubcontent(subcontentRow,path):
    """Export a row that represents
    a subcontent to csv file
    List,String->void
    """
    exportRowCsv(path,subcontentRow)
    
def saveContent(contentRow,path):
    """Export a row that represents
    a content to csv file
    List,String->void
    """
    exportRowCsv(path,contentRow)
    
def getAllContents(server,repo,branch,flagRecursion):
    """Get all contents or subcontents of repo using recursion
    String,String,Tuple(String,String),Boolean->List
    """
    if flagRecursion:
        url=server+"/repos/"+repo+"/git/trees/"+branch[1]+"?recursive="+str(9999)#Max search recursion
        res=conn.get(url)
        dicres=json.loads(res.text)
        contents=dicres.get("tree")
        return contents
    else:
        url=server+"/repos/"+repo+"/git/trees/"+branch[1]
        res=conn.get(url)
        dicres=json.loads(res.text)
        contents=dicres.get("tree")
        return contents

def getContents(server,repos,pathContent,pathSubcontent):
    """Get all contents of repo
    and their information.
    String,List,String->Boolean
    """
    try:
        global conn
        cleanFile(pathContent)
        cleanFile(pathSubcontent)
        for repo in repos:#For each repo
            #Get repo id
            repo_id=getRepoId(server,repo)
            #Get all branches for repo
            branches=getAllBranches(server,repo)
            for branch in branches:#For each branch
                #Get the parents contents
                contents=getAllContents(server,repo,branch,False)#False=Inactive recursion
                #For each parent content,store information
                #and look for subcontents
                for content in contents:
                    nameShaContent=(content.get("path"),content.get("sha"))#(name,sha)
                    #Store information
                    contentRow=[repo_id,branch[0]]
                    contentRow.append(nameShaContent[0])#name
                    if content.get("type")=="blob":
                        contentRow.append(content.get("type"))
                        contentRow.append(str(content.get("size")))
                    else:
                        contentRow.append(content.get("type"))
                        contentRow.append(str(0))
                    #Save row of content
                    saveContent(contentRow,pathContent)
                    if content.get("type")=="tree":
                        #Look for subcontent
                        subcontents=getAllContents(server,repo,nameShaContent,True)#True=Active recursion
                        for subcontent in subcontents:
                        #For each subcontent, store information
                            subcontentRow=[repo_id,branch[0],nameShaContent[0]]
                            if subcontent.get("type")=="blob":
                                subcontentRow.append(subcontent.get("type"))
                                subcontentRow.append(str(subcontent.get("size")))
                                
                            else:
                                subcontentRow.append(content.get("type"))
                                subcontentRow.append(str(0))
                            subcontentRow.append(subcontent.get("path"))
                            saveSubcontent(subcontentRow,pathSubcontent)
        return True
    except:
        return False
                            
def main():
    try:
        repos=leerRepos("repos.txt")
        if len(repos)>0:
            gitServer="https://api.github.com"
            #Start an active and authenticated session
            global conn
            conn=requests.Session()
            #Authenthicate with server
            auth()
            #Github REST API requests
            print("Creating tables...")
            start_time=time.time()
            if getRepos(gitServer,repos,"1_repos.csv"):
                print("Repos\t\tOK")
            if getDevelopers(gitServer,repos,"2_developers.csv"):
                print("Developers\tOK")
            if getContributors(gitServer,repos,"3_contributors.csv"):
                print("Contributors\tOK")
            if getBranches(gitServer,repos,"4_branches.csv"):
                print("Branches\tOK") 
            if getCommits(gitServer,repos,"5_commits.csv"):
                print("Commits\t\tOK")
            if getForks(gitServer,repos,"6_forks.csv"):
                print("Forks\t\tOK")
            if getContents(gitServer,repos,"7_contents.csv","8_subcontents.csv"):
                print("Contents\tOK")
                print("Subcontents\tOK")
            print("All tables were created properly in ", round(time.time()-start_time,2) ,"seconds.")
            input("Press enter to continue.")
        else:
            print("There arent repositories to retrieve information\nCheck your repos.txt file")
            print("Read repositories from txt file\nThe format of txt must be:\n\tuser/repository => alvaroarribasroyo/CesarCipher")
            input("Press enter to continue")
    except:
        print("An error ocurred.")
        input("Press enter to continue")
        
if __name__ == "__main__":
    main()

