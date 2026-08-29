import re

def check_duplicate_ip(show_outputs):
    """Simple heuristic: if an IP appears multiple times in arp or route context."""
    # Simplified check for demonstration
    ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
    ips = re.findall(ip_pattern, show_outputs)
    duplicates = set([ip for ip in ips if ips.count(ip) > 1])
    if duplicates:
        return f"Warning: Duplicate IPs or overlapping subnets detected: {duplicates}"
    return None

def check_missing_vlan(show_outputs):
    """Checks if VLAN 30 is missing from trunk configuration."""
    if 'show interfaces trunk' in show_outputs and '30' not in show_outputs:
        return "Warning: VLAN 30 might be missing from trunk allowed list."
    return None

def run_deterministic_checks(show_outputs):
    """Run all deterministic checks on the provided output."""
    errors = []
    
    dup_ip = check_duplicate_ip(show_outputs)
    if dup_ip:
        errors.append(dup_ip)
        
    miss_vlan = check_missing_vlan(show_outputs)
    if miss_vlan:
        errors.append(miss_vlan)
        
    if "down" in show_outputs.lower() and "line protocol is down" in show_outputs.lower():
        errors.append("Warning: An interface is down/down. Check physical connectivity or port security.")
        
    return errors

if __name__ == "__main__":
    # Sample Test
    sample = "Interface GigabitEthernet0/0\n  IP address 192.168.1.1\nshow interfaces trunk\nAllowed vlans: 10,20\n"
    print("Testing Rule Checker on sample output:")
    for err in run_deterministic_checks(sample):
        print("-", err)
