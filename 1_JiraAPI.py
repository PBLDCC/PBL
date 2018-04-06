import requests
import json
from collections import defaultdict
import time

def readCredential(path):
    """Read the credentials stored in a txt file.The first line is the user
    and the second is the pass.
        String->String,String"""
    try:
        file=open(path, "r")
        user=file.readline().strip()
        passw=file.readline().strip()
        file.close()
        return user,passw
    except:
        print("Invalid username o password.")
         
def login(server):
    """Log-in in the Jira server to get an authenticated user.
    String->Response"""
    url=server+"/rest/auth/1/session"
    credential=readCredential("pass.txt")
    payload={"username": credential[0], "password": credential[1]}
    jsonPayload=json.dumps(payload)
    headers={'Content-type': 'application/json'}
    response=requests.post(url,data=jsonPayload,headers=headers)
    return response

def storeCookie(response):
    """Save the session cookie to get diferents requests with the same cookie
    response->String"""
    global session_cookie
    content=json.loads(response.text)
    session_cookie=content.get("session").get("name")
    session_cookie+="="
    session_cookie+=content.get("session").get("value")
    return session_cookie

def includeHeaders():
    """Include te session cookie in the headers of the request
    void->dict"""
    global session_cookie
    headers={'Content-type': 'application/json',"cookie": session_cookie}
    return headers

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
    
def getAllGroups(server,headers):
    """Get all groups stored in the Jira server.
    String,dict->List"""
    groups=[]
    defaultGroupNames=["jira-administrators","jira-software-users","jira-core-users"]
    #The max number of group to show
    maxResults=9999
    url=server+"/rest/api/2/groups/picker?maxResults="+str(maxResults)
    res=requests.get(url,headers=headers)
    dicres=json.loads(res.text)
    for group in dicres.get("groups"):
        nameGroup=group.get("name")
        if nameGroup not in defaultGroupNames:
            groups.append(nameGroup)
    return groups

def getAllProjects(server,headers):
    """Get all group projects of each group.
    String,dict->dict()"""
    projects=[]
    url=server+"/rest/api/2/project"
    res=requests.get(url,headers=headers)
    dicres=json.loads(res.text)
    for project in dicres:
        projects.append(project.get("id"))
    return projects

def getAllBoards(server,headers):
    """Get all boards of each project.
    String,dict->List"""
    boards=[]
    url=server+"/rest/agile/1.0/board"
    res=requests.get(url,headers=headers)
    dicres=json.loads(res.text)
    totalBoards=dicres.get("values")
    for board in totalBoards:
        boards.append(board.get("id"))
    return boards

def getAllSprints(server,headers,board):
    """Get all sprints of each board.
    String,dict,List->List"""
    sprints=[]
    url=server+"/rest/agile/1.0/board/"+str(board)+"/sprint"
    res=requests.get(url,headers=headers)
    dicres=json.loads(res.text)
    totalSprints=dicres.get("values")
    for sprint in totalSprints:
        sprints.append(sprint.get("id"))
    return sprints

def getBacklog(server,headers,board):
    """Get the backlog's board.
    String,dict,List->List"""
    backlog=[]
    url=server+"/rest/agile/1.0/board/"+str(board)+"/backlog"
    res=requests.get(url,headers=headers)
    dicres=json.loads(res.text)
    totalIssues=dicres.get("issues")
    for issue in totalIssues:
        backlog.append(issue.get("id"))
    return backlog

##Get developers csv##
        
def saveDevelopers(developer,path):
    """Export a row that represents a developer to csv file
    List,String->void
    """
    exportRowCsv(path,developer)
    
def getDevelopers(server,headers,path):
    """Get all developers of each group.
    String,dict,String->Boolean
    """
    cleanFile(path)
    developerRow=[]
    groups=getAllGroups(server,headers)
    for group in groups:
        url=server+"/rest/api/2/group/member?groupname="+group
        res=requests.get(url,headers=headers)
        #Get all users from each group
        dicres=json.loads(res.text)
        totalDevelopers=dicres.get("values")#All group users
        #Get all user information for each user in group
        for developer in totalDevelopers:
            developerRow.append(developer.get("key"))
            developerRow.append(developer.get("emailAddress"))
            developerRow.append(developer.get("displayName"))
            developerRow.append(developer.get("timeZone"))
            #Export the user to csv
            saveDevelopers(developerRow,path)
            #Save new user
            developerRow=[]
    return True

