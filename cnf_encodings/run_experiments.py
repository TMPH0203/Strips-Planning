import subprocess

domains = ["depot", "miconic", "rovers"]
configurations = [
    {"name": "No fluent mutex or reachable action axioms", "args": ["-p", "false"]},
    {"name": "Only fluent mutex axioms", "args": ["-p", "true", "-l", "fmutex"]},
    {"name": "Only reachable action axioms", "args": ["-p", "true", "-l", "reachable"]},
    {"name": "Both fluent mutex and reachable action axioms", "args": ["-p", "true", "-l", "both"]},
    {"name": "No fluent mutex or reachable action axioms for serial", "args": ["-x", "serial", "-p", "false"]},
    {"name": "Only fluent mutex axioms for serial", "args": ["-x", "serial", "-p", "true", "-l", "fmutex"]},
    {"name": "Only reachable action axioms for serial", "args": ["-x", "serial", "-p", "true", "-l", "reachable"]},
    {"name": "Both fluent mutex and reachable action axioms for serial", "args": ["-x", "serial", "-p", "true", "-l", "both"]},
]

def run_experiment(domain, config):
    print(f"Running experiment for domain: {domain}, configuration: {config['name']}")
    for i in range(1, 11):
        cmd = f"timeout 100 python3 -u ../planner.py ../benchmarks/{domain}/domain.pddl ../benchmarks/{domain}/problem{i:02d}.pddl {domain}-{i} 1:30:1 -x parallel {' '.join(config['args'])} -q ramp -r true"
        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, timeout=100)
            with open(f"logs/{config['name']}-{domain}-{i}.log", "w") as file:
                file.write(output.decode())
                print(f"Finished problem {i}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred while running experiment for problem {i}:")
            # print(e.output.decode())
        except subprocess.TimeoutExpired:
            print(f"Timeout occurred while running experiment for problem {i}")

    print("=" * 50)

for domain in domains:
    for config in configurations:
        run_experiment(domain, config)


