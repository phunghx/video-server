import json
from io import BytesIO

import pytest
from flask import url_for


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_retrieve_project_success(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)
        # retrieve project
        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])
        resp = client.get(url)
        resp_data = json.loads(resp.data)

        assert resp.status == '200 OK'
        assert '_id' in resp_data
        assert 'filename' in resp_data
        assert 'storage_id' in resp_data
        assert 'create_time' in resp_data
        assert resp_data['mime_type'] == 'video/mp4'
        assert resp_data['request_address'] == '127.0.0.1'
        assert resp_data['original_filename'] == filename
        assert resp_data['version'] == 1
        assert resp_data['parent'] == None
        assert resp_data['processing'] == {'video': False, 'thumbnail_preview': False, 'thumbnails_timeline': False}
        assert resp_data['thumbnails'] == {'timeline': [], 'preview': None}
        assert resp_data['url'] == f'http://localhost:5050/projects/{resp_data["_id"]}/raw/video'
        assert resp_data['metadata']['codec_name'] == 'h264'
        assert resp_data['metadata']['codec_long_name'] == 'H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10'
        assert resp_data['metadata']['width'] == 1280
        assert resp_data['metadata']['height'] == 720
        assert resp_data['metadata']['r_frame_rate'] == '25/1'
        assert resp_data['metadata']['bit_rate'] == 1045818
        assert resp_data['metadata']['nb_frames'] == 375
        assert resp_data['metadata']['duration'] == 15.0
        assert resp_data['metadata']['format_name'] == 'mov,mp4,m4a,3gp,3g2,mj2'
        assert 'size' in resp_data['metadata']


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_retrieve_project_404(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)

        # retrieve project
        url = url_for('projects.retrieve_edit_destroy_project', project_id="definitely_not_object_id")
        resp = client.get(url)
        assert resp.status == '404 NOT FOUND'

        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])
        client.delete(url)
        resp = client.get(url)
        assert resp.status == '404 NOT FOUND'


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_destroy_project_success(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)

        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])
        resp = client.delete(url)
        assert resp.status == '204 NO CONTENT'


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_destroy_project_fails(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)

        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])
        client.delete(url)
        resp = client.delete(url)
        assert resp.status == '404 NOT FOUND'


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_edit_project_202_response(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)

        # set processing to true in db
        _id = list(test_app.mongo.db.projects.find().limit(1))[0]['_id']
        test_app.mongo.db.projects.find_one_and_update(
            {'_id': _id},
            {'$set': {'processing.video': True}}
        )

        # edit request
        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])
        start = 2.0
        end = 6.0
        resp = client.put(
            url,
            data=json.dumps({
                "trim": {
                    "start": start,
                    "end": end
                }
            }),
            content_type='application/json'
        )
        assert resp.status == '202 ACCEPTED'


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_edit_project_trim_success(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)

        # edit request
        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])
        start = 2.0
        end = 6.0
        resp = client.put(
            url,
            data=json.dumps({
                "trim": {
                    "start": start,
                    "end": end
                }
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '200 OK'
        assert resp_data == {'processing': True}
        # get details
        resp = client.get(url)
        resp_data = json.loads(resp.data)
        assert resp_data['processing']['video'] == False
        assert resp_data['metadata']['duration'] == end - start


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_edit_project_trim_fail(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)
        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])

        # edit request
        resp = client.put(
            url,
            data=json.dumps({
                "trim": {
                    "start": 6.0,
                    "end": 2.0
                }
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {'message': {'trim': [{'start': ["must be less than 'end' value"]}]}}

        # edit request
        resp = client.put(
            url,
            data=json.dumps({
                "trim": {
                    "start": 0,
                    "end": 1
                }
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {'message': {'trim': [{'start': ['trimmed video must be at least 2 seconds']}]}}

        # edit request
        resp = client.put(
            url,
            data=json.dumps({
                "trim": {
                    "start": 10,
                    "end": 20
                }
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {'message': {'trim': [{'end': ["outside of initial video's length"]}]}}

        # edit request
        resp = client.put(
            url,
            data=json.dumps({
                "trim": {
                    "start": 0,
                    "end": 15
                }
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {'message': {'trim': [{'end': ['trim is duplicating an entire video']}]}}


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_edit_project_rotate_success(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)

        # edit request
        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])
        resp = client.put(
            url,
            data=json.dumps({
                "rotate": 90
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '200 OK'
        assert resp_data == {'processing': True}
        # get details
        resp = client.get(url)
        resp_data = json.loads(resp.data)
        assert resp_data['metadata']['width'] == 720
        assert resp_data['metadata']['height'] == 1280


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_edit_project_rotate_fail(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)

        # edit request
        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])
        resp = client.put(
            url,
            data=json.dumps({
                "rotate": 70
            }),
            content_type='application/json'
        )
        assert resp.status == '400 BAD REQUEST'


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_edit_project_crop_success(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)

        # edit request
        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])
        resp = client.put(
            url,
            data=json.dumps({
                "crop": {
                    "x": 0,
                    "y": 0,
                    "width": 640,
                    "height": 480
                }
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '200 OK'
        assert resp_data == {'processing': True}
        # get details
        resp = client.get(url)
        resp_data = json.loads(resp.data)
        assert resp_data['metadata']['width'] == 640
        assert resp_data['metadata']['height'] == 480


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_edit_project_crop_fail(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)
        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])

        # edit request
        resp = client.put(
            url,
            data=json.dumps({
                "crop": {
                    "x": 2000,
                    "y": 0,
                    "width": 640,
                    "height": 480
                }
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {'message': {'crop': [{'x': ['less than minimum allowed crop width']}]}}

        # edit request
        resp = client.put(
            url,
            data=json.dumps({
                "crop": {
                    "x": 0,
                    "y": 1000,
                    "width": 640,
                    "height": 480
                }
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {'message': {'crop': [{'y': ['less than minimum allowed crop height']}]}}

        # edit request
        resp = client.put(
            url,
            data=json.dumps({
                "crop": {
                    "x": 300,
                    "y": 0,
                    "width": 1000,
                    "height": 480
                }
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {'message': {'crop': [{'width': ["crop's frame is outside a video's frame"]}]}}

        # edit request
        resp = client.put(
            url,
            data=json.dumps({
                "crop": {
                    "x": 0,
                    "y": 200,
                    "width": 640,
                    "height": 600
                }
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {'message': {'crop': [{'height': ["crop's frame is outside a video's frame"]}]}}


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_edit_project_scale_success(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)

        # edit request
        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])
        resp = client.put(
            url,
            data=json.dumps({
                "scale": 640
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '200 OK'
        assert resp_data == {'processing': True}
        # get details
        resp = client.get(url)
        resp_data = json.loads(resp.data)
        assert resp_data['metadata']['width'] == 640
        assert resp_data['metadata']['height'] == 360


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_edit_project_scale_fail(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)
        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])

        # edit request
        resp = client.put(
            url,
            data=json.dumps({
                "scale": 0
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {'message': {'scale': [f'min value is {test_app.config.get("MIN_VIDEO_WIDTH")}']}}

        # edit request
        resp = client.put(
            url,
            data=json.dumps({
                "scale": 5000
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {'message': {'scale': [f'max value is {test_app.config.get("MAX_VIDEO_WIDTH")}']}}

        # edit request
        resp = client.put(
            url,
            data=json.dumps({
                "scale": 1280
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {
            'message': {'trim': [{'scale': ['video or crop option already has exactly the same width']}]}}

        # edit request
        resp = client.put(
            url,
            data=json.dumps({
                "scale": 1440
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {'message': {
            'trim': [{'scale': ['interpolation is permitted only for videos which have width less than 1280px']}]}
        }

        # edit request
        test_app.config['ALLOW_INTERPOLATION'] = False
        resp = client.put(
            url,
            data=json.dumps({
                "scale": 1440
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '400 BAD REQUEST'
        assert resp_data == {'message': {
            'trim': [{'scale': ['interpolation of pixels is not allowed']}]}
        }


@pytest.mark.parametrize('filestreams', [('sample_0.mp4',)], indirect=True)
def test_edit_project_scale_and_crop_success(test_app, client, filestreams):
    mp4_stream = filestreams[0]
    filename = 'sample_0.mp4'

    with test_app.test_request_context():
        # create a project
        url = url_for('projects.list_upload_project')
        resp = client.post(
            url,
            data={
                'file': (BytesIO(mp4_stream), filename)
            },
            content_type='multipart/form-data'
        )
        resp_data = json.loads(resp.data)

        # edit request
        url = url_for('projects.retrieve_edit_destroy_project', project_id=resp_data['_id'])
        resp = client.put(
            url,
            data=json.dumps({
                "scale": 640,
                "crop": {
                    "x": 0,
                    "y": 0,
                    "width": 400,
                    "height": 400
                }
            }),
            content_type='application/json'
        )
        resp_data = json.loads(resp.data)
        assert resp.status == '200 OK'
        assert resp_data == {'processing': True}
        # get details
        resp = client.get(url)
        resp_data = json.loads(resp.data)
        assert resp_data['metadata']['width'] == 640
        assert resp_data['metadata']['height'] == 640