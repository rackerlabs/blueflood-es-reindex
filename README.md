
# Blueflood ES reindex

This project is created to re-index existing data in blueflood ES cluster into a 
new index. The idea is to experiment with couple of different mappings and see 
which ones performs better.


## Command

```bash
usage: reindex.py [-h] [--dryrun] --current-index CURRENT_INDEX
                  [--hosts HOSTS] [--scroll-timeout SCROLL_TIMEOUT]
                  [--size SIZE] [--new-index NEW_INDEX]
                  [--new-index-type NEW_INDEX_TYPE]
                  [--transform {parent_child,extra_paths,extra_paths2,no_transform}]
                  [--tenantIds TENANTIDS]
                  [--bulk-thread-count BULK_THREAD_COUNT]
                  [--bulk-size BULK_SIZE]

Reindex data from metric_metadata ES index to a new index.

optional arguments:
  -h, --help            show this help message and exit
  --dryrun              Display metric id's being reindexed
  --current-index CURRENT_INDEX
                        Current index that needs to be re-indexed
  --hosts HOSTS         ES hosts
  --scroll-timeout SCROLL_TIMEOUT
                        Scroll timeout
  --size SIZE           Number of documents to retrieve per shard
  --new-index NEW_INDEX
                        New index where the documents need to be re-indexed to
  --new-index-type NEW_INDEX_TYPE
                        New index type where the documents need to be re-
                        indexed to
  --transform {parent_child,extra_paths,extra_paths2,no_transform}
                        Transform current data using one of these methods
  --tenantIds TENANTIDS
                        TenantId's that need to be re-indexed
  --bulk-thread-count BULK_THREAD_COUNT
                        Number of bulk requests in parallel
  --bulk-size BULK_SIZE
                        Number of documents in one bulk request
```

The command when run prints some useful data to stdout. You may want to pipe that
into a file while running for future reference.



*More information about scroll timeout and size parametrs can be found here. [https://www.elastic.co/guide/en/elasticsearch/guide/1.x/scan-scroll.html](https://www.elastic.co/guide/en/elasticsearch/guide/1.x/scan-scroll.html)* 

# Steps to follow

1. Create the new index. The project comes with couple of commands. Run one of
   the below scripts.
    
    | new index choices    | create index scripts               |
    | ---------------------|:----------------------------------:|
    | extra_paths          | scripts/init_index_extra_paths.sh  |
    | extra_paths2         | scripts/init_index_extra_paths2.sh |
    | parent_child         | scripts/init_index_parent_child.sh |

    *Note: This scripts will wipe out the index if already exists.*

2. Once the indexes are created, make sure the cluster health and index health 
   are green
   
3. Before we start re-indexing run the below command which will help speedup bulk indexing
   
    ```bash   
       --disabling refresh. Documents will not be visible until you enable refresh. 
       curl -XPUT localhost:9200/<new index>/_settings -d '{
            "index" : {
                "refresh_interval" : "-1"
            } 
       }'
    ```
   
    ```bash
       --disable replicas
       curl -XPUT 'http://localhost:9200/<new index>/_settings' -d '{
            "number_of_replicas": 0
       }'
    ```
   
4. (Optional) Run the below command to check the counts before re-indexing.   

    ```bash
    python esreindex/reindex.py --hosts  <ip1>:9200,<ip2>:9200 --current-index metric_metadata_v2 --dryrun
    ```

5. Make sure to adjust values like timeout, size. Take a look at step six before 
   proceeding with this one. If you want to reindex all the documents present in 
   metric_metadata index run the below command.

    ```bash
    python esreindex/reindex.py --hosts <ip1>:9200,<ip2>:9200 --current-index metric_metadata  --scroll-timeout 10m --size 100 --new-index <new index name> --new-index-type <new index type> --transform <extra_paths|extra_paths2|parent_child>  &> result.out
    ```
   *<new index type> is "metrics" for extra_paths and "tokens" for <parent_child>*

6. If you want to re-index tenant by tenant, use the below command
    
    ```bash
    python reindex.py --hosts <ip1>:9200,<ip2>:9200 --current-index metric_metadata  --scroll-timeout 10m --size 100 --new-index <new index name> --new-index-type <new index type> --transform <extra_paths|extra_paths2|parent_child> --tenantIds <id1>,<id2>  &> result.out 
    ```

    *<new index type> is "metrics" for extra_paths and "tokens" for <parent_child>*

7. Once the re-index is completed, make sure the cluster health and index health 
   are green

    ```bash
    curl -XGET 'http://localhost:9200/_cat/indices?v' | grep metadata
    curl -XGET http://localhost:9200/_cluster/health?pretty
    ```   
   
8. After all re-indexing is complete, run the below commands to make the reindex 
   documents visible.

    ```bash
    --default value of refresh interval is 1s. If your cluster has a different value set that amount.
    curl -XPUT localhost:9200/<new index>/_settings -d '{
        "index" : {
            "refresh_interval" : "1s"
        } 
    }'
    ```

9. Get counts by tenantid in the new index and compare with the initial data.
 
    ```bash
    curl -XGET 'http://localhost:9200/<new index name>/_search?search_type=count&pretty' -d '{
        "aggs": {
              "tenantId": {
                  "terms": {
                      "field" : "_routing",
                      "size": 0
                  }
              }
        }
    }'
    ```

10. After all the documents become visible (by verifying counts from previous step),
    run the below command to turn on replication

    ```bash
    curl -XPUT 'http://localhost:9200/<new index>/_settings' -d '{
        "number_of_replicas": 2
    }'
    ```
 

# Useful links

[https://www.elastic.co/guide/en/elasticsearch/guide/1.x/scan-scroll.html](https://www.elastic.co/guide/en/elasticsearch/guide/1.x/scan-scroll.html)
[http://elasticsearch-py.readthedocs.io/en/master/helpers.html](http://elasticsearch-py.readthedocs.io/en/master/helpers.html)