# Google App Engine

This example code is executed in local computer using app engine standard environment (python 2.7)

## Set up in local
1. Install google-sdk
2. Create a folder `lib` and install all the extra-required libraries by:
   ```
   pip install -t lib -r requirements.txt
   ```
3. Determine path to dev_appserver.py (Located inside google-cloud-sdk/bin/dev_appserver.py)
4. cd into the application folder and run:
   ```
   python C://.../dev_appserver.py app.yaml
   ```

## Folder structure
```
+- lib
+   - library1 
+   - library2
+   - ...
+- app.yaml
+- cron.yaml
+- queue.yaml
+- appengine_config.py
+- main.py
+- requirements.txt
```

### App Engine local dev UI
![local ui](https://github.com/neurotichl/GCP/raw/master/img/local_gae1.PNG)

### Insert data into datastore
![call API](https://github.com/neurotichl/GCP/raw/master/img/local_gae2.PNG)
- Datatstore UI
![datastore](https://github.com/neurotichl/GCP/raw/master/img/local_gae_datastore.PNG)

Note: Inserting into datastore in standard env must use the library [ndb](https://cloud.google.com/appengine/docs/standard/python/ndb/), google.cloud.datastore is not accepted and will raise [error](https://github.com/GoogleCloudPlatform/python-docs-samples/issues/1235) 


### Cron job scheduling
- target: service name defined in `app.yaml`
![cron](https://github.com/neurotichl/GCP/raw/master/img/local_gae_cron.PNG)

### Task queue
- Task queue is currently not supported in app engine flex.
![queue](https://github.com/neurotichl/GCP/raw/master/img/local_gae_queue.PNG)
![queue2](https://github.com/neurotichl/GCP/raw/master/img/local_gae_queue2.PNG)

### Memcache
- Temporary store value in cache in specified timeout.
![memcache](https://github.com/neurotichl/GCP/raw/master/img/memcache.gif)
