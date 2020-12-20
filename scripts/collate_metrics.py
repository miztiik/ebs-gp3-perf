#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
import logging
import json
import datetime
import os


class GlobalArgs:
    """ Global statics """
    OWNER = "Mystique"
    ENVIRONMENT = "production"
    MODULE_NAME = "log_processor"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FILE_NAME = "/var/log/miztiik-automation-apps-log_processor.log"
    INSERT_DURATION = 57
    RANDOM_SLEEP_SECS = int(os.getenv("RANDOM_SLEEP_SECS", 2))
    ANDON_CORD_PULLED = os.getenv("ANDON_CORD_PULLED", False)
    FIO_TEST_CONFIG = {
        "output_f_prefix": "/var/log/miztiik-automation-apps-",
        "threads": 16,
        "block_size": [4, 8, 16, 32, 64, 128, 256],
        "mode": "randwrite",
        "devs_map": {
            "nvme1n1": "gp3_throughput_1000",
            "md0": "gp3_throughput_2000_with_raid_0",
            "nvme4n1": "io2_iops_16000",
            "nvme5n1": "gp3_iops_16000"
        }
    }


def read_log(path_to_file):
    with open(path_to_file) as f:
        data = json.load(f)
        return data


def json_to_csv(data, csv_f_name):
    with open(csv_f_name, 'w') as f:
        dw = csv.DictWriter(f, data[0].keys())
        dw.writeheader()
        for row in data:
            dw.writerow(row)


def log_processor():
    perf_results = []
    # Loop for all the block size
    for _i in GlobalArgs.FIO_TEST_CONFIG["block_size"]:
        # Loop for all the devices
        for _k in GlobalArgs.FIO_TEST_CONFIG["devs_map"]:
            _temp_result = {}
            # Read the log file
            __fio_log_name = (
                f"{GlobalArgs.FIO_TEST_CONFIG['output_f_prefix']}"
                f"{_i}kb_"
                f"{GlobalArgs.FIO_TEST_CONFIG['threads']}threads_"
                f"{_k}_"
                f"{GlobalArgs.FIO_TEST_CONFIG['mode']}.log"
            )
            print(f"processing_file:{__fio_log_name}")
            _d = read_log(__fio_log_name)
            # Parse our results
            _temp_result["test_name"] = GlobalArgs.FIO_TEST_CONFIG["devs_map"][_k]
            _temp_result["mode"] = _d["jobs"][0]["job options"]["rw"]
            _temp_result["block_size"] = _i
            _temp_result["threads"] = _d["jobs"][0]["job options"]["numjobs"]
            _temp_result["w_iops"] = round(_d["jobs"][0]["write"]["iops"])
            _temp_result["bw_in_mibs"] = round(
                _d["jobs"][0]["write"]["bw"]/1024)
            _temp_result["dev"] = _d["jobs"][0]["job options"]["filename"]
            # Add to global results
            perf_results.append(_temp_result)
            print(_temp_result)
            print("-------------------------")
    return perf_results


logger = logging.getLogger()
logger = logging.getLogger()
logging.basicConfig(
    filename=f"{GlobalArgs.LOG_FILE_NAME}",
    filemode='a',
    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=GlobalArgs.LOG_LEVEL
)


perf_results = log_processor()
print(perf_results)
json_to_csv(
    perf_results, f"fio_results_{round(datetime.datetime.now().timestamp())}.csv")
# json_to_csv(a, "fio_results.csv")
