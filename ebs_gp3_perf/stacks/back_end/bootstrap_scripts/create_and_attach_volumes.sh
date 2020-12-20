#!/bin/bash
set -ex
set -o pipefail

# version: 18Dec2020

##################################################
#############     SET GLOBALS     ################
##################################################

REPO_NAME="ebs-gp3-perf"

GIT_REPO_URL="https://github.com/miztiik/$REPO_NAME.git"

APP_DIR="/var/$REPO_NAME"

mkdir -p ${APP_DIR}

LOG_DIR="/var/log/"
LOG_FILE="${LOG_DIR}miztiik-automation-apps-create-vol.log"

# Let us ensure latest version of CLI is installed
cd /tmp
rm -rf *
aws --version
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install --update
aws --version

# Refresh BASH profile
source ~/.bash_profile


INST_ID=`wget -q -O - http://169.254.169.254/latest/meta-data/instance-id`
EC2_AVAIL_ZONE=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone`
AWS_REGION="`echo \"$EC2_AVAIL_ZONE\" | sed 's/[a-z]$//'`"
export AWS_REGION

# We will store volume ids in a file to allow for later clean-up
VOL_IDS_LOG_NAME=${APP_DIR}/fio_vol_ids.log

###################################
#######  1000 MiBs VOLUME  ########
###################################

# Creating gp3 volume with 50G size and 1000MiBs throughput & 4000IOPS, will be attached as nvme1n1"
echo "Creating gp3 volume with 50G size and 1000MiBs throughput & 4000IOPS, will be attached as nvme1n1"  | tee ${LOG_FILE}
gp3_vol_1=$(aws ec2 create-volume \
 --availability-zone ${EC2_AVAIL_ZONE} \
 --size 51 \
 --volume-type gp3 \
 --iops 4000 \
 --throughput 1000 \
 --tag-specifications 'ResourceType=volume,Tags=[{Key=Project,Value=ebs-gp3-perf}]' --output=text --query 'VolumeId')

aws ec2 wait volume-available --volume-ids ${gp3_vol_1}
echo "new_vol_id:${gp3_vol_1}"  | tee ${LOG_FILE}
echo "${gp3_vol_1}" >> ${VOL_IDS_LOG_NAME}


########################################
#######   2000 MiBs RAID VOLUME ########
########################################

# Creating gp3 volume_1 with 50G size and 1000MiBs throughput for RAID-0, will be attached as md0
echo "Creating gp3 volume_1 with 50G size and 1000MiBs throughput for RAID-0, will be attached as md0"  | tee ${LOG_FILE}
gp3_raid_vol_1=$(aws ec2 create-volume \
 --availability-zone ${EC2_AVAIL_ZONE} \
 --size 52 \
 --volume-type gp3 \
 --iops 4000 \
 --throughput 1000 \
 --tag-specifications 'ResourceType=volume,Tags=[{Key=Project,Value=ebs-gp3-perf}]' --output=text --query 'VolumeId')

aws ec2 wait volume-available --volume-ids ${gp3_raid_vol_1}
echo "new_vol_id:${gp3_raid_vol_1}"  | tee ${LOG_FILE}
echo "${gp3_raid_vol_1}" >> ${VOL_IDS_LOG_NAME}


# Creating gp3 volume_2 with 50G size and 1000MiBs throughput for RAID-0, will be attached as md0
echo "Creating gp3 volume_2 with 50G size and 1000MiBs throughput for RAID-0, will be attached as md0"  | tee ${LOG_FILE}
gp3_raid_vol_2=$(aws ec2 create-volume \
 --availability-zone ${EC2_AVAIL_ZONE} \
 --size 52 \
 --volume-type gp3 \
 --iops 4000 \
 --throughput 1000 \
 --tag-specifications 'ResourceType=volume,Tags=[{Key=Project,Value=ebs-gp3-perf}]' --output=text --query 'VolumeId')

aws ec2 wait volume-available --volume-ids ${gp3_raid_vol_2}
echo "new_vol_id:${gp3_raid_vol_2}"  | tee ${LOG_FILE}
echo "${gp3_raid_vol_2}" >> ${VOL_IDS_LOG_NAME}


######################################
####### 16000 IOPS io2 VOLUME ########
######################################

# Creating gp3 volume with 50G size and 1000MiBs throughput & 4000IOPS, will be attached as nvme4n1"
echo "Creating io2 volume with 50G size and 4000IOPS throughput & 4000IOPS"
io2_iops_vol_1=$(aws ec2 create-volume \
 --availability-zone ${EC2_AVAIL_ZONE} \
 --size 54 \
 --volume-type io2 \
 --iops 16000 \
 --tag-specifications 'ResourceType=volume,Tags=[{Key=Project,Value=ebs-gp3-perf}]' --output=text --query 'VolumeId')

aws ec2 wait volume-available --volume-ids ${io2_iops_vol_1}
echo "new_vol_id:${io2_iops_vol_1}"
echo "${io2_iops_vol_1}" >> ${VOL_IDS_LOG_NAME}


######################################
####### 16000 IOPS gp3 VOLUME ########
######################################

# Creating gp3 volume with 16000IOPS , will be attached as nvme5n1"
echo "Creating gp3 volume with 16000IOPS, will be attached as nvme5n1"  | tee ${LOG_FILE}
gp3_iops_vol_1=$(aws ec2 create-volume \
 --availability-zone ${EC2_AVAIL_ZONE} \
 --size 55 \
 --volume-type gp3 \
 --iops 16000 \
 --throughput 1000 \
 --tag-specifications 'ResourceType=volume,Tags=[{Key=Project,Value=ebs-gp3-perf}]' --output=text --query 'VolumeId')


aws ec2 wait volume-available --volume-ids ${gp3_iops_vol_1}
echo "new_vol_id:${gp3_iops_vol_1}"  | tee ${LOG_FILE}
echo "${gp3_iops_vol_1}" >> ${VOL_IDS_LOG_NAME}

####### BEGIN ATTACHING VOLUME TO INSTANCE #######
# For NVMe devices attaching them as '/dev/sdf' aws will map it to nvm[*]n1 names

aws ec2 attach-volume --volume-id ${gp3_vol_1}      --instance-id ${INST_ID} --device /dev/sdf  | tee ${LOG_FILE}
aws ec2 attach-volume --volume-id ${gp3_raid_vol_1} --instance-id ${INST_ID} --device /dev/sdg  | tee ${LOG_FILE}
aws ec2 attach-volume --volume-id ${gp3_raid_vol_2} --instance-id ${INST_ID} --device /dev/sdh  | tee ${LOG_FILE}
aws ec2 attach-volume --volume-id ${io2_iops_vol_1} --instance-id ${INST_ID} --device /dev/sdi  | tee ${LOG_FILE}
aws ec2 attach-volume --volume-id ${gp3_iops_vol_1} --instance-id ${INST_ID} --device /dev/sdj  | tee ${LOG_FILE}

function create_raid_0(){
    echo 'Begin RAID-O Creation with NVMe devices'
    sudo mdadm --create /dev/md0 --level=0 --raid-devices=2 /dev/nvme2n1 /dev/nvme3n1 && \
    echo 'Sucessfully create RAID-O volume /dev/md0'
}


create_raid_0 >> "${LOG_FILE}"
