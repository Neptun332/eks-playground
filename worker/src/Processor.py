import cv2

from EndpointClientMock import EndpointClientMock
from VideoFrame import VideoFrame


class Processor:

    def __init__(self, endpoint_client: EndpointClientMock):
        self.endpoint_client = endpoint_client

    def on_new_frame(self, video_frame: VideoFrame) -> None:
        cv2.imshow('Frame', video_frame)
        cv2.waitKey(25)

        results = self.endpoint_client.get_results(video_frame)

        pass
        # TODO save detections in dynamo
