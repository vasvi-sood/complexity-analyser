# Github Complexity Analyser
This application will return the technically most complex repository when a github username is inputed.

## Running locally
### Requirements
This application has been created using flask.
<ol>
<li>Clone the repository</li>
  
```
git clone https://github.com/vasvi-sood/complexity-analyser
```

<li>cd into the repository using the command 
  
  ```cd complexity-analyser```

</li>
<li>Create a new Python environment and activate it. </li>
<li> Download the requirements using the command 
  
  ```pip install -r requirements.txt```
  
  . Make sure pip is installed</li>
<li>Create a file named 
  
  ```config.py``` 
  
  and paste the following code: 
  
 ```
github_token = YOUR GITHUB TOKEN
api_key=YOUR GPT API KEY
```
Remember to replace [YOUR GITHUB TOKEN](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) with your own github token and [YOUR GPT API KEY](https://help.openai.com/en/articles/4936850-where-do-i-find-my-secret-api-key) with your own oprnai API key.
</li>
</ol>

### To run 
Now to finally run the application use the command

```flask --app app run ```

<br>
Congrats, the app is running locally now.

