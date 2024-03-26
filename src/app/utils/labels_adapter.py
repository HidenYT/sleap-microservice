import os
import pandas as pd
import numpy as np
from sleap.io.format.adaptor import Adaptor, SleapObjectType
from sleap.io.format.filehandle import FileHandle
from sleap import Labels, Video, Skeleton
from typing import List, Optional
from sleap.instance import Instance, LabeledFrame, Point
from sleap.util import find_files_by_suffix

class ACDCsvAdaptor(Adaptor):
    """
    Reads Animal Keypoint Detection csv file with labeled frames for single video.
    """

    @property
    def handles(self):
        return SleapObjectType.labels

    @property
    def default_ext(self):
        return "csv"

    @property
    def all_exts(self):
        return ["csv"]

    @property
    def name(self):
        return "Animal Keypoint Detection Dataset CSV"

    def can_read_file(self, file: FileHandle):
        if not self.does_match_ext(file.filename):
            return False
        return True

    def can_write_filename(self, filename: str):
        return False

    def does_read(self) -> bool:
        return True

    def does_write(self) -> bool:
        return False

    @classmethod
    def read(
        cls,
        file: FileHandle,
        full_video: Optional[Video] = None,
        *args,
        **kwargs,
    ) -> Labels:
        return Labels(
            labeled_frames=cls.read_frames(
                file=file, 
                full_video=full_video, 
                *args, 
                **kwargs
            )
        )

    @classmethod
    def make_video_for_image_list(cls, image_dir, filenames) -> Video:
        """Creates a Video object from frame images."""

        # the image filenames in the csv may not match where the user has them
        # so we'll change the directory to match where the user has the csv
        def fix_img_path(img_dir, img_filename):
            img_filename = img_filename.replace("\\", "/")
            img_filename = os.path.basename(img_filename)
            img_filename = os.path.join(img_dir, img_filename)
            return img_filename

        filenames = list(map(lambda f: fix_img_path(image_dir, f), filenames))

        return Video.from_image_filenames(filenames)

    @classmethod
    def read_frames(
        cls,
        file: FileHandle,
        skeleton: Optional[Skeleton] = None,
        full_video: Optional[Video] = None,
        *args,
        **kwargs,
    ) -> List[LabeledFrame]:
        filename = file.filename

        # Read CSV file.
        data = pd.read_csv(filename, header=[0, 1])

        # Create the skeleton from the list of nodes in the csv file.
        # Note that DeepLabCut doesn't have edges, so these will need to be
        # added by user later.
        start_col = 1
        node_names = [n[0] for n in list(data)[start_col::2]]
        print(node_names)

        if skeleton is None:
            skeleton = Skeleton()
            skeleton.add_nodes(node_names)

        img_files = data.iloc[:, 0]

        if full_video:
            video = full_video
        else:
            img_dir = os.path.dirname(filename)
            video = cls.make_video_for_image_list(img_dir, img_files)

        lfs = []
        for i in range(len(data)):

            frame_idx = i

            instances = []
            
            # Get points for each node.
            any_not_missing = False
            instance_points = dict()
            for node in node_names:
                x, y = data[(node, "X")][i], data[(node, "Y")][i]
                instance_points[node] = Point(x, y)
                if ~(np.isnan(x) and np.isnan(y)):
                    any_not_missing = True
            if any_not_missing:
                instances.append(
                    Instance(skeleton=skeleton, points=instance_points)
                )
            if len(instances) > 0:
                lfs.append(
                    LabeledFrame(video=video, frame_idx=frame_idx, instances=instances)
                )

        return lfs