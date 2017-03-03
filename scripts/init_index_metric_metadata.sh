DEFAULT_WAIT_PERIOD="10s"
WAIT_PERIOD=${1:-$DEFAULT_WAIT_PERIOD}

echo "**** Creating index metric_metadata_current ****"
curl -XDELETE 'http://localhost:9200/metric_metadata_current'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XPUT 'http://localhost:9200/metric_metadata_current'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XPOST 'http://localhost:9200/metric_metadata_current/_close'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XPUT 'http://localhost:9200/metric_metadata_current/_settings' -d'{
    "index": {
        "analysis": {
            "analyzer": {
                "prefix-test-analyzer": {
                    "filter": "dotted",
                    "tokenizer": "prefix-test-tokenizer",
                    "type": "custom"
                }
            },
            "filter": {
                "dotted": {
                    "patterns": [
                        "([^.]+)"
                    ],
                    "type": "pattern_capture"
                }
            },
            "tokenizer": {
                "prefix-test-tokenizer": {
                    "delimiter": ".",
                    "type": "path_hierarchy"
                }
            }
        }
    }
}'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XPOST 'http://localhost:9200/metric_metadata_current/_open'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XPOST 'http://localhost:9200/metric_metadata_current/_mapping/metrics' -d '{
    "metrics": {
        "_routing": {
            "required": true
        },
        "properties": {
            "tenantId": {
                "type": "string",
                "index": "not_analyzed"
            },
            "unit": {
                "type": "string",
                "index": "not_analyzed"
            },
            "metric_name": {
                "index_analyzer": "prefix-test-analyzer",
                "search_analyzer": "keyword",
                "type": "string"
            }
        }
    }
}'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XGET 'http://localhost:9200/_cat/indices?v' | grep metadata
curl -XGET http://localhost:9200/_cluster/health?pretty

echo "!!!! Make sure both the cluster health and index health is green before proceeding further !!"
