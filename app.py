from flask import Flask
from flask import render_template, request

import config
github_token = config.github_token
api_key=config.api_key
app = Flask(__name__)
message=[]
result=''
@app.route('/')
def index():
     return render_template('index.html')

@app.route("/getResponse", methods=["POST"])
def validate_user():
    if request.method == "POST":
        print(request.form['userid'])
        repository_owner = request.form['userid']
        main(repository_owner)  
    return render_template('result.html',data=message, title=repository_owner,result=result)


import requests
import openai


def check_github_username(username):
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        return True
    elif response.status_code == 404:
        return False
    else:
        # Handle other response codes if needed
        return False
    

def give_reason(key, prompt):
    openai.api_key = key  

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        temperature=0.25,
        n=1,
        stop=None,
    )

    ans= response.choices[0].text.strip()
    return ans
def fetch_github_repositories(access_token,username, page_no):
    url = f"https://api.github.com/users/{username}/repos?page={page_no}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/vnd.github.v3+json"
    }
    print("here1")
    try:
        response = requests.get(url, headers=headers)
        print("here")
        response.raise_for_status()  # Raise an exception for non-successful status codes
        repositories = response.json()
        return repositories
    except requests.exceptions.RequestException as e:
        print(f"Error fetching repositories: {e}")

def is_repository_forked(access_token,repo_owner, repo_name):
    headers = {
        'Authorization': f'Token {access_token}'
    }
    try:
        # Make a request to the GitHub API to fetch the repository information
        response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}", headers=headers)
        response.raise_for_status()  # Raise an exception if the request was not successful
        repo_data = response.json()
        # Check if the repository is a fork
        is_forked = repo_data['fork']
        return is_forked
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while retrieving repository data: {e}")
    except KeyError:
        print("Invalid response format. Repository data may be missing or incomplete.")
    return None

def fetch_top_contributors_with_commits(token,username,repo_name, num_contributors):
   

    # API endpoint for getting contributors
    contributors_url = f"https://api.github.com/repos/{username}/{repo_name}/contributors"
    headers = {
        "Authorization": f"Bearer {token}",
        'Accept': 'application/vnd.github.v3+json'
        }

    # Send GET request to the API
    response = requests.get(contributors_url,headers=headers)

    if response.status_code == 200:
        contributors_data = response.json()

        # Sort contributors by the number of commits in descending order
        sorted_contributors = sorted(contributors_data, key=lambda c: c['contributions'], reverse=True)

        # Select the top contributors with the most commits
        top_contributors = sorted_contributors[:num_contributors]

       

        return top_contributors
    else:
        # Error occurred, handle accordingly
        print(f"Error retrieving contributors: {response.status_code} - {response.text}")
        return None

def calculate_profile_score(token,username):
    # Make a request to the GitHub API to fetch the user's profile information
   
    headers = {
        "Authorization": f"Bearer {token}",
        'Accept': 'application/vnd.github.v3+json'
        }
    response = requests.get(f"https://api.github.com/users/{username}",headers=headers)
    if response.status_code == 200:
        profile_data = response.json()
        # Extract relevant information from the user's profile data
        followers_count = profile_data['followers']
        public_repos_count = profile_data['public_repos']
        commits_response = requests.get(f"https://api.github.com/users/{username}/events",headers=headers)
        if commits_response.status_code == 200:
            commits_data = commits_response.json()
            # Calculate the total number of commits made by the user
            contributions_count = sum(1 for event in commits_data if event['type'] == 'PushEvent')
        # Calculate the profile score
            profile_score = followers_count + public_repos_count + contributions_count

            return profile_score
    else:
        return 0



def get_repository_stats(token,username, repo):
    url = f"https://api.github.com/repos/{username}/{repo}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        response = requests.get(url,headers=headers)
        response.raise_for_status()  
        repository_data = response.json()
        stars_count = repository_data["stargazers_count"]
        forks_count = repository_data["forks_count"]
        return stars_count, forks_count
    except requests.exceptions.RequestException as e:
        print(f"Error retrieving repository stats: {e}")

