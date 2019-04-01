import pandas as pd
from sklearn.utils.linear_assignment_ import linear_assignment
from numba import jit
import numpy as np


@jit
def iou(bb_test, bb_gt):
    """
    Computes IUO between two bboxes in the form [x1,y1,x2,y2]
    """
    xx1 = np.maximum(bb_test[0], bb_gt[0])
    yy1 = np.maximum(bb_test[1], bb_gt[1])
    xx2 = np.minimum(bb_test[2], bb_gt[2])
    yy2 = np.minimum(bb_test[3], bb_gt[3])
    w = np.maximum(0., xx2 - xx1)
    h = np.maximum(0., yy2 - yy1)
    wh = w * h
    o = wh / ((bb_test[2] - bb_test[0]) * (bb_test[3] - bb_test[1])
              + (bb_gt[2] - bb_gt[0]) * (bb_gt[3] - bb_gt[1]) - wh)
    return (o)


def associate_detections_to_trackers(detections, trackers, iou_threshold=0.3):
    """
    Assigns detections to tracked object (both represented as bounding boxes)

    Returns 3 lists of matches, unmatched_detections and unmatched_trackers
    """
    if (len(trackers) == 0):
        return np.empty((0, 2), dtype=int), np.arange(len(detections)), np.empty((0, 5), dtype=int)
    iou_matrix = np.zeros((len(detections), len(trackers)), dtype=np.float32)

    for d, det in enumerate(detections):
        for t, trk in enumerate(trackers):
            # print('det'+str(det))
            # print('trk'+str(trk))
            # print('t'+str(t))
            # print('d'+str(d))
            iou_matrix[d, t] = iou(det, trk)
    matched_indices = linear_assignment(-iou_matrix)

    # filter out matched with low IOU
    matches = []
    for m in matched_indices:
        if (iou_matrix[m[0], m[1]] > iou_threshold):
            matches.append(m.reshape(1, 2))
    if (len(matches) == 0):
        matches = np.empty((0, 2), dtype=int)
    else:
        matches = np.concatenate(matches, axis=0)

    return matches


class Objects(object):

    def __init__(self, start_position, end_position, object_name, start_frame_number, end_frame_number, object_id):
        self.end_position = end_position
        self.start_position = start_position
        self.id = object_id
        self.name = object_name
        self.start_frame = start_frame_number
        self.end_frame = end_frame_number
        self.duration = self.end_frame - self.start_frame

        # 0: unknown 1:stay 2:ingress 3:outgress 4:ingress and outgress
        self.state = 0

    def get_state(self, duration_of_video, threshold=30):

        if self.start_frame <= threshold:
            if self.end_frame >= duration_of_video - threshold:
                self.state = 1
                return
            else:
                self.state = 3
                return

        if self.end_frame >= duration_of_video - threshold:
            self.state = 2
            return

        self.state = 4
        return

    def to_dataframe(self, length_of_video=795, threshold_of_frame=30):

        # vtest.avi 795      GP050503.MP4  21600

        self.get_state(length_of_video, threshold_of_frame)

        new_frame = pd.DataFrame()
        new_frame['object_id'] = [self.id]
        new_frame['object_name'] = [self.name]
        new_frame['start_frame'] = self.start_frame
        new_frame['end_frame'] = self.end_frame
        new_frame['duration'] = self.end_frame - self.start_frame
        new_frame['start_x1'] = self.start_position[0]
        new_frame['start_y1'] = self.start_position[1]
        new_frame['start_x2'] = self.start_position[2]
        new_frame['start_y2'] = self.start_position[3]
        new_frame['end_x1'] = self.end_position[0]
        new_frame['end_y1'] = self.end_position[1]
        new_frame['end_x2'] = self.end_position[2]
        new_frame['end_y2'] = self.end_position[3]
        new_frame['state'] = self.state

        return new_frame

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_start_frame(self):
        return self.start_frame

    def get_end_frame(self):
        return self.end_frame

    def get_duration(self):
        return self.duration

    def get_start_position(self):
        return self.start_position

    def get_end_position(self):
        return self.end_position

    def update(self, new_position, new_frame_number):
        self.position = new_position
        self.end_frame = new_frame_number
        self.duration = self.end_frame - self.start_frame

    def update_from_tracker(self, tracker):
        if tracker.get_end_frame() > self.end_frame:
            self.end_frame = tracker.get_end_frame()
            self.duration = self.end_frame - self.start_frame

        self.end_position = tracker.get_end_position()


