#@author: Giten Mitra
#Date: 21 May 2021
#Description: This script will create and make an entry in CloudFront distrubution if you are running multiple website in single EC2

import boto3
import datetime
from dateutil.parser import parse
cloudfront = boto3.client('cloudfront')
acm = boto3.client('acm')

#Converting date time format into date

def createat(date):
    dt = parse(date)
    d = dt.date()
    return d

def remove():
    response = acm.list_certificates(CertificateStatuses=['ISSUED'])
    cert = response['CertificateSummaryList']
    domain = [] 
    for d in cert:
        domain_name = d['DomainName']
        name = d['CertificateArn']
        domain.append(name)

    #Getting the ARN details
    for v in domain:
        #v is certificate ARN
        response = acm.describe_certificate(CertificateArn=v)
        created_date = str(response['Certificate']['CreatedAt'])
        #Converting to correct date format
        convert_date = str(createat(created_date))
        #print(convert_date)
        dns_name = str(response['Certificate']['DomainName'])
        if convert_date == "2019-07-04":
            try:
                now = str(datetime.datetime.now())
                Origin = 'ec2-11-1111-111-111.ap-south-1.compute.amazonaws.com' #EC2 end point
                response = cloudfront.create_distribution(
                    DistributionConfig={
                        'CallerReference': now,
                        'Aliases': {
                            'Quantity': 1,
                            'Items': [
                                # Domain Name needs to be passed here
                                "*."+dns_name,
                            ]
                        },
                        'Origins': {
                            'Quantity': 1,
                            'Items': [
                                {
                                    'Id': "custom-" + Origin,
                                    'DomainName': Origin,
                                    'CustomOriginConfig': {
                                        'HTTPPort': 80,
                                        'HTTPSPort': 443,
                                        'OriginProtocolPolicy': 'http-only',
                                        'OriginSslProtocols': {
                                            'Quantity': 1,
                                            'Items': ['TLSv1.2']
                                        },
                                        'OriginReadTimeout': 60,
                                        'OriginKeepaliveTimeout': 5
                                    }
                                },
                            ]
                        },
                        'DefaultCacheBehavior': {
                            'TargetOriginId': "custom-" + Origin,
                            'ForwardedValues': {
                                'QueryString': True,
                                'Cookies': {
                                    'Forward': 'all'
                                },
                                'Headers': {
                                    'Quantity': 4,
                                    'Items': [
                                        'Host', 'Origin', 'Refere', 'User-Agent'
                                    ]
                                },
                                'QueryStringCacheKeys': {
                                    'Quantity': 0
                                }
                            },
                            'TrustedSigners': {
                                'Enabled': False,
                                'Quantity': 0
                            },
                            'ViewerProtocolPolicy': 'allow-all',
                            'MinTTL': 0,
                            'AllowedMethods': {
                                'Quantity': 7,
                                'Items': [
                                    'GET', 'HEAD', 'POST', 'PUT', 'PATCH', 'OPTIONS', 'DELETE',
                                ],
                                'CachedMethods': {
                                    'Quantity': 2,
                                    'Items': [
                                        'GET', 'HEAD',
                                    ]
                                }
                            },
                            'DefaultTTL': 86400,
                            'MaxTTL': 31536000,
                            'Compress': True,
                        },
                        'Comment': dns_name,
                        'PriceClass': 'PriceClass_All',
                        'Enabled': True,
                        'ViewerCertificate': {
                            'CloudFrontDefaultCertificate': False,
                            'ACMCertificateArn': v,
                            'SSLSupportMethod': 'sni-only',
                            'MinimumProtocolVersion': 'TLSv1.1_2016',
                            # 'Certificate': 'string',
                            'CertificateSource': 'acm'
                        },
                        'HttpVersion': 'http2'
                    }
                )
                print("Creating CFN of: ",dns_name)
            except Exception as e:
                print(e)
        else:
            continue

remove()