from flask import Flask, request, render_template
import boto3
import os
import datetime

app = Flask(__name__)

AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']

SIMPLE_DB_DOMAIN_NAME = os.environ['SIMPLE_DB_DOMAIN_NAME']

QUEUE_NAME = os.environ['QUEUE_NAME']
BUCKET_NAME = os.environ['BUCKET_NAME']
BUCKET_URL = 'https://s3-us-west-2.amazonaws.com/{}'.format(BUCKET_NAME)

#s3 = boto3.resource('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
#sqs = boto3.resource('sqs', region_name='us-west-2', aws_access_key_id=AWS_ACCESS_KEY_ID,
#                     aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
#queue = sqs.get_queue_by_name(QueueName=QUEUE_NAME)
#
#sdb = boto3.client('sdb', region_name='us-west-2', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/done')
def done():
    return render_template('done.html')

@app.route('/choose')
def modify():
    client = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-west-2')
    response = client.list_objects_v2(
    Bucket = 'projekt-psoir1',
    Prefix = 'uploads/'
    )
    image_list = []
    for image in response["Contents"]:
       image_list.append(image["Key"].split('/')[1])
    return render_template('choose.html', image_list=image_list)


@app.route('/queue', methods=["POST"])
def queue():
    image_list = request.form.getlist("uploads")
    sqs = boto3.resource("sqs", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-west-2')
    queue = sqs.get_queue_by_name(QueueName="projekt-psoir-queue")
    simpledb = boto3.client("sdb", aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY, region_name='us-west-2')
    for image_name in image_list:
        queue.send_message(MessageBody="{0}".format(image_name))
        simpledb.put_attributes(DomainName="PsoirSimpleDB", ItemName="Image",
        Attributes=[{"Name":"Name", "Value":image_name, "Replace":True}])

    return render_template("sent.html")


if __name__ == '__main__':
    app.run()

