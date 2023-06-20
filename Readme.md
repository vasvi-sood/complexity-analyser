# Github Complexity Analyser
This application will return the technically most complex repository when a github username is inputed.

## Running locally
### Requirements
This application has been created using flask.
<ol>
<li>Clone the repository
```
git clone https://github.com/vasvi-sood/complexity-analyser
```</li>
<li>cd into the repositor using the command ```cd complexity-analyser``` </li>
<li>Create a new python environment and activate it. </li>
<li> Download the requirements using the command ```pip install -r requirements.txt```. Make sure pip is installed</li>
<li>Create a file named ```config.py``` and paste the following code: ````
github_token = YOUR GITHUB TOKEM
api_key=YOUR GPT API KEY
```</li>
</ol>

### To run 
Now to finally run the application use the command ```flask --app app run ```.
<br>
Congrats, the app is running locally now.

