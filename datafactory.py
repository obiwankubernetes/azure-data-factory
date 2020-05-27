# pip install : azure-mgmt-resource and azure-mgmt-datafactory

# import libraries
from azure.common.credentials import ServicePrincipalCredentials
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.datafactory import DataFactoryManagementClient
from azure.mgmt.datafactory.models import *
from datetime import datetime, timedelta
import time

# Add the following functions that print information.
def print_item(group):
    """Print an Azure object instance."""
    print("\tName: {}".format(group.name))
    print("\tId: {}".format(group.id))
    if hasattr(group, 'location'):
        print("\tLocation: {}".format(group.location))
    if hasattr(group, 'tags'):
        print("\tTags: {}".format(group.tags))
    if hasattr(group, 'properties'):
        print_properties(group.properties)

def print_properties(props):
    """Print a ResourceGroup properties instance."""
    if props and hasattr(props, 'provisioning_state') and props.provisioning_state:
        print("\tProperties:")
        print("\t\tProvisioning State: {}".format(props.provisioning_state))
    print("\n\n")

def print_activity_run_details(activity_run):
    """Print activity run details."""
    print("\n\tActivity run details\n")
    print("\tActivity run status: {}".format(activity_run.status))
    if activity_run.status == 'Succeeded':
        print("\tNumber of bytes read: {}".format(activity_run.output['dataRead']))
        print("\tNumber of bytes written: {}".format(activity_run.output['dataWritten']))
        print("\tCopy duration: {}".format(activity_run.output['copyDuration']))
    else:
        print("\tErrors: {}".format(activity_run.error['message']))

# Add the following code to the Main method that creates an instance of DataFactoryManagementClient class. You use this object to create the data factory, linked service, datasets, and pipeline. You also use this object to monitor the pipeline run details.
def main():

    # Azure subscription ID
    subscription_id = '57a30d11-5ae0-4fe4-86b4-48412bbfcd09'

    # This program creates this resource group. If it's an existing resource group, comment out the code that creates the resource group
    rg_name = 'YoutubeStatsResourceGroup'

    # The data factory name. It must be globally unique.
    df_name = 'ytdatablobtosql'

    # Specify your Active Directory client ID, client secret, and tenant ID
    # credentials = ServicePrincipalCredentials(client_id='<Active Directory application/client ID>', secret='<client secret>', tenant='<Active Directory tenant ID>')
    # resource_client = ResourceManagementClient(credentials, subscription_id)
    # adf_client = DataFactoryManagementClient(credentials, subscription_id)

    rg_params = {'location':'eastus'}
    df_params = {'location':'eastus'}

    # create the resource group
    # comment out if the resource group already exits
    # resource_client.resource_groups.create_or_update(rg_name, rg_params)

    #Create a data factory
    df_resource = Factory(location='eastus')
    df = adf_client.factories.create_or_update(rg_name, df_name, df_resource)
    print_item(df)
    while df.provisioning_state != 'Succeeded':
        df = adf_client.factories.get(rg_name, df_name)
        time.sleep(1)

    # create a linked service
    # Create an Azure Storage linked service
    ls_name = 'storageLinkedService'

    # IMPORTANT: specify the name and key of your Azure Storage account.
    storage_string = SecureString(value='DefaultEndpointsProtocol=https;AccountName=<storageaccountname>;AccountKey=<storageaccountkey>')

    ls_azure_storage = AzureStorageLinkedService(connection_string=storage_string)
    ls = adf_client.linked_services.create_or_update(rg_name, df_name, ls_name, ls_azure_storage)
    print_item(ls)

    # create datasets

    # one for blob storage (input)
    ds_name = 'ds_in'
    ds_ls = LinkedServiceReference(reference_name=ls_name)
    blob_path= 'adfv2tutorial/input'
    blob_filename = 'mircrosoft_visual_studio.json'
    ds_azure_blob= AzureBlobDataset(linked_service_name=ds_ls, folder_path=blob_path, file_name = blob_filename)
    ds = adf_client.datasets.create_or_update(rg_name, df_name, ds_name, ds_azure_blob)
    print_item(ds)

    # one for cosmosdb sink (output)
    dsOut_name = 'ds_out'
    output_blobpath = 'adfv2tutorial/output'
    dsOut_azure_blob = AzureBlobDataset(linked_service_name=ds_ls, folder_path=output_blobpath)
    dsOut = adf_client.datasets.create_or_update(rg_name, df_name, dsOut_name, dsOut_azure_blob)
    print_item(dsOut)

    uri -> https://ytstatscosmosdb.documents.azure.com:443/
    primary key -> ymoxP8HBRDqSojd75R675C5dfNRkbF49YtuPdcnCMIsh1tsJVpKHFiLklYJe1VxMBNuQ5daegdZMOZOp1j8gRg==
    primary connection string -> AccountEndpoint=https://ytstatscosmosdb.documents.azure.com:443/;AccountKey=ymoxP8HBRDqSojd75R675C5dfNRkbF49YtuPdcnCMIsh1tsJVpKHFiLklYJe1VxMBNuQ5daegdZMOZOp1j8gRg==;