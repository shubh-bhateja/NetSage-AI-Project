"""
Deterministic rule checker for Cisco IOS device outputs.
Analyzes show command outputs to identify common network issues.
"""

import re

def check_duplicate_ip(show_outputs):
    """
    Checks for duplicate IP addresses in the show outputs.
    Ignores common network/broadcast addresses like 0.0.0.0 and 255.255.255.0.
    """
    issues = []
    # Match IP addresses (basic pattern)
    ip_pattern = re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b')
    ips_found = set()
    duplicates = set()
    
    ignore_list = {'0.0.0.0', '255.255.255.0', '255.255.255.255', '127.0.0.1', '255.255.255.252'}
    
    # Extract all IPs from the text
    for match in ip_pattern.finditer(show_outputs):
        ip = match.group(0)
        if ip in ignore_list:
            continue
        if ip in ips_found:
            duplicates.add(ip)
        ips_found.add(ip)
        
    for ip in duplicates:
        issues.append(f"Duplicate IP address detected: {ip}")
        
    return issues

def check_missing_vlan(show_outputs):
    """
    Parses 'show interfaces trunk' output to find VLANs mentioned in 'show vlan brief' 
    but missing from trunk allowed list.
    """
    issues = []
    # Find all VLANs configured
    vlan_pattern = re.compile(r'^(\d{1,4})\s+\w+', re.MULTILINE)
    vlans = set(vlan_pattern.findall(show_outputs))
    
    # Find trunk allowed VLANs
    trunk_pattern = re.compile(r'(\w+\d/\d+(?:/\d+)?)\s+(?:on|auto|desirable|trunk)\s+802.1q\s+trunking\s+\d+\s+([0-9,-]+)')
    
    # Look for the section with allowed VLANs
    allowed_vlan_section = re.compile(r'Port\s+Vlans allowed on trunk\n(.*?)(?=\nPort|\n\n|$)', re.DOTALL)
    for section_match in allowed_vlan_section.finditer(show_outputs):
        lines = section_match.group(1).strip().split('\n')
        for line in lines:
            parts = line.split()
            if len(parts) == 2:
                interface = parts[0]
                allowed_vlans_str = parts[1]
                
                allowed_vlans = set()
                for part in allowed_vlans_str.split(','):
                    if '-' in part:
                        try:
                            start, end = part.split('-')
                            allowed_vlans.update(str(v) for v in range(int(start), int(end) + 1))
                        except ValueError:
                            pass
                    else:
                        allowed_vlans.add(part)
                        
                # Exclude default VLAN 1 from check
                missing = [v for v in vlans if v not in allowed_vlans and v != '1']
                if missing:
                    issues.append(f"Interface {interface} trunk is missing allowed VLANs: {', '.join(missing)}")
            
    return issues

def check_interface_down(show_outputs):
    """
    Parses 'show ip interface brief' for interfaces that are down/down or administratively down.
    """
    issues = []
    # e.g., GigabitEthernet0/1 192.168.1.1 YES NVRAM administratively down down
    pattern = re.compile(r'^([A-Za-z0-9/.-]+)\s+(?:[0-9.]+|unassigned)\s+\w+\s+\w+\s+(administratively down|down)\s+(down)', re.MULTILINE)
    
    for match in pattern.finditer(show_outputs):
        interface = match.group(1)
        status = match.group(2)
        protocol = match.group(3)
        issues.append(f"Interface {interface} is {status}/{protocol}")
        
    return issues

def check_subnet_mask(show_outputs):
    """
    Detects obviously wrong subnet masks (e.g., /32 on interface config).
    """
    issues = []
    # Look for subnet mask 255.255.255.255 on a regular interface IP address
    pattern = re.compile(r'^\s*ip address ([0-9.]+) (255\.255\.255\.255)', re.MULTILINE)
    for match in pattern.finditer(show_outputs):
        ip = match.group(1)
        issues.append(f"Suspicious subnet mask 255.255.255.255 configured for IP {ip}")
    return issues

def check_default_route(show_outputs):
    """
    Checks if 'show ip route' output has a default route (0.0.0.0/0 or S* or Gateway of last resort).
    """
    issues = []
    if 'show ip route' in show_outputs.lower():
        if 'Gateway of last resort is not set' in show_outputs and '0.0.0.0' not in show_outputs and 'S*' not in show_outputs:
            issues.append("No default route (0.0.0.0/0 or Gateway of last resort) is configured.")
    return issues

def check_nat_config(show_outputs):
    """
    If NAT-related output is present, checks for missing 'ip nat inside' or 'ip nat outside' indicators.
    """
    issues = []
    if 'ip nat' in show_outputs.lower():
        inside_match = re.search(r'ip nat inside', show_outputs)
        outside_match = re.search(r'ip nat outside', show_outputs)
        if not inside_match or not outside_match:
            issues.append("NAT commands present, but might be missing 'ip nat inside' or 'ip nat outside' definitions.")
    return issues

