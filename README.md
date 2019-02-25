# What is this?
This script demonstrates how to use a scheduled look to provide parameter option values to a Google Cloud Function, which will automatically maintain corresponding parameter option values specified in a LookML file.

## Step-by-step
1. In a file in your LookML project, annotate the parameter options you want to maintain automatically by inserting a `# BEGIN AUTO-GENERATED PARAMETER VALUES` comment immediately before the parameter option values and an `# END AUTO-GENERATED PARAMETER VALUES` comment immediately afterwards. See [testfile.view.lkml](testfile.view.lkml) for an example.
2. Save a look that returns two columns containing the data you want to use for parameter option labels and values. In this example, the look contains two columns, "Event Name" and "Event ID". 
3. Clone this repository and set your own parameter values in [env.yaml](env.yaml). You will need a Github API token that has permission to make changes to the repository containing your LookML files, and the Outgoing Webhook Token from your Looker instance.
4. Create a GCP project and configure the gcloud command line utility by following the [Quickstart instructions](https://cloud.google.com/functions/docs/quickstart) 
5. Deploy the function with `gcloud` (run this command in the directory containing the files from this repository)
    > `gcloud functions deploy lookml_parameter_option_generator --runtime python37 --trigger-http --env-vars-file env.yaml`
6. Schedule your previously saved look to provide results via webhook every five minutes, and only if the results have changed. Select "Webhook" in the "Where should this data go?" section of the Schedule Events modal, then enter the URL for your Google Cloud Function. Choose "JSON - Simple" in the "Format data as" section.
    > Example Webhook URL: https://us-central1-maintain-lookml-parameter.cloudfunctions.net/lookml_parameter_option_generator?filename=testfile&project_id=looker (replace `testfile` with the LookML filename that contains the parameter you want to maintain automatically, and replace `looker` with a project_id specified in your env.yaml file)
7. Click 'Send Test' to make a request to your Google Cloud Function immediately
8. Get function execution logs with `gcloud`
    > `gcloud functions logs read`

## How will I know this works?
The expected outcome from this example is that if a new row is included in the results from your scheduled look, the file containing your LookML parameter definition will have a new option for the parameter. For example, if the look results included a new row with _Seventy Seven_ in the "Event Name" field and _77_ in the "Event ID" field, the following option will be automatically added to your parameter definition within a few minutes:
```
allowed_value: {
  label: "Fifty Six"
  value: "56"
}
```
