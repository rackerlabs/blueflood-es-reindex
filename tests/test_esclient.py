import esreindex.esclient as es


def test_paths_generated_1():
    tenant_id = '1234'
    metric_name = 'a.b.c.d'

    old_id = tenant_id + ":" + metric_name
    new_index = 'new_index'
    new_type = 'type'
    actions = es.extra_paths(old_id, new_index, new_type)[0]
    # print actions

    assert actions['_id'] == old_id
    assert actions['_index'] == new_index
    assert actions['_type'] == new_type
    assert actions['_routing'] == tenant_id

    assert actions['_source']['tenantId'] == tenant_id
    assert actions['_source']['metric_name'] == metric_name
    assert len(actions['_source']['paths']) == 4

    assert actions['_source']['paths'][0] == '0:a'
    assert actions['_source']['paths'][1] == '1:a.b'
    assert actions['_source']['paths'][2] == '2:a.b.c'
    assert actions['_source']['paths'][3] == '3:a.b.c.d:$'


def test_paths_generated_2():
    actions = es.extra_paths('1234:a', 'new_index', 'new_type')[0]
    assert len(actions['_source']['paths']) == 1
    assert actions['_source']['paths'][0] == '0:a:$'


def test_paths_generated_3():
    actions = es.extra_paths('1234:', 'new_index', 'new_type')
    assert len(actions) == 0


def test_path2_generated_1():
    tenant_id = '1234'
    metric_name = 'a.b.c.d'

    old_id = tenant_id + ":" + metric_name
    new_index = 'new_index'
    new_type = 'type'
    actions = es.extra_paths2(old_id, new_index, new_type)[0]
    # print actions

    assert actions['_id'] == old_id
    assert actions['_index'] == new_index
    assert actions['_type'] == new_type
    assert actions['_routing'] == tenant_id

    assert actions['_source']['tenantId'] == tenant_id
    assert actions['_source']['metric_name'] == metric_name

    assert actions['_source']['l0'] == 'a'
    assert actions['_source']['l1'] == 'a.b'
    assert actions['_source']['l2'] == 'a.b.c'
    assert actions['_source']['l3'] == 'a.b.c.d:$'


def test_paths2_generated_2():
    actions = es.extra_paths2('1234:a', 'new_index', 'new_type')[0]
    assert actions['_source']['l0'] == 'a:$'


def test_paths2_generated_3():
    actions = es.extra_paths2('1234:', 'new_index', 'new_type')
    assert len(actions) == 0


def test_parent_child_generated_1():
    tenant_id = '1234'
    metric_name = 'a.b.c.d'

    old_id = tenant_id + ":" + metric_name
    new_index = 'new_index'
    new_type = 'type'
    actions = es.metric_tokens(old_id, new_index, new_type)
    print actions

    assert actions[0]['_index'] == new_index
    assert actions[0]['_type'] == new_type
    assert actions[0]['_routing'] == tenant_id

    assert actions[0]['_id'] == tenant_id + ":" + "a"
    assert actions[0]['_source']['token'] == "a"
    assert not actions[0]['_source']['isLeaf']
    assert actions[0]['_source']['parent'] == ""

    assert actions[1]['_id'] == tenant_id + ":" + "a.b"
    assert actions[1]['_source']['token'] == "b"
    assert not actions[1]['_source']['isLeaf']
    assert actions[1]['_source']['parent'] == "a"

    assert actions[2]['_id'] == tenant_id + ":" + "a.b.c"
    assert actions[2]['_source']['token'] == "c"
    assert not actions[2]['_source']['isLeaf']
    assert actions[2]['_source']['parent'] == "a.b"

    assert actions[3]['_id'] == tenant_id + ":" + "a.b.c.d:$"
    assert actions[3]['_source']['token'] == "d"
    assert actions[3]['_source']['isLeaf']
    assert actions[3]['_source']['parent'] == "a.b.c"


def test_parent_child_generated_2():
    actions = es.metric_tokens('1234:a', 'new_index', 'new_type')
    assert actions[0]['_source']['token'] == 'a'
    assert actions[0]['_source']['isLeaf']
    assert actions[0]['_source']['parent'] == ''


def test_parent_child_generated_3():
    actions = es.metric_tokens('1234:', 'new_index', 'new_type')
    assert len(actions) == 0
