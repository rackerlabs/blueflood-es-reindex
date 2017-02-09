DEFAULT_WAIT_PERIOD="10s"
WAIT_PERIOD=${1:-$DEFAULT_WAIT_PERIOD}

echo "**** Creating index with extra paths2 ****"
curl -XDELETE 'http://localhost:9200/metric_metadata_with_paths2'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XPUT 'http://localhost:9200/metric_metadata_with_paths2'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XPOST 'http://localhost:9200/metric_metadata_with_paths2/_close'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XPUT 'http://localhost:9200/metric_metadata_with_paths2/_settings' -d'{
    "index": {
        "store" : {
            "preload": ["nvd", "dvd", "tim", "doc", "dim"]
        },
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

curl -XPOST 'http://localhost:9200/metric_metadata_with_paths2/_open'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XPOST 'http://localhost:9200/metric_metadata_with_paths2/_mapping/metrics' -d '{
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
            },
            "l0": { "type": "string","index": "not_analyzed","doc_values": true },
            "l1": { "type": "string","index": "not_analyzed","doc_values": true },
            "l2": { "type": "string","index": "not_analyzed","doc_values": true },
            "l3": { "type": "string","index": "not_analyzed","doc_values": true },
            "l4": { "type": "string","index": "not_analyzed","doc_values": true },
            "l5": { "type": "string","index": "not_analyzed","doc_values": true },
            "l6": { "type": "string","index": "not_analyzed","doc_values": true },
            "l7": { "type": "string","index": "not_analyzed","doc_values": true },
            "l8": { "type": "string","index": "not_analyzed","doc_values": true },
            "l9": { "type": "string","index": "not_analyzed","doc_values": true },
            "l10": { "type": "string","index": "not_analyzed","doc_values": true },
            "l11": { "type": "string","index": "not_analyzed","doc_values": true },
            "l12": { "type": "string","index": "not_analyzed","doc_values": true },
            "l13": { "type": "string","index": "not_analyzed","doc_values": true },
            "l14": { "type": "string","index": "not_analyzed","doc_values": true },
            "l15": { "type": "string","index": "not_analyzed","doc_values": true },
            "l16": { "type": "string","index": "not_analyzed","doc_values": true },
            "l17": { "type": "string","index": "not_analyzed","doc_values": true },
            "l18": { "type": "string","index": "not_analyzed","doc_values": true },
            "l19": { "type": "string","index": "not_analyzed","doc_values": true },
            "l20": { "type": "string","index": "not_analyzed","doc_values": true },
            "l21": { "type": "string","index": "not_analyzed","doc_values": true },
            "l22": { "type": "string","index": "not_analyzed","doc_values": true },
            "l23": { "type": "string","index": "not_analyzed","doc_values": true },
            "l24": { "type": "string","index": "not_analyzed","doc_values": true },
            "l25": { "type": "string","index": "not_analyzed","doc_values": true }
        }
    }
}'

echo "Waiting ${WAIT_PERIOD}..."
sleep ${WAIT_PERIOD}

curl -XGET 'http://localhost:9200/_cat/indices?v' | grep metadata
curl -XGET http://localhost:9200/_cluster/health?pretty

echo "!!!! Make sure both the cluster health and index health is green before proceeding further !!"
