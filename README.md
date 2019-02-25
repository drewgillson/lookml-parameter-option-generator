# Create and schedule a look to be the source for parameter options
Select "Webhook" in the "Where should this data go?" section of the Schedule Events modal and enter the URL for your Google Cloud Function
Example: https://us-central1-maintain-lookml-parameter.cloudfunctions.net/lookml_parameter_option_generator?filename=`testfile`&project_id=`looker` 
👆Replace `testfile` with the LookML filename that contains the parameter you want to maintain automatically, and replace `looker` with a project_id specified in your env.yaml file.
 

# Deploy the Google Cloud Function
`gcloud functions deploy lookml_parameter_option_generator --runtime python37 --trigger-http --env-vars-file env.yaml`

# Get logs from function execution
`gcloud functions logs read`
