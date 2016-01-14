#!/bin/bash

# this script downloads some test datasets and puts it into a format that is
# convenient for testing the effectiveness of scrubadub

# all of the data is unpacked in data/testing
bin_dir=$(dirname $0)
project_root=${bin_dir}/..
raw_dir=${project_root}/data/raw
mkdir -p ${raw_dir}

# enron
echo 'downloading enron data...'
curl https://www.cs.cmu.edu/~./enron/enron_mail_20150507.tgz > ${project_root}/enron_mail_20150507.tgz
echo 'extracting enron data...'
mkdir -p ${raw_dir}/enron
tar xzf ${project_root}/enron_mail_20150507.tgz -C ${raw_dir}/enron --strip-components=1
rm ${project_root}/enron_mail_20150507.tgz

# sms
echo 'downloading sms data...'
curl https://archive.ics.uci.edu/ml/machine-learning-databases/00228/smsspamcollection.zip > ${project_root}/smsspamcollection.zip
echo 'extracting sms data...'
unzip ${project_root}/smsspamcollection.zip -d ${raw_dir}/sms
rm ${project_root}/smsspamcollection.zip
