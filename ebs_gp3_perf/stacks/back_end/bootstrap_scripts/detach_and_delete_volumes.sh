#!/bin/bash
set -ex
set -o pipefail

# version: 20Dec2020

##################################################
#############     SET GLOBALS     ################
##################################################

REPO_NAME="ebs-gp3-perf"

GIT_REPO_URL="https://github.com/miztiik/$REPO_NAME.git"

APP_DIR="/var/$REPO_NAME"

mkdir -p ${APP_DIR}

LOG_DIR="/var/log/"
LOG_FILE="${LOG_DIR}miztiik-automation-apps-delete-vol.log"


# We will store volume ids in a file to allow for later clean-up
VOL_IDS_LOG_NAME=${APP_DIR}/fio_vol_ids.log

function detach_and_delete_vols(){
    
    for _v in `cat ${VOL_IDS_LOG_NAME}`
        do
            aws ec2 detach-volume --volume-id ${_v} && \
            aws ec2 wait volume-available --volume-ids ${_v} && \
            aws ec2 delete-volume --volume-id ${_v}
        done
        echo "successfully_deleted_vol:${_v}" | tee ${LOG_FILE}
}



# After sucessfully deleting clean-up the log file
detach_and_delete_vols && \
> ${VOL_IDS_LOG_NAME}
