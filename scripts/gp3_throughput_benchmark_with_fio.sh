#!/bin/bash
set -ex
set -o pipefail

# version: 11Dec2020

##################################################
#############     SET GLOBALS     ################
##################################################

REPO_NAME="ebs-gp3-perf"

GIT_REPO_URL="https://github.com/miztiik/$REPO_NAME.git"

APP_DIR="/var/$REPO_NAME"

PERF_SCRIPTS_DIR="/var/ebs-gp3-perf/scripts/"
LOG_DIR="/var/log/"
LOG_FILE="${LOG_DIR}miztiik-automation-apps-fio-tests.log"

function clone_git_repo(){
    install_libs
    # mkdir -p /var/
    cd /var
    git clone $GIT_REPO_URL

}

function add_env_vars(){
    EC2_AVAIL_ZONE=`curl -s http://169.254.169.254/latest/meta-data/placement/availability-zone`
    AWS_REGION="`echo \"$EC2_AVAIL_ZONE\" | sed 's/[a-z]$//'`"
    export AWS_REGION
    sudo touch /var/log/miztiik-load-generator-unthrottled.log
    sudo touch /var/log/miztiik-load-generator-throttled.log
    sudo chmod 775 /var/log/miztiik-load-generator-*
    sudo chown root:ssm-user /var/log/miztiik-load-generator-*
}

function create_fio_test_configs() {

mkdir -p ${PERF_SCRIPTS_DIR} \
    && cd ${PERF_SCRIPTS_DIR} \

cat > '4kb_16threads.fio' << "EOF"
[4kb_16threads]
filename=${DEV_ID}
direct=1
rw=${TEST_MODE}
bs=16k
size=1G
numjobs=16
time_based=1
runtime=10
norandommap=1
group_reporting=1
EOF

cat > '8kb_16threads.fio' << "EOF"
[8kb_16threads]
filename=${DEV_ID}
direct=1
rw=${TEST_MODE}
bs=16k
size=1G
numjobs=16
time_based=1
runtime=10
norandommap=1
group_reporting=1
EOF

cat > '16kb_16threads.fio' << "EOF"
[16kb_16threads]
filename=${DEV_ID}
direct=1
rw=${TEST_MODE}
bs=16k
size=1G
numjobs=16
time_based=1
runtime=10
norandommap=1
group_reporting=1
EOF

cat > '32kb_16threads.fio' << "EOF"
[32kb_16threads]
filename=${DEV_ID}
direct=1
rw=${TEST_MODE}
bs=32k
size=1G
numjobs=16
time_based=1
runtime=10
norandommap=1
group_reporting=1
EOF

cat > '64kb_16threads.fio' << "EOF"
[64kb_16threads]
filename=${DEV_ID}
direct=1
rw=${TEST_MODE}
bs=64k
size=1G
numjobs=16
time_based=1
runtime=10
norandommap=1
group_reporting=1
EOF

cat > '128kb_16threads.fio' << "EOF"
[128kb_16threads]
filename=${DEV_ID}
direct=1
rw=${TEST_MODE}
bs=128k
size=1G
numjobs=16
time_based=1
runtime=10
norandommap=1
group_reporting=1
EOF

cat > '256kb_16threads.fio' << "EOF"
[256kb_16threads]
filename=${DEV_ID}
direct=1
rw=${TEST_MODE}
bs=256k
size=1G
numjobs=16
time_based=1
runtime=10
norandommap=1
group_reporting=1
EOF
}

function run_fio_perf_tests(){
    cd ${PERF_SCRIPTS_DIR}
    for _d in "nvme1n1" "md0" "nvme4n1" "nvme5n1"
        do
            for _t in "randwrite"
                do
                    for _b in "4" "8" "16" "32" "64" "128" "256"
                        do
                            printf "Beginning ${_b}kb_16threads test on ${_d} for test ${_t}\n"
                            DEV_ID=/dev/${_d} TEST_MODE=${_t} fio ${_b}kb_16threads.fio --output-format=json --output=/var/log/miztiik-automation-apps-${_b}kb_16threads_${_d}_${_t}.log
                            printf "End of ${_t} tests\n"
                        done
                done
            printf "End of test for device ${_d}\n"
        done
}

# DEV_ID=/dev/nvme1n1 fio /var/ebs-gp3-perf/fio-scripts/16kb_16threads.fio --output-format=json --output=miztiik-automation-16kb_16threads.log
# DEV_ID=/dev/nvme1n1 TEST_MODE=randread fio /var/ebs-gp3-perf/fio-scripts/16kb_16threads.fio --output-format=json --output=/var/log/miztiik-automation-16kb_16threads.log

create_fio_test_configs >> "${LOG_FILE}"
run_fio_perf_tests >> "${LOG_FILE}"

