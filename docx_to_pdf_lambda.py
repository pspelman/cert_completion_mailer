import boto3
import os

libreoffice_bucket = boto3.resource("s3").Bucket("app-lambda-libreoffice-demo")
os.system("curl https://s3.amazonaws.com/app-lambda-libreoffice-demo/lo.tar.gz -o /tmp/lo.tar.gz && cd /tmp && tar -xf /tmp/lo.tar.gz")
output_dir = "/tmp"
convert_command = f"instdir/program/soffice --headless --invisible --nodefault --nofirststartwizard --nolockcheck --nologo --norestore --convert-to pdf --outdir {output_dir}"


def lambda_handler(event, context):
    content_type = event['content_type']
    input_file_name = event['original_s3_oid']
    output_file_name = event['converted_s3_oid']
    document_bucket_name = event['document_bucket_name']
    document_bucket = boto3.resource("s3").Bucket(document_bucket_name)

    # get item to be converted (from s3)
    with open(f'{output_dir}/{input_file_name}.{content_type}', 'wb') as data:
        document_bucket.download_fileobj(input_file_name, data)
    os.system(f"cd /tmp && {convert_command} {input_file_name}.{content_type}")  # perform conversion with libreoffice
    print("post conversion /tmp dir")
    arr = os.listdir('/tmp')
    print(arr)

    # Save converted object back to S3
    f = open(f"{output_dir}/{input_file_name}.pdf", "rb")
    document_bucket.put_object(Key=output_file_name, Body=f)
    f.close()