def check_ospf_adjacency(show_outputs):
    """
    If OSPF output is present, checks for missing neighbors or FULL/TWO-WAY state issues.
    """
    issues = []
    if 'show ip ospf neighbor' in show_outputs.lower() or 'ospf' in show_outputs.lower():
        # Match lines like: 192.168.1.2       1   EXSTART/DR      00:00:32    10.0.0.2        GigabitEthernet0/0
        pattern = re.compile(r'^([0-9.]+)\s+\d+\s+([A-Z0-9/]+)\s+', re.MULTILINE)
        for match in pattern.finditer(show_outputs):
            neighbor = match.group(1)
            state = match.group(2)
            if 'FULL' not in state and '2WAY' not in state:
                issues.append(f"OSPF neighbor {neighbor} is in a non-optimal state: {state}")
    return issues

def check_acl_order(show_outputs):
    """
    If access-list output is present, checks if 'permit ip any any' or 'permit any' appears before more specific deny rules.
    """
    issues = []
    if 'access-list' in show_outputs.lower() or 'ip access-list' in show_outputs.lower():
        permit_any_pos = show_outputs.find('permit ip any any')
        if permit_any_pos == -1:
            permit_any_pos = show_outputs.find('permit any')
            
        if permit_any_pos != -1:
            deny_pos = show_outputs.find('deny', permit_any_pos)
            if deny_pos != -1:
                issues.append("ACL Warning: 'permit any' rule appears before a 'deny' rule, potentially making the deny rule ineffective.")
    return issues

def check_dhcp_pool(show_outputs):
    """
    If DHCP pool output is present, checks for pool exhaustion (utilization 100%) or missing configuration.
    """
    issues = []
    if 'show ip dhcp pool' in show_outputs.lower() or 'dhcp' in show_outputs.lower():
        # Look for 100% utilization in the output
        if '100%' in show_outputs or '0 free' in show_outputs.lower():
             issues.append("DHCP pool may be exhausted (100% utilization or 0 free addresses detected).")
    return issues

def check_gateway_reachability(show_outputs):
    """
    If both route table and interface brief are present, verifies the default gateway IP exists on a connected network.
    """
    issues = []
    gw_pattern = re.search(r'Gateway of last resort is ([0-9.]+) to network', show_outputs)
    if gw_pattern:
        gw_ip = gw_pattern.group(1)
        if gw_ip != '0.0.0.0':
            # This is a simplified check for reachability based on connected networks
            if 'C ' not in show_outputs or gw_ip not in show_outputs:
                issues.append(f"Gateway IP {gw_ip} might not be reachable (missing connected route).")
    return issues

def run_deterministic_checks(show_outputs):
    """
    Runs all deterministic checks and returns a list of warning/error strings.
    """
    issues = []
    issues.extend(check_duplicate_ip(show_outputs))
    issues.extend(check_missing_vlan(show_outputs))
    issues.extend(check_interface_down(show_outputs))
    issues.extend(check_subnet_mask(show_outputs))
    issues.extend(check_default_route(show_outputs))
    issues.extend(check_nat_config(show_outputs))
    issues.extend(check_ospf_adjacency(show_outputs))
    issues.extend(check_acl_order(show_outputs))
    issues.extend(check_dhcp_pool(show_outputs))
    issues.extend(check_gateway_reachability(show_outputs))
    return issues

if __name__ == '__main__':
    sample_output = '''
show ip interface brief
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0     192.168.1.1     YES NVRAM  up                    up
GigabitEthernet0/1     10.0.0.1        YES NVRAM  administratively down down
GigabitEthernet0/2     192.168.1.1     YES NVRAM  up                    up

show ip route
Gateway of last resort is not set

10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C        10.0.0.0/24 is directly connected, GigabitEthernet0/1

show vlan brief
VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Gi1/0/1, Gi1/0/2
10   Data                             active    
20   Voice                            active    

show interfaces trunk
Port        Mode             Encapsulation  Status        Native vlan
Gi1/0/1     on               802.1q         trunking      1

Port        Vlans allowed on trunk
Gi1/0/1     1,10

show ip ospf neighbor
Neighbor ID     Pri   State           Dead Time   Address         Interface
192.168.1.2       1   EXSTART/DR      00:00:32    10.0.0.2        GigabitEthernet0/0

access-list 100 permit ip any any
access-list 100 deny ip host 10.0.0.5 any

ip address 10.1.1.1 255.255.255.255
'''
    print("Running deterministic checks on sample output...\n")
    issues = run_deterministic_checks(sample_output)
    if issues:
        for issue in issues:
            print(f"- {issue}")
    else:
        print("No issues found.")
