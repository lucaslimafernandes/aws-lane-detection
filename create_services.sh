awslocal s3 mb s3://lane-bucket

awslocal sqs create-queue --queue-name future-processing

awslocal sns create-topic --name alertas

# Deve ser feito após o container estar de pé
# Devido a necessidade de confirmação
# awslocal sns subscribe \   
#   --topic-arn arn:aws:sns:us-east-1:000000000000:alertas \
#   --protocol http \
#   --notification-endpoint http://notifier:8081/sns-telegram