##Get Teams csv##
            
def saveTeam(path,groups):
    """Export a row that represents a team to csv file
    """
    for group in groups:
        exportRowCsv(path,group)

def getTeams(server,headers,path):
    """Get all groups stored in the Jira server.
    String,dict->Boolean"""
    cleanFile(path)
    groups=[]
    defaultGroupNames=["jira-administrators","jira-software-users","jira-core-users"]
    #The max number of group to show
    maxResults=9999
    url=server+"/rest/api/2/groups/picker?maxResults="+str(maxResults)
    res=requests.get(url,headers=headers)
    dicres=json.loads(res.text)
    for group in dicres.get("groups"):
        nameGroup=group.get("name")
        if nameGroup not in defaultGroupNames:
            groups.append(nameGroup)
    saveTeam(path,groups)
    return True

##Get devTeam csv##

def saveDevTeam(path,developers):
    """Split the developers information to get rows and export it to .csv file
    String,dict(List)->void"""
    row=[]
    #Element represents a group of developers
    for element in developers:
        registro=developers[element]#The group members
        numDevelopers=len(registro)
        for i in range(0,numDevelopers):
            #Append member to row
            row.append(developers[element][i])
            #Append group to row in the 0 index
            row.insert(0,element)
            #Export row
            exportRowCsv(path,row)
            #Clean de the row to get another one
            row=[]

def getDevTeam(server,headers,path):
    """Get all group members of each group.
    String,dict->Boolean"""
    cleanFile(path)
    groups=getAllGroups(server,headers)
    developers=defaultdict(list)
    for group in groups:
        url=server+"/rest/api/2/group/member?groupname="+group
        res=requests.get(url,headers=headers)
        if(res.status_code)==200:
            dicres=json.loads(res.text)
            for user in dicres.get("values"):
                developers[group].append(user.get("key"))
    saveDevTeam(path,developers)
    return True

##Get project csv##
    
def saveProject(path,project):
    """Export a row that represents a project to csv file
    String,List->void
    """
    exportRowCsv(path,project)

def getProjects(server,headers,path):
    """Get all projects of Jira and their attributes
    String,dict,String->Boolean
    """
    cleanFile(path)
    projects=getAllProjects(server,headers)
    projectRow=[]
    for project in projects:
        url=server+"/rest/api/2/project/"+project
        res=requests.get(url,headers=headers)
        dicres=json.loads(res.text)
        projectRow.append(dicres.get("id"))
        projectRow.append(dicres.get("name"))
        projectRow.append(dicres.get("projectTypeKey"))
        projectRow.append(dicres.get("lead").get("name"))
        saveProject(path,projectRow)
        projectRow=[]
    return True
        
##Get projectTeam csv##
        
def saveProjectTeam(path,projectTeam):
    """Export a row that represents the realtionship
    between projects and team to csv file
    List,String->void
    """
    exportRowCsv(path,projectTeam)
    
def getProjectTeam(server,headers,path):
    """Get the attributes of the relationship between
    project and team
    String,dict,String->Boolean
    """
    cleanFile(path)
    projects=getAllProjects(server,headers)
    for project in projects:
        projectRow=[]
        url=server+"/rest/api/2/project/"+project
        res=requests.get(url,headers=headers)
        dicres=json.loads(res.text)
        projectRoles=dicres.get("roles").get("Developers")
        url=projectRoles
        res=requests.get(url,headers=headers)
        dicres=json.loads(res.text)
        groupAssigned=dicres.get("actors")
        for group in groupAssigned:
            projectRow.append(project)
            projectRow.append(group.get("name"))
            saveProjectTeam(path,projectRow)
            projectRow=[]
    return True
            
##Get  boards csv##
            
def saveBoards(path,boards):
    """Export a row that represents a board to csv file
    List,String->void
    """
    exportRowCsv(path,boards)
    
def getBoards(server,headers,path):
    """Get all boards stored in Jira.
    String,dict,String->Boolean"""
    cleanFile(path)
    projects=getAllProjects(server,headers)
    for project in projects:
        boardRow=[]
        url=server+"/rest/agile/1.0/board?projectKeyOrId="+project
        res=requests.get(url,headers=headers)
        dicres=json.loads(res.text)
        totalBoards=dicres.get("values")
        for board in totalBoards:
            boardRow.append(project)
            boardRow.append(str(board.get("id")))
            boardRow.append(board.get("name"))
            saveBoards(path,boardRow)
            boardRow=[]
    return True

