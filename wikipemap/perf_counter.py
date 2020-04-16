import time
import os


class PerformanceCounter:
    metrics = None
    metric = {}

    @classmethod
    def init(cls, metrics):
        cls.metrics = metrics
        for metric in metrics:
            cls.metric[metric] = {
                "n_values": 0,
                "max_value": 0,
                "mean_value": 0,
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

    @classmethod
    def start_metric(cls, metric):
        if metric in cls.metrics:
            cls.metric[metric]["start_time"] = time.time()

    @classmethod
    def summary(cls):
        res = "Summary of metrics" + os.linesep
        res += "_" * 66 + os.linesep
        res += (
            "{:15}{:17}{:17}{:17}".format(
                "Metric", "Nb. values", "Max. value (s)", "Mean value (s)"
            )
            + os.linesep
        )
        res += "=" * 66 + os.linesep

        for metric_name, metric in cls.metric.items():
            res += (
                "{:15}{:17.7}{:17.7}{:17.7}\n".format(
                    metric_name,
                    str(metric["n_values"]),
                    str(metric["max_value"]),
                    str(metric["mean_value"]),
                )
                + os.linesep
                + "_" * 66
                + os.linesep
            )

        print(res)
