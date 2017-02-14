from elasticsearch import Elasticsearch
from elasticsearch.helpers import ScanError, BulkIndexError
import elasticsearch.helpers as helpers
import sys


def no_transform(old_doc_id, new_index, new_index_type):
    """
    Transformation logic used to transform the source when called with
    no_transform and returns ES actions for bulk indexing.
    Here we dont transform the data in any way.
    """

    new_doc = {}
    (tenant_id, metric_name) = old_doc_id.split(':', 1)

    new_doc['tenantId'] = tenant_id
    new_doc['metric_name'] = metric_name

    action = {
        "_index": new_index,
        "_type": new_index_type,
        "_routing": tenant_id,
        "_id": old_doc_id,
        "_source": new_doc
    }

    return [action]


def parent_child(old_doc_id, new_index, new_index_type):
    """
    Transformation logic used to transform the source when called with
    parent_child and returns ES actions for bulk indexing.
    """

    new_doc = {}
    (tenant_id, metric_name) = old_doc_id.split(':', 1)

    actions = []
    if len(metric_name) > 0 and len(tenant_id) > 0:
        tokens = metric_name.split('.')

        level = 0
        path = ""
        for token in tokens:
            if level == 0:
                path = token
            else:
                path = path + "." + token

            action = {
                "_index": new_index,
                "_type": new_index_type,
                "_routing": tenant_id,
            }

            if level == len(tokens) - 1:
                action['_id'] = tenant_id + ":" + path + ":$"
                new_doc['is_leaf'] = True
            else:
                action['_id'] = tenant_id + ":" + path
                new_doc['is_leaf'] = False

            new_doc['token'] = token
            if level == 0:
                new_doc['parent'] = tenant_id + ":"
            else:
                (parent, token) = action['_id'].rsplit('.', 1)
                new_doc['parent'] = parent

            action["_source"] = new_doc
            actions.append(action)

            new_doc = {}
            level += 1
    else:
        print "Invalid document id {0} for tenant {1}".format(old_doc_id,
                                                              tenant_id)
        return []

    return actions


def extra_paths(old_doc_id, new_index, new_index_type):
    """
    Transformation logic used to transform the source when called with
    extra_paths and returns ES actions for bulk indexing.
    """

    new_doc = {}

    (tenant_id, metric_name) = old_doc_id.split(':', 1)
    if len(metric_name) > 0 and len(tenant_id) > 0:
        tokens = metric_name.split('.')

        level = 0
        paths = []
        path = ""
        for token in tokens:
            if level == 0:
                path = token
            else:
                path = path + "." + token

            if level == len(tokens) - 1:
                paths.append(str(level) + ":" + path + ":$")
            else:
                paths.append(str(level) + ":" + path)

            level += 1

        new_doc['tenantId'] = tenant_id
        new_doc['metric_name'] = metric_name
        new_doc['paths'] = paths
    else:
        print "Invalid document id %s for tenant %s" % (old_doc_id, tenant_id)
        return []

    action = {
        "_index": new_index,
        "_type": new_index_type,
        "_routing": tenant_id,
        "_id": old_doc_id,
        "_source": new_doc
    }

    return [action]


def extra_paths2(old_doc_id, new_index, new_index_type):
    """
    Transformation logic used to transform the source when called with
    extra_paths2 and returns ES actions for bulk indexing.
    """

    new_doc = {}

    (tenant_id, metric_name) = old_doc_id.split(':', 1)
    if len(metric_name) > 0 and len(tenant_id) > 0:
        tokens = metric_name.split('.')

        level = 0
        path = ""
        for token in tokens:
            if level == 0:
                path = token
            else:
                path = path + "." + token

            if level == len(tokens) - 1:
                new_doc["l" + str(level)] = path + ":$"
            else:
                new_doc["l" + str(level)] = path

            level += 1

        new_doc['tenantId'] = tenant_id
        new_doc['metric_name'] = metric_name

    else:
        print "Invalid document id {0} for tenant {1}".format(old_doc_id,
                                                              tenant_id)
        return []

    action = {
        "_index": new_index,
        "_type": new_index_type,
        "_routing": tenant_id,
        "_id": old_doc_id,
        "_source": new_doc
    }
    return [action]


class ESClient:
    def __init__(self, hosts, timeout):
        print "Connecting to ES cluster: " + str(hosts)
        self.es = Elasticsearch(hosts=hosts, timeout=timeout,
                                retry_on_timeout=True)

    def get_total_number_of_docs(self, index, index_type):
        request_body = {
            "aggs": {
                "tenantId": {
                    "terms": {
                        "field": "_routing",
                        "size": 0
                    }
                }
            }
        }
        return self.es.search(index=index, doc_type=index_type,
                              body=request_body)

    def reindex(self, tenantId, current_index, new_index, new_index_type,
                timeout, retrieve_quatity_by_shard, transform,
                bulk_thread_count, bulk_size):
        """
        Uses scan and scroll API to go thru the data from current_index and
        bulk indeing to reindex the data to new_index.
        """

        request_body = {
            "query": {
                "term": {
                    "tenantId": tenantId
                }
            },
            "fields": [],
            "size": retrieve_quatity_by_shard
        }

        # Keeps the scroll open for 'timeout' interval.
        scroll_result = self.es.search(index=current_index, doc_type="metrics",
                                       body=request_body,
                                       search_type="scan", scroll=timeout)

        scroll_id = scroll_result['_scroll_id']

        transform_methods = {
            'parent_child': parent_child,
            'extra_paths': extra_paths,
            'extra_paths2': extra_paths2,
            'no_transform': no_transform
        }
        transform_method = transform_methods[transform]

        if not transform_method:
            raise NotImplementedError("Method %s not implemented" % transform)

        actions = self._scroll(timeout, scroll_id,
                               transform_method,
                               new_index,
                               new_index_type)

        try:

            count = 0
            for success, info in \
                    helpers.parallel_bulk(self.es, actions=actions,
                                          thread_count=bulk_thread_count,
                                          chunk_size=bulk_size):
                if count % bulk_size == 0:
                    sys.stdout.write(' %d ..' % count)

                count += 1
                if not success:
                    print('Bulk insert failed', info)

            sys.stdout.write('\n')
        except BulkIndexError:
            print "Exception during bulk indexing"
            raise

    def _scroll(self, timeout, scroll_id, f, new_index, new_index_type):

        try:
            scroll_result = self.es.scroll(scroll_id, scroll=timeout)

            while len(scroll_result['hits']['hits']) > 0:
                for item in scroll_result['hits']['hits']:
                    for action in f(item['_id'], new_index, new_index_type):
                        yield action

                scroll_id = scroll_result['_scroll_id']
                scroll_result = self.es.scroll(scroll_id, scroll=timeout)
        except ScanError:
            print "Exception during scrolling"
            raise
