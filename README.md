
## Setting up Hazelcast on local environment
```bash
cd adzd-project 

docker-compose up --build
```
To remove: 
```bash
docker-compose down
```

## Setting up AWS environment
1. Create EC2 instance on AWS with default settings (Amazon Linux)
2. Assign security group to EC2 allowing SSH connections and 8080 (for Hazelcast Management Center)
3. Login to EC2 Instance via SSH
```bash
ssh -v -i "labsuser.pem" ec2-user@<public-ip>
```
4. Install Hazelcast on instance
```bash
wget https://repository.hazelcast.com/rpm/stable/hazelcast-rpm-stable.repo -O hazelcast-rpm-stable.repo
sudo mv hazelcast-rpm-stable.repo /etc/yum.repos.d/
sudo yum install hazelcast
```

5. Install and run Hazelcast Management Center on instance
```bash
sudo amazon-linux-extras enable corretto8
sudo yum install -y java-1.8.0-amazon-corretto
wget https://repository.hazelcast.com/download/management-center/hazelcast-management-center-5.6.0.tar.gz

tar -xvf hazelcast-management-center-5.6.0.tar.gz

java -jar hazelcast-management-center-5.6.0.jar
```

6. Run Hazelcast cluster
```bash
hz start
```

## Configuration
Hazelcast configuration file is stored in: /usr/lib/hazelcast/config/hazelcast.xml (by default user don't have rights to change it)

#### Options:
- change cluster-name (dev by default)
- auto-detection - determines if nodes are connecting automatically
- network - allows to set static IP address for node
- tcp-ip>members - static list of connections between nodes