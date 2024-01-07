# Setup Steps

1. Register your application [here](https://secure.splitwise.com/apps). Setting your application url to be something 
like http://localhost:8000/splitwise/oauth2
2. Copy the Consumer key and secret and copy into your .env file (duplicate .env.example and update with your 
application details)
3. Run the auth app with the following command `uvicorn splitwise_invoicing.auth:app --reload` and complete the auth in 
the browser. After that the required token should be displayed in the terminal. Then copy the token into the .env file