##Get sprint csv##
            
def saveSprint(path,sprint):
    """Export a row that represents a sprint to csv file
    List,String->void
    """
    exportRowCsv(path,sprint)
    
def getSprints(server,headers,path):
    """Get all sprints for each board.
    String,dict->void"""
    cleanFile(path)
    projects=getAllProjects(server,headers)
    for project in projects:
        url=server+"/rest/agile/1.0/board?projectKeyOrId="+project
        res=requests.get(url,headers=headers)
        dicres=json.loads(res.text)
        totalBoards=dicres.get("values")
        for board in totalBoards:
            #Sprint 0 represents the backlog of the board 
            sprintRow=[str(project),str(board.get("id")),str(0),"active","backlog",None,None,None]
            saveSprint(path,sprintRow)
            sprintRow=[]
            url=server+"/rest/agile/1.0/board/"+str(board.get("id"))+"/sprint"
            res=requests.get(url,headers=headers)
            dicres=json.loads(res.text)
            totalSprints=dicres.get("values")
            for sprint in totalSprints:
                sprintRow.append(str(project))
                sprintRow.append(str(board.get("id")))
                sprintRow.append(str(sprint.get("id")))
                sprintRow.append(sprint.get("state"))
                sprintRow.append(sprint.get("name"))
                sprintRow.append(sprint.get("startDate"))
                sprintRow.append(sprint.get("endDate"))
                sprintRow.append(sprint.get("completeDate"))
                saveSprint(path,sprintRow)
                sprintRow=[]
    return True
                
##Get issues csv##
                
def saveBacklog(path,backlog,board,project,server,headers):
    """Export many rows that represent a backlog issues to csv file
        The backlog bit must be at 1.
    String,List,Int,Int,String,dict->void
    """
    for issue in backlog:#For each issue
        url=server+"/rest/api/2/issue/"+issue
        res=requests.get(url,headers=headers)
        issue=json.loads(res.text)
        issueRow=[]
        #If the issue is not a subtask
        if not issue.get("fields").get("issuetype").get("subtask"):
            issueRow=[str(project),str(board),str(0)]#Project,board,sprint
            issueRow.append(str(issue.get("id")))
            issueRow.append(issue.get("fields").get("creator").get("key"))
            issueRow.append(issue.get("fields").get("created"))
            issueRow.append(issue.get("fields").get("issuetype").get("name"))
            try:
                issueRow.append(issue.get("fields").get("assignee").get("key"))
            except:
                issueRow.append(None)
            issueRow.append(issue.get("fields").get("summary"))
            issueRow.append(issue.get("fields").get("priority").get("name"))
            issueRow.append(issue.get("fields").get("status").get("name"))
            issueRow.append(str(issue.get("fields").get("comment").get("total")))
            issueRow.append(str(issue.get("fields").get("watches").get("watchCount")))
            issueRow.append(str(1))#Backlog bit
            saveIssues(path,issueRow)
                
def saveIssues(path,issue):
    """Export a row that represents a issue to csv file
    String,List->void"""
    exportRowCsv(path,issue)

