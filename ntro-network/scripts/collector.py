import json
import logging
import paramiko
from datetime import datetime
from abc import ABC, abstractmethod
import hashlib
import os

logging.basicConfig(level=logging.INFO)

class DeviceConnection:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
    def connect(self):
        logging.info(f"Connecting to {self.host}...")
        self.client.connect(self.host, username=self.username, password=self.password, timeout=10)
        
    def execute(self, command):
        stdin, stdout, stderr = self.client.exec_command(command)
        return stdout.read().decode('utf-8')
        
    def close(self):
        self.client.close()

class VendorAdapter(ABC):
    @abstractmethod
    def detect(self, ssh_client):
        pass
        
    @abstractmethod
    def collect_raw_config(self, ssh_client):
        pass
        
    @abstractmethod
    def normalize(self, raw_config):
        pass

class NokiaSRLinuxAdapter(VendorAdapter):
    def detect(self, ssh_client):
        output = ssh_client.execute("show version")
        if "SR Linux" in output:
            return True
        return False
        
    def collect_raw_config(self, ssh_client):
        # We output JSON format for easy parsing later
        return ssh_client.execute("info from running | as json")
        
    def normalize(self, raw_config):
        try:
            data = json.loads(raw_config)
        except json.JSONDecodeError:
            data = {}
            
        normalized = {
            "device": {
                "vendor": "Nokia",
                "platform": "SR Linux",
            },
            "interfaces": [],
            "routing": [],
            "authentication": {"methods": []}
        }
        
        # We dynamically map SR Linux YANG paths to our generic schema
        if "system" in data and "aaa" in data["system"] and "authentication" in data["system"]["aaa"]:
            auth_methods = data["system"]["aaa"]["authentication"].get("authentication-method", [])
            normalized["authentication"]["methods"] = auth_methods
            
        return normalized

class SnapshotStore:
    def __init__(self, base_dir="snapshots"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        
    def store(self, device_id, raw_config, normalized_config):
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        
        raw_hash = hashlib.sha256(raw_config.encode()).hexdigest()
        
        snapshot = {
            "device_id": device_id,
            "timestamp": timestamp,
            "hash": raw_hash,
            "raw": raw_config,
            "normalized": normalized_config
        }
        
        filename = os.path.join(self.base_dir, f"{device_id}_{timestamp}.json")
        with open(filename, "w") as f:
            json.dump(snapshot, f, indent=2)
            
        logging.info(f"Stored snapshot {filename} with hash {raw_hash}")
        return snapshot

class ComplianceEngine:
    def __init__(self):
        self.rules = []
        
    def add_rule(self, name, check_func, description):
        self.rules.append({"name": name, "check": check_func, "desc": description})
        
    def evaluate(self, normalized_config):
        findings = []
        for rule in self.rules:
            passed = rule["check"](normalized_config)
            findings.append({
                "rule": rule["name"],
                "description": rule["desc"],
                "passed": passed
            })
        return findings

# Example execution if run directly
if __name__ == "__main__":
    host = "172.20.20.4" # Nokia IP
    conn = DeviceConnection(host, "admin", "NokiaSrl1!")
    try:
        conn.connect()
        adapter = NokiaSRLinuxAdapter()
        if adapter.detect(conn):
            logging.info("Detected Nokia SR Linux")
            raw = adapter.collect_raw_config(conn)
            normalized = adapter.normalize(raw)
            
            store = SnapshotStore()
            store.store("nokia-lab-01", raw, normalized)
            
            engine = ComplianceEngine()
            # Example rule: check if authentication is centralized
            engine.add_rule("AUTH-001", lambda cfg: "tacacs" in cfg.get("authentication", {}).get("methods", []), "Centralized AAA required")
            
            findings = engine.evaluate(normalized)
            print(json.dumps(findings, indent=2))
    except Exception as e:
        logging.error(f"Failed: {e}")
    finally:
        conn.close()