def get_repository_issues(token,repo_owner, repo_name):

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
     # Make a request to the GitHub API to fetch the repository information
    response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}", headers=headers)
    if response.status_code == 200:
        repo_data = response.json()
        # Extract the issue count information
        open_issues_count = repo_data['open_issues_count']
        
        # Make a request to the GitHub API to fetch the list of issues
        issues_response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues?state=all", headers=headers)
        if issues_response.status_code == 200:
            issues_data = issues_response.json()
            resolved_issues_count = 0
            unresolved_issues_count = 0
            
            # Calculate the count of resolved and unresolved issues
            for issue in issues_data:
                if issue['state'] == 'open':
                    unresolved_issues_count += 1
                else:
                    resolved_issues_count += 1
            
            return resolved_issues_count, unresolved_issues_count
        
    return 0, 0
  


def get_total_commits(token,repo_owner, repo_name):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    # Make a request to the GitHub API to fetch the repository information
    response = requests.get(f"https://api.github.com/repos/{repo_owner}/{repo_name}",headers=headers)
    if response.status_code == 200:
        repo_data = response.json()
        # Extract the URL for the repository's commits endpoint
        commits_url = repo_data['commits_url'].split("{")[0]

        # Make a request to the commits endpoint to retrieve the commits data
        commits_response = requests.get(commits_url)
        if commits_response.status_code == 200:
            commits_data = commits_response.json()
            # Calculate the total number of commits on the repository
            total_commits = len(commits_data)

            return total_commits

    return 0











