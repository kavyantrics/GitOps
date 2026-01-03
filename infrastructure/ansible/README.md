# Ansible Playbooks

Ansible playbooks for bootstrapping and configuring EC2 instances.

## Structure

```
ansible/
├── common.yml        # Common server setup
├── jenkins.yml       # Jenkins installation and configuration
├── monitoring.yml     # Prometheus/Grafana setup
└── inventory/        # Inventory files for different environments
```

## Usage

```bash
# Install dependencies
ansible-galaxy install -r requirements.yml

# Run playbook
ansible-playbook -i inventory/prod.yml common.yml
```

## EC2 Instances

- **Jenkins**: t3.medium
- **Ansible/Bastion**: t3.micro
- **kOps cluster**: t3.medium x2
- **Monitoring**: t3.micro (optional)

