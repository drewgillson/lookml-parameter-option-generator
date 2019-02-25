# What is this?
This script demonstrates how to use a scheduled look to provide parameter option values to a Google Cloud Function that automatically maintains the corresponding parameter option values specified in LookML.

## Step-by-step
1. In your LookML project, annotate the parameter options you want to maintain automatically by inserting a `# BEGIN AUTO-GENERATED PARAMETER VALUES` comment immediately before the parameter values and an `# END AUTO-GENERATED PARAMETER VALUES` comment immediately after. See [testfile.view.lkml](testfile.view.lkml) for an example.
2. Save a look that returns two columns containing the data you want to use for parameter option labels and values
3. Create a GCP project and configure the gcloud command line utility by following the [Quickstart instructions](https://cloud.google.com/functions/docs/quickstart) 
4. Clone this repository and set your own parameter values in env.yaml
5. Deploy the function with `gcloud`
    >>> `gcloud functions deploy lookml_parameter_option_generator --runtime python37 --trigger-http --env-vars-file env.yaml`
6. Create and schedule a look to be the source for parameter options
Select "Webhook" in the "Where should this data go?" section of the Schedule Events modal and enter the URL for your Google Cloud Function, which will be shown to you after successfully deploying your function. Example: https://us-central1-maintain-lookml-parameter.cloudfunctions.net/lookml_parameter_option_generator?filename=testfile&project_id=looker
    >>> 👆Replace `testfile` with the LookML filename that contains the parameter you want to maintain automatically, and replace `looker` with a project_id specified in your env.yaml file.
7. Click 'Send Test' to make a request to the Google Cloud Function immediately
8. Get function execution logs with `gcloud`
    >>> `gcloud functions logs read`