def main(repository_owner):
 global message,result
 page_no=1

 if(check_github_username(repository_owner)):
   num_contributors = 5 
   repo_names=[]
   contributor_scores=[]
   
   userscores={}
   # repo_score=[]
   stars_list=[]
   forks_list=[]
   resolved_issue=[]
   unresolved_issue=[]
   total_issue=[]
   total_commits=[]
 
 
   while True:
    print(github_token,repository_owner,page_no)
    repositories=fetch_github_repositories(github_token,repository_owner,page_no)
    for repo in repositories:
       repo_name =repo["name"]
       if(not is_repository_forked(github_token,repository_owner,repo_name)):
        repo_names.append(repo_name)
    page_no=page_no+1
    if len(repositories)==0:
     break
    
   # Number of top contributors to fetch
   
 #   print(repo_names)
   for repository_name in repo_names:
      message.append("")
      top_contributors = fetch_top_contributors_with_commits(github_token,repository_owner,repository_name, num_contributors)
   
      if top_contributors:
       total_score=0
       print("Top contributors with the most commits in this repository:", repository_name)
       message.append("The top contributors in repository "+repository_name+" are: ")
       for contributor in top_contributors:
           username = contributor['login']
           contributions = contributor['contributions']
           message.append("Username "+username+ " Contributions: "+ str(contributions))
           if username in userscores:
              profile_score=userscores[username]
              message.append("This is a user already present in our list. The profile score for this user is " +str(profile_score))  
           else:
            profile_score = calculate_profile_score(github_token,username)
            userscores[username]=profile_score
            print("This is a new user! The calculated profile score is "+ str(profile_score))
            message.append("This is a new user! The profile score for this user is " +str(profile_score))
           print(f"Username: {username}")
           print(f"Contributions: {contributions}")
           if profile_score:
            print(f"The profile score for user {username} is: {profile_score}")
            score=profile_score*contributions
            total_score+=score
           else:
            print(f"Failed to retrieve profile data for user {username}")
            message.append("Failed to retrieve profile data for user "+username )
           print()
       contributor_scores.append(total_score)       
       print("total repo score is", total_score)  
       message.append("Total accumulated score for this repo is: "+ str(total_score))
   
      else:
         print("No contributors found in :", repository_name)  
         contributor_scores.append(0); 
         message.append("No contributors found in :"+ repository_name)
   
      resolved, unresolved = get_repository_issues(github_token,repository_owner, repository_name)
      resolved_issue.append(resolved)
      unresolved_issue.append(unresolved)
      total_issue.append(resolved+unresolved) 
      stars, forks = get_repository_stats(github_token,repository_owner, repository_name)
      stars_list.append(stars)
      forks_list.append(forks)   
      commits = get_total_commits(github_token,repository_owner, repository_name)
      total_commits.append(commits)
      print("stars",stars,"forks",forks,"resolved",resolved,"unresolved",unresolved,"commits",commits)
      message.append("The stats for this repo are stars: "+str(stars)+" forks: "+str(forks)+" resolved issues: "+str(resolved)+" unresolved issues: "+str(unresolved)+" commits: "+str(commits))
   
   
   
   if len(repo_names)>0:
     strongest_repo=0
     max_score=0
     for i in range (len(repo_names)) :
      issue_coff=1 if total_issue[i]==0 else(((resolved_issue[i]+1)*10)/total_issue[i])
      score=(total_commits[i]+1)*(stars_list[i]+forks_list[i]+1)*issue_coff*(contributor_scores[i]+1)
      if(score>max_score):
         max_score=score
         strongest_repo=i
     
     prompt='''
     The strongest repository with the most technical complexity from a user's profile has been chosen.
     Q: Given that total commits=5000, stars= 97, forks= 88, resolved issue= 68, unresolved issue= 18, contributor scores= 10800 is chosen
     Ans: This repository was chosen as the most technically complex because it had a large number of commits,stars,forks, resoled issues and a large number of contributions.
     
     Q: Given that total commits=1000, stars= 50, forks= 20, resolved issue= 10, unresolved issue= 20, contributor scores= 10000 is chosen
     Ans: This repository was chosen as the most technically complex because it had a large number of commits,stars and a large number of contributions.
     
     Q: Given that total commits=110, stars= 4, forks= 3, resolved issue= 4, unresolved issue= 0, contributor scores= 45 is chosen
     Ans: This repository was chosen as the most technically complex because it had a large number of commits.
     
     Q: Given that total commits=1050, stars= 60, forks= 29, resolved issue= 44, unresolved issue= 12, contributor scores= 500 is chosen
     Ans: This repository was chosen as the most technically complex because it had a large number of commits,stars and resoled issues.
     
     Q: Given that total commits=1000, stars= 57, forks= 8, resolved issue= 96, unresolved issue= 15, contributor scores= 10800 is chosen
     Ans: This repository was chosen as the most technically complex because it had a large number of commits,stars, resoled issues than unresolved and a large number of contributions.
     
     Q: Given that total commits=1309, stars= 12, forks= 8, resolved issue= 82, unresolved issue= 11, contributor scores= 10800 is chosen
     Ans: This repository was chosen as the most technically complex because it had a large number of commits, resoled issues and a large number of contributions.
     
     Q: Given that total commits=10, stars= 5, forks= 8, resolved issue= 8, unresolved issue= 7, contributor scores= 108 is chosen
     Ans: This repository was chosen as the most technically because of large number of forks.
     
     Q:Given that total commits={total_commits[strongest_repo]}, stars= {stars_list[strongest_repo]}, forks= {forks_list[strongest_repo]}, resolved issue= {resolved_issue[strongest_repo]}, unresolved issue= {unresolved_issue[strongest_repo]}, contributor scores= {contributor_score[strongest_repo]} is chosen
     Ans:
     
     '''   
       
     
     print(max_score, repo_names[strongest_repo])
     ans=(give_reason(api_key,prompt))
     result=str(repo_names[strongest_repo])+" has the highest score of "+str(max_score)+"."
     result+=ans
     
   # access_token = "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"
   else:
      print("No repositories to monitor")
      result="No repositories to monitor"

 else:
    print("No such user found")
    result="No such user found"
  