# Datalab 
- https://cloud.google.com/datalab/docs/quickstart

Datalab is just a compute engine instance with datalab image installed in it. The instance resource (disk space, memory) can be edited in the compute engine console.


Before creating datalab instance, run:
```
gcloud components install datalab
```

1. Create instances using:
    ```datalab create instance <instance-name>```
    
2. Connect to instance:
    ```datalab connect <instance-name>```
    
### Datalab API

Datalab has it's own API for cloud computing
- http://googledatalab.github.io/pydatalab/
