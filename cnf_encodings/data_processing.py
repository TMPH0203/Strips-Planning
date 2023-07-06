import re
import matplotlib.pyplot as plt

domains = ["depot", "miconic", "rovers"]
configurations = [
    {"name": "No fluent mutex or reachable action axioms", "results": {}},
    {"name": "Only fluent mutex axioms", "results": {}},
    {"name": "Only reachable action axioms", "results": {}},
    {"name": "Both fluent mutex and reachable action axioms", "results": {}},
    {"name": "No fluent mutex or reachable action axioms for serial", "results": {}},
    {"name": "Only fluent mutex axioms for serial", "results": {}},
    {"name": "Only reachable action axioms for serial", "results": {}},
    {"name": "Both fluent mutex and reachable action axioms for serial", "results": {}}]


def extract_time(line):
    match = re.search(r"Total time: (\d+(\.\d+)?)", line)
    if match:
        return float(match.group(1))
    return None


def process_log(log_file, config):
    try:
        with open(log_file, "r") as file:
            content = file.read()
            time = extract_time(content)
            if time is not None:
                problem = log_file.split("/")[-1].split(".")[0]
                config["results"][problem] = time
    except:
        None


# Iterate over log files
for domain in domains:
    for config in configurations:
        log_prefix = f"logs/{config['name']}-{domain}-"
        for i in range(1, 11):
            log_file = f"{log_prefix}{i}.log"
            process_log(log_file, config)

# 准备绘图数据


# 绘制折线图
for domain in domains:

    plt.figure(figsize=(10, 10))
    plt.title(f"Domain: {domain}")

    for config in configurations:
        x = []
        y = []  # y轴数据
        for i in range(1, 11):
            a = config["name"]
            problem = f"{a}-{domain}-{i}"
            if problem in config["results"]:
                time = config["results"][problem]
                x.append(i)
                y.append(time)
            else:
                x.append(i)
                y.append(100)
        # 绘制折线
        if len(x) != 0:
            plt.plot(x, y, label=config["name"])

    plt.xlabel("Problem Instance")
    plt.ylabel("Time")
    plt.legend()
    plt.savefig(f"{domain}.png")

plt.show()

# 绘制折线图
for domain in domains:

    plt.figure(figsize=(10, 10))
    plt.title(f"Domain: {domain}-serial vs parallel when both")

    for config in configurations:
        x = []
        y = []  # y轴数据
        if "Both" in config["name"]:
            for i in range(1, 11):
                a = config["name"]
                problem = f"{a}-{domain}-{i}"
                if problem in config["results"]:
                    time = config["results"][problem]
                    x.append(i)
                    y.append(time)
                else:
                    x.append(i)
                    y.append(100)

            # 绘制折线
            if len(x) != 0:
                if "serial" in config["name"]:
                    plt.plot(x, y, label="serial")
                else:
                    plt.plot(x, y, label="parallel")

    plt.xlabel("Problem Instance")
    plt.ylabel("Time")
    plt.legend()
    plt.savefig(f"{domain}-serial vs parallel when both.png")

plt.show()  # 显示图形

for domain in domains:

    plt.figure(figsize=(10, 10))
    plt.title(f"Domain: {domain}-Comparison between four situation of axiom when parallel")

    for config in configurations:
        x = []
        y = []  # y轴数据
        if "serial" not in config["name"]:
            for i in range(1, 11):
                a = config["name"]
                problem = f"{a}-{domain}-{i}"
                if problem in config["results"]:
                    time = config["results"][problem]
                    x.append(i)
                    y.append(time)
                else:
                    x.append(i)
                    y.append(100)

            # 绘制折线
            if len(x) != 0:
                if "No fluent mutex" in config["name"]:
                    plt.plot(x, y, label="No Axiom")
                elif "Only fluent" in config["name"]:
                    plt.plot(x, y, label="Only fluent mutex axiom")
                elif "Only reachable" in config["name"]:
                    plt.plot(x, y, label="Only reachable action axiom")
                else:
                    plt.plot(x, y, label="Both axioms")

    plt.xlabel("Problem Instance")
    plt.ylabel("Time")
    plt.legend()
    plt.savefig(f"{domain}-Comparison between four situation of axiom when parallel.png")

plt.show()
