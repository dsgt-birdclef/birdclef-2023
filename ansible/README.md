# ansible

This directory contains ansible for configuring GCP resources.
In particular, we provision a centralized scheduler for luigi so that we can parallelize tasks across multiple VMs.

```bash
ansible-inventory -i inventory.luigi.gcp.yml --graph
ansible all -i inventory.luigi.gcp.yml -m ping
ansible-playbook -i inventory.luigi.gcp.yml luigi.yml
```

## links

- https://docs.ansible.com/ansible/2.8/user_guide/playbooks_best_practices.html#content-organization
- https://docs.ansible.com/ansible/latest/collections/google/cloud/gcp_compute_inventory.html
- http://matthieure.me/2018/12/31/ansible_inventory_plugin.html
- https://www.bionconsulting.com/blog/gcp-iap-tunnelling-on-ansible-with-dynamic-inventory