class Filter_objects(object):

    def __init__(self):
        self.objects = []
        self.objects_end_position = []
        self.count = 0
        self.trackers = []

    def add_objects(self, tracker):
        new_object = Objects(tracker.get_start_position(), tracker.get_end_position(), tracker.get_name(),
                             tracker.get_start_frame(), tracker.get_end_frame(), tracker.get_id())
        self.objects.append(new_object)
        self.objects_end_position.append(tracker.get_end_position())

    def add_trackers(self, tracker):
        self.trackers.append(tracker)

    # return true if there is one. and update it.
    def update(self, tracker, duration_threshold):

        if len(self.objects) == 0:
            self.add_objects(tracker)
            return tracker.get_id()

        matched = associate_detections_to_trackers(self.objects_end_position, [tracker.get_start_position()],
                                                   iou_threshold=0.3)
        update_flag = 0
        if len(matched) != 0:
            for m in matched:
                # TODO assign all tracker's features to objects. Can't be '='.
                if tracker.get_name() == self.objects[m[0]].get_name() and abs(
                        tracker.get_start_frame() - self.objects[m[0]].get_end_frame()) < duration_threshold:
                    print('update')
                    update_flag = 1
                    self.objects[m[0]].update_from_tracker(tracker)
                    self.objects_end_position[m[0]] = tracker.get_end_position()
                    return self.objects[m[0]].get_id()

            if update_flag == 0:
                self.add_objects(tracker)
                return tracker.get_id()
        else:
            self.add_objects(tracker)
            return tracker.get_id()

    def print_count(self, threshold=75):
        count = 0
        for i in self.objects:
            if i.get_duration() > threshold:
                count += 1
        print('There are ' + str(count) + ' objects in the video. ')

    def generate_csv(self, file_path, length_of_video):
        threshold_of_frame = length_of_video / 100
        total_frame = pd.concat([i.to_dataframe(length_of_video, threshold_of_frame) for i in self.objects])
        total_frame.to_csv(file_path)

    def generate_test_csv(self, file_path):
        total_frame = pd.concat([i.to_dataframe() for i in self.trackers])
        total_frame.to_csv(file_path)


class Tracker(object):

    def __init__(self, id, name, start_frame, end_frame, start_position, end_position):
        self.id = id
        self.name = name
        self.start_frame = start_frame
        self.end_frame = end_frame
        self.start_position = start_position
        self.end_position = end_position
        self.object_id = id

    def get_id(self):
        return self.id

    def set_object_id(self, new_id):
        self.object_id = new_id

    def get_name(self):
        return self.name

    def get_start_frame(self):
        return self.start_frame

    def get_end_frame(self):
        return self.end_frame

    def get_start_position(self):
        return start_position

    def get_end_position(self):
        return end_position

    def to_dataframe(self):
        # vtest.avi 795      GP050503.MP4  21600

        new_frame = pd.DataFrame()
        new_frame['object_id'] = [self.id]
        new_frame['unique_id'] = [self.object_id]
        new_frame['object_name'] = [self.name]
        new_frame['start_frame'] = self.start_frame
        new_frame['end_frame'] = self.end_frame
        new_frame['duration'] = self.end_frame - self.start_frame
        new_frame['start_x1'] = self.start_position[0]
        new_frame['start_y1'] = self.start_position[1]
        new_frame['start_x2'] = self.start_position[2]
        new_frame['start_y2'] = self.start_position[3]
        new_frame['end_x1'] = self.end_position[0]
        new_frame['end_y1'] = self.end_position[1]
        new_frame['end_x2'] = self.end_position[2]
        new_frame['end_y2'] = self.end_position[3]
        return new_frame


if __name__ == '__main__':
    data_path = 'results/F_result_GP080030.MP4_total_21600.csv'
    output_path = 'results/postprocess.csv'
    work_frame = pd.read_csv(data_path)
    trackers_id = work_frame.object_id.unique()
    duration_threshold = 30
    length_of_video = 21600
    object_filter = Filter_objects()
    total_frame = pd.DataFrame()
    for i in trackers_id:
        # get frame of object i.
        tmp_frame = work_frame[work_frame['object_id'] == i]

        start_frame = tmp_frame[tmp_frame.frame_number == tmp_frame.frame_number.min()]
        end_frame = tmp_frame[tmp_frame.frame_number == tmp_frame.frame_number.max()]

        start_position = [start_frame.x1.unique()[0], start_frame.y1.unique()[0], start_frame.x2.unique()[0],
                          start_frame.y2.unique()[0]]

        end_position = [end_frame.x1.unique()[0], end_frame.y1.unique()[0], end_frame.x2.unique()[0],
                        end_frame.y2.unique()[0]]

        new_tracker = Tracker(i, tmp_frame.object_name.unique()[0], tmp_frame.frame_number.min(),
                              tmp_frame.frame_number.max(), start_position, end_position)
        tmp_frame['unique_id'] = object_filter.update(new_tracker, duration_threshold)
        total_frame = pd.concat([tmp_frame, total_frame])
    total_frame.to_csv('results/results.csv', index=False)