def getIssues(server,headers,path,pathSubtask):
    """Get all issues for each sprint.
    String,dict,String,String->Boolean"""
    cleanFile(path)
    cleanFile(pathSubtask)
    ##Get all projects
    projects=getAllProjects(server,headers)
    for project in projects:#For each Jira project
        issueRow=[str(project)]
        url=server+"/rest/agile/1.0/board?projectKeyOrId="+project
        res=requests.get(url,headers=headers)
        dicres=json.loads(res.text)
        #Get all boards
        totalBoards=dicres.get("values")
        for board in totalBoards:#For each board
            issueRow.append(str(board.get("id")))
            #Get the backlog of the board
            backlog=getBacklog(server,headers,board.get("id"))
            #Store all issues of backlog
            saveBacklog(path,backlog,board.get("id"),project,server,headers)
            #Get all sprints
            url=server+"/rest/agile/1.0/board/"+str(board.get("id"))+"/sprint"
            res=requests.get(url,headers=headers)
            dicres=json.loads(res.text)
            totalSprints=dicres.get("values")
            for sprint in totalSprints:#For each sprint
                issueRow.append(str(sprint.get("id")))
                url=server+"/rest/agile/1.0/sprint/"+str(sprint.get("id"))+"/issue"
                res=requests.get(url,headers=headers)
                dicres=json.loads(res.text)
                #Get all issues
                totalIssues=dicres.get("issues")
                for issue in totalIssues:#For each issue
                    #issueSprintRow.append(str(issue.get("id")))
                    #issueRow=[]
                    if not issue.get("fields").get("issuetype").get("subtask"):
                        issueRow.append(str(issue.get("id")))
                        issueRow.append(issue.get("fields").get("creator").get("key"))
                        issueRow.append(issue.get("fields").get("created"))
                        issueRow.append(issue.get("fields").get("issuetype").get("name"))
                        try:
                            issueRow.append(issue.get("fields").get("assignee").get("key"))
                        except:
                            issueRow.append(None)
                        issueRow.append(issue.get("fields").get("summary"))
                        issueRow.append(issue.get("fields").get("priority").get("name"))
                        issueRow.append(issue.get("fields").get("status").get("name"))
                        issueRow.append(str(issue.get("fields").get("comment").get("total")))
                        issueRow.append(str(issue.get("fields").get("watches").get("watchCount")))
                        issueRow.append(str(0))
                        saveIssues(path,issueRow)
                    else:#If subtask
                        issueRow.append(str(issue.get("fields").get("parent").get("id")))
                        issueRow.append(str(issue.get("id")))
                        issueRow.append(issue.get("fields").get("creator").get("key"))
                        issueRow.append(issue.get("fields").get("created"))
                        issueRow.append(issue.get("fields").get("issuetype").get("name"))
                        try:
                            issueRow.append(issue.get("fields").get("assignee").get("key"))
                        except:
                            issueRow.append(None)
                        issueRow.append(issue.get("fields").get("summary"))
                        issueRow.append(issue.get("fields").get("priority").get("name"))
                        issueRow.append(issue.get("fields").get("status").get("name"))
                        issueRow.append(str(issue.get("fields").get("comment").get("total")))
                        issueRow.append(str(issue.get("fields").get("watches").get("watchCount")))
                        saveIssues(pathSubtask,issueRow)
                    issueRow=[str(project),str(board.get("id")),str(sprint.get("id"))]
                issueRow=[str(project),str(board.get("id"))]
            issueRow=[str(project)]
    return True

def main():
    """A file "pass.txt" is needed.The file must contains a valid
    username and password to login in your Jira server.
        pass.txt:
            username
            password
    """
    try:
        global session_cookie
        session_cookie=""
        jiraServer="http://jira.cc.uah.es:8080"
        #Login with JIRA server
        conn=login(jiraServer)
        if conn.status_code==200:
            print("Login status OK\n")
            start_time=time.time()
            #Save the cookie to get authenticated requests
            storeCookie(conn)
            #Include cookie in header requests
            headers=includeHeaders()
            print("Creating tables...")
            #REST requests to create the relacional model between JIRA entities
            if getDevelopers(jiraServer,headers,"1_developers.csv"):
                print("Developers\tOK.")
            if getTeams(jiraServer,headers,"2_teams.csv"):
                print("Teams\t\tOK.")
            if getDevTeam(jiraServer,headers,"3_devTeam.csv"):
                print("DevTeam\t\tOk.")
            if getProjects(jiraServer,headers,"4_projects.csv"):
                print("Projects\tOK.")
            if getProjectTeam(jiraServer,headers,"5_projectTeam.csv"):
                print("ProjectTeam\tOK.")
            if getBoards(jiraServer,headers,"6_boards.csv"):
                print("Boards\t\tOK.")
            if getSprints(jiraServer,headers,"7_sprints.csv"):
                print("Sprints\t\tOK.")
            if getIssues(jiraServer,headers,"8_issues.csv","9_subtask.csv"):
                print("Issues\t\tOK.\nSubtask\t\tOK.")
            print("All tables were created properly in ", round(time.time()-start_time,2) ,"seconds.")
            input("Press enter to continue.")
        else:
            print("Connection refused by Jira Server.\nCheck your credentials.")
            input("Press enter to contiune")
    except:
        print("An error ocurred\nCheck your connection with the JiraServer. ")
        input("Press enter to contiune")
        
if __name__ == "__main__":
    main()
