from app import createApp
"""
dress up main page with gpt ~ 30 mins
"""

#Create instance of Flask application
app = createApp()

#Ensure script is being run directly
if __name__=="__main__":

    #Run application in debug mode
    app.run(debug=True)
