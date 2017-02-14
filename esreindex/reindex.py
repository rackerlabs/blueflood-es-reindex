import sys
import argparse
import datetime
import esclient as es

DEFAULT_ES_HOSTS = "localhost:9200"
DEFAULT_SCROLL_TIMEOUT = "1m"
DEFAULT_SIZE_PER_SHARD = 100
DEFAULT_CURRENT_INDEX = 'metric_metadata'
DEFAULT_THREAD_COUNT = 20
DEFAULT_BULK_SIZE = 500

TRANSFORMATION_CHOICES = ['parent_child', 'extra_paths', 'extra_paths2',
                          'no_transform']


def parse_args(args):
    parser = argparse.ArgumentParser(
        description='Reindex data from metric_metadata ES index to a new index.')

    parser.add_argument('--dryrun', action='store_true',
                        help="Display metric id's being reindexed")

    parser.add_argument('--current-index', required=True,
                        help="Current index that needs to be re-indexed")
    parser.add_argument('--hosts', default=DEFAULT_ES_HOSTS, help="ES hosts")
    parser.add_argument('--scroll-timeout', default=DEFAULT_SCROLL_TIMEOUT,
                        help="Scroll timeout")
    parser.add_argument('--size', default=DEFAULT_SIZE_PER_SHARD, type=int,
                        help="Number of documents to retrieve per shard")

    parser.add_argument('--new-index',
                        help="New index where the documents need to be re-indexed to")
    parser.add_argument('--new-index-type',
                        help="New index type where the documents need to be re-indexed to")
    parser.add_argument('--transform', choices=TRANSFORMATION_CHOICES,
                        default='no_transform',
                        help="Transform current data using one of these methods")
    parser.add_argument('--tenantIds', type=str,
                        help="TenantId's that need to be re-indexed")
    parser.add_argument('--bulk-thread-count', default=DEFAULT_THREAD_COUNT,
                        type=int, help="Number of bulk requests in parallel")
    parser.add_argument('--bulk-size', default=DEFAULT_BULK_SIZE, type=int,
                        help="Number of documents in one bulk request")

    return parser.parse_args(args)


def count_index(es_client, index_name, index_type, tenant_ids):
    """
    Displays counts by tenant id's in the given index.
    """
    count_response = es_client.get_total_number_of_docs(index_name, index_type)

    if int(count_response['_shards']['failed']) > 0:
        print "Count query to index {} failed".format(index_name)

    tenant_id_infos = []
    for bucket in count_response['aggregations']['tenantId']['buckets']:
        if len(tenant_ids) > 0:
            if bucket['key'] in tenant_ids:
                tenant_id_infos.append((bucket['key'], bucket['doc_count']))
        else:
            tenant_id_infos.append((bucket['key'], bucket['doc_count']))

    print "\n{0} Total Number of documents is {1}".format(
        index_name, count_response['hits']['total'])

    print "\n[{}] Doc counts by tenant Id...\n".format(index_name)
    for tenant_id_info in tenant_id_infos:
        print "{:20} : {:20}".format(tenant_id_info[0], tenant_id_info[1])

    return tenant_id_infos


def main():
    config = parse_args(sys.argv[1:])
    print config

    es_client = es.ESClient(hosts=config.hosts.split(","), timeout=30)

    print "\nVerifying counts..."

    tenant_ids = []
    if config.tenantIds:
        tenant_ids = config.tenantIds.split(',')

    tenant_id_infos = count_index(es_client, config.current_index, "metrics",
                                  tenant_ids)

    if not config.dryrun:
        print "\nReindexing..."
        for tenantId in tenant_id_infos:
            print "\n***** Re-indexing tenantId: {0} started at: {1}".format(
                tenantId[0], datetime.datetime.now())
            es_client.reindex(tenantId[0], config.current_index,
                              config.new_index,
                              config.new_index_type, config.scroll_timeout,
                              config.size, config.transform,
                              config.bulk_thread_count,
                              config.bulk_size)
            print "***** Re-indexing tenantId: {0} ended at  : {1}".format(
                tenantId[0], datetime.datetime.now())

            # count_index(es_client, config.new_index, config.new_index_type, tenant_ids)


if __name__ == "__main__":
    main()
