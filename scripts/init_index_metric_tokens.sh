DEFAULT_WAIT_PERIOD="10s"
WAIT_PERIOD=${1:-$DEFAULT_WAIT_PERIOD}

echo "**** Creating index with parent child relationship ****"

curl -XDELETE 'http://localhost:9200/metric_tokens'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XPUT 'http://localhost:9200/metric_tokens'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XPOST 'http://localhost:9200/metric_tokens/_mapping/tokens' -d '{
    "tokens": {
        "_routing": {
            "required": true
        },
        "properties": {
            "tenantId": {
                "type": "string",
                "index": "not_analyzed",
                "doc_values": true
            },
            "token": {
                "type": "string",
                "index": "not_analyzed",
                "doc_values": true
            },
            "path": {
                "type": "string",
                "index": "not_analyzed",
                "doc_values": true
            },
            "isLeaf": {
                "type": "boolean",
                "index": "not_analyzed",
                "doc_values": true
            }
        }
    }
}'

curl -XGET 'http://localhost:9200/_cat/indices?v' | grep metric
curl -XGET http://localhost:9200/_cluster/health?pretty

echo "!!!! Make sure both the cluster health and index health is green before proceeding further !!"
