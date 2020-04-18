import time
import os
from collections import deque


class PerformanceCounter:
    metrics = []
    metric = {}

    @classmethod
    def init(cls, metrics):
        cls.metrics = metrics
        for metric in metrics:
            cls.metric[metric] = {
                "n_values": 0,
                "max_value": 0,
                "mean_value": 0,
                "last": deque(maxlen=10),
                "mean_last": 0,
            }

    @classmethod
    def end_metric(cls, metric):
        if metric in cls.metrics:
            cls.metric[metric]["n_values"] += 1
            cls.metric[metric]["end_time"] = time.time()
            cls.metric[metric]["current_time"] = (
                cls.metric[metric]["end_time"]
                - cls.metric[metric]["start_time"]
            )
            if (
                cls.metric[metric]["current_time"]
                > cls.metric[metric]["max_value"]
            ):
                cls.metric[metric]["max_value"] = cls.metric[metric][
                    "current_time"
                ]

            cls.metric[metric]["mean_value"] = (
                cls.metric[metric]["mean_value"]
                * (cls.metric[metric]["n_values"] - 1)
                + cls.metric[metric]["current_time"]
            ) / cls.metric[metric]["n_values"]

            cls.metric[metric]["last"].append(
                cls.metric[metric]["current_time"]
            )
            cls.metric[metric]["mean_last"] = sum(
                cls.metric[metric]["last"]
            ) / len(cls.metric[metric]["last"])

    @classmethod
    def start_metric(cls, metric):
        if metric in cls.metrics:
            cls.metric[metric]["start_time"] = time.time()

    @classmethod
    def summary(cls):
        res = "Summary of metrics" + os.linesep
        res += "_" * 92 + os.linesep
        res += (
            "{:20}{:17}{:17}{:17}{:17}".format(
                "Metric",
                "Nb. values",
                "Max. value (s)",
                "Mean value (s)",
                "Mean value (10 lasts)",
            )
            + os.linesep
        )
        res += "=" * 92 + os.linesep

        for metric_name, metric in cls.metric.items():
            res += (
                "{:20}{:17}{:17e}{:17e}{:17e}\n".format(
                    metric_name,
                    metric["n_values"],
                    metric["max_value"],
                    metric["mean_value"],
                    metric["mean_last"],
                )
                + os.linesep
                + "_" * 92
                + os.linesep
            )

        print(res)

    @staticmethod
    def timed(name):
        def timing(func):
            def wrapper(*args, **kwargs):
                PerformanceCounter.start_metric(name)
                res = func(*args, **kwargs)
                PerformanceCounter.end_metric(name)
                return res

            return wrapper

        return timing
