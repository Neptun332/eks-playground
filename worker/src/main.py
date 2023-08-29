import os

import boto3

from EndpointClientMock import EndpointClientMock
from Processor import Processor
from frame_sources.KVSFrameSource import KVSFrameSource

STREAM_NAME = os.environ['STREAM_NAME']
REGION = os.environ['REGION']

if __name__ == "__main__":
    session = boto3.Session(region_name=REGION)
    endpoint_client_mock = EndpointClientMock(request_time_in_seconds=3)
    processor = Processor(endpoint_client_mock)
    kvs_frame_source = KVSFrameSource(session=session, stream_name=STREAM_NAME, on_new_frame=processor.on_new_frame)
    kvs_frame_source.start_reading()
