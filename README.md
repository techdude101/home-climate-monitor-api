# home-climate-monitor-api
Home Climate Monitor - DB API

## DB Setup
Create a free MongoDB Atlas account   
Create a cluster  
Get the connection string of the cluster  
  
1. Add a new database user  
  Under Security click Database Access  
  Click ADD NEW DATABASE USER  
	Enter a username  
	Enter a password  
	Leave all other options as default  
	Click Add User  
2. Click Connect  
3. Click Connect your application  
4. Change Driver to Python & Version to 3.6 or later  
5. Copy the connection string and paste into a text editor  
6. Edit the connection string  
	
	Before:
    mongodb+srv://<user>:<password>@cluster0.ABCDE.mongodb.net/myFirstDatabase?retryWrites=true&w=majority  
		
		Change myFirstDatabase?retryWrites=true&w=majority to homeClimateMonitorDB  
		Change <user> & <password> to the username and password you entered previously  
		
	After:
		mongodb+srv://<user>:<password>@cluster0.ABCDE.mongodb.net/homeClimateMonitorDB
		
## API Setup
### Heroku app setup
	Create a heroku account
	Create a new app 
		Choose an app name e.g. my-home-climate-monitor
		App name = my-home-climate-monitor
		Region: United States or Europe
		Click Create app

	Add the DB connection info
		Navigate to the Settings tab
		Click the Reveal Config Vars button
	
		Set KEY = DB_URL
		Set VALUE = mongodb+srv://<user>:<password>@cluster0.ABCDE.mongodb.net/homeClimateMonitorDB
		Click the Add button
	

	Open a command prompt (Windows) or terminal (Linux / MacOS)
	Clone the repository - git clone https://github.com/techdude101/home-climate-monitor-api.git

### Deploy using Heroku Git
	heroku login (opens a web browser)
	
	heroku git:remote -a <app name>
	
	git push heroku main:master
	
	heroku logs --tail
	Look for #### Admin api key = abcdefgh-1234-5678-9abc-defghijklmno ####
	Use this key to add devices
	
The API should now be successfully deployed to heroku  
Click Open app from the heroku page or open a web browser to https://<your-app-name>.herokuapp.com/  
You should see - {"message":"Home Climate Monitor API"}  
