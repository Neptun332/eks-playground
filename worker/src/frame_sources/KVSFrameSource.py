import logging
import time
from typing import Callable

from VideoFrame import VideoFrame
from frame_sources.amazon_kinesis_video_consumer_library.kinesis_video_fragment_processor import KvsFragementProcessor
from frame_sources.amazon_kinesis_video_consumer_library.kinesis_video_streams_parser import KvsConsumerLibrary

log = logging.getLogger()


class KVSFrameSource:

    def __init__(self, session, stream_name: str, on_new_frame: Callable[[VideoFrame], None]):
        log.info('Initializing Amazon Kinesis Video client....')
        self.session = session
        self.stream_name = stream_name
        self.on_new_frame = on_new_frame
        self.kvs_client = self.session.client("kinesisvideo")
        self.kvs_fragment_processor = KvsFragementProcessor()
        self.last_good_fragment_tags = None

    def start_reading(self):
        log.info(f'Getting KVS GetMedia Endpoint for stream: {self.stream_name} ........')
        get_media_endpoint = self._get_data_endpoint(self.stream_name, 'GET_MEDIA')

        log.info(f'Initializing KVS Media client for stream: {self.stream_name}........')
        kvs_media_client = self.session.client('kinesis-video-media', endpoint_url=get_media_endpoint)

        log.info(f'Requesting KVS GetMedia Response for stream: {self.stream_name}........')
        get_media_response = kvs_media_client.get_media(
            StreamName=self.stream_name,
            StartSelector={
                'StartSelectorType': 'NOW'
            }
        )
        log.info(f'Starting KvsConsumerLibrary for stream: {self.stream_name}........')
        my_stream01_consumer = KvsConsumerLibrary(
            self.stream_name,
            get_media_response,
            self.on_fragment_arrived,
        )

        my_stream01_consumer.run()

    ####################################################
    # KVS Consumer Library call-backs

    def on_fragment_arrived(self, stream_name, fragment_bytes, fragment_dom, fragment_receive_duration):
        '''
        This is the callback for the KvsConsumerLibrary to send MKV fragments as they are received from a stream being processed.
        The KvsConsumerLibrary returns the received fragment as raw bytes and a DOM like structure containing the fragments meta data.

        With these parameters you can do a variety of post-processing including saving the fragment as a standalone MKV file
        to local disk, request individual frames as a numpy.ndarray for data science applications or as JPEG/PNG files to save to disk
        or pass to computer vison solutions. Finally, you can also use the Fragment DOM to access Meta-Data such as the MKV tags as well
        as track ID and codec information.

        In the below example we provide a demonstration of all of these described functions.

        ### Parameters:

            **stream_name**: str
                Name of the stream as set when the KvsConsumerLibrary thread triggering this callback was initiated.
                Use this to identify a fragment when multiple streams are read from different instances of KvsConsumerLibrary to this callback.

            **fragment_bytes**: bytearray
                A ByteArray with raw bytes from exactly one fragment. Can be save or processed to access individual frames

            **fragment_dom**: mkv_fragment_doc: ebmlite.core.Document <ebmlite.core.MatroskaDocument>
                A DOM like structure of the parsed fragment providing searchable list of EBML elements and MetaData in the Fragment

            **fragment_receive_duration**: float
                The time in seconds that the fragment took for the streaming data to be received and processed.

        '''

        try:
            log.info(f'Fragment Received on Stream: {stream_name}')
            log.info(f'Fragment Receive and Processing Duration: {fragment_receive_duration} Secs')

            self.last_good_fragment_tags = self.kvs_fragment_processor.get_fragment_tags(fragment_dom)

            ##### Log Time Deltas:  local time Vs fragment SERVER and PRODUCER Timestamp:
            time_now = time.time()
            kvs_ms_behind_live = float(self.last_good_fragment_tags['AWS_KINESISVIDEO_MILLIS_BEHIND_NOW'])
            producer_timestamp = float(self.last_good_fragment_tags['AWS_KINESISVIDEO_PRODUCER_TIMESTAMP'])
            server_timestamp = float(self.last_good_fragment_tags['AWS_KINESISVIDEO_SERVER_TIMESTAMP'])

            log.info('')
            log.info('####### Timestamps and Delta: ')
            log.info(f'KVS Reported Time Behind Live {kvs_ms_behind_live} mS')
            log.info(
                f'Local Time Diff to Fragment Producer Timestamp: {round(((time_now - producer_timestamp) * 1000), 3)} mS')
            log.info(
                f'Local Time Diff to Fragment Server Timestamp: {round(((time_now - server_timestamp) * 1000), 3)} mS')

            ndarray_frames = self.kvs_fragment_processor.get_frames_as_ndarray(fragment_bytes, one_in_frames_ratio=1)
            for i in range(len(ndarray_frames)):
                ndarray_frame = ndarray_frames[i]
                self.on_new_frame(ndarray_frame)
                log.info(f'Frame-{i} Shape: {ndarray_frame.shape}')

        except Exception as err:
            log.error(f'on_fragment_arrived Error: {err}')

    ####################################################
    # KVS Helpers
    def _get_data_endpoint(self, stream_name, api_name):
        '''
        Convenience method to get the KVS client endpoint for specific API calls.
        '''
        response = self.kvs_client.get_data_endpoint(
            StreamName=stream_name,
            APIName=api_name
        )
        return response['DataEndpoint']
