import numpy as np

class TrackedObject:
    def __init__(self, obj_id, obj_class, x1, y1, x2, y2):
        self.object_id = obj_id
        self.object_class = obj_class
        self.center = self.calculate_center(x1, y1, x2, y2)
        self.bbox = [x1, y1, x2, y2]
        # self.numberplate = None
        self.matched = False
        self.inactive_frames = 0  # Initialize inactive frames counter
        self.numberplate_bbox = None
        self.inactive_frames_numberplate = 0
    
    def calculate_center(self, x1, y1, x2, y2):
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        return (cx, cy)
    
    def update(self, x1, y1, x2, y2):
        self.center = self.calculate_center(x1, y1, x2, y2)
        self.bbox = [x1, y1, x2, y2]
        # Optionally update other attributes like velocity
    
    # def assign_numberplate(self, numberplate):
    #     self.numberplate = numberplate
    
    def update_numberplate_bbox(self, x1, y1, x2, y2):
        self.numberplate_bbox = [x1, y1, x2, y2]

class ObjectTracker:
    def __init__(self, max_distance_threshold=50, max_inactive_frames=5):
        self.max_distance_threshold = max_distance_threshold
        self.max_inactive_frames = max_inactive_frames
        self.tracks = []
        self.next_object_id = 1
    
    # Other methods remain unchanged

    def update_tracks(self, detections):
        # Update existing tracks
        for track in self.tracks:
            track.matched = False
        
        # Match detections to tracks
        for detection in detections:
            x1, y1, x2, y2 = detection['bbox']
            min_distance = float('inf')
            closest_track = None
            
            for track in self.tracks:
                distance = np.linalg.norm(np.array(track.center) - np.array(self.calculate_center(x1, y1, x2, y2)))
                if distance < min_distance:
                    min_distance = distance
                    closest_track = track
            
            if min_distance < self.max_distance_threshold:
                closest_track.update(x1, y1, x2, y2)
                closest_track.matched = True
                closest_track.inactive_frames = 0  # Reset inactive frames counter
            else:
                new_track = TrackedObject(self.next_object_id, "vehicle", x1, y1, x2, y2)
                self.next_object_id += 1
                self.tracks.append(new_track)
        
        # Increment inactive frames for unmatched tracks and delete if exceeds threshold
        for track in self.tracks:
            if not track.matched:
                track.inactive_frames += 1
                if track.inactive_frames > self.max_inactive_frames:
                    self.tracks.remove(track)

    import numpy as np

    def assign_numberplates(self, numberplate_detections):
        for numberplate_detection in numberplate_detections:
            x1, y1, x2, y2 = numberplate_detection['bbox']
            min_distance = float("inf")
            closest_track = None
            
            # Find the closest track that meets the criteria
            for track in self.tracks:
                if track.object_class == 'vehicle' and not track.numberplate_bbox:
                    distance = np.linalg.norm(np.array(track.center) - np.array(self.calculate_center(x1, y1, x2, y2)))
                    if distance < min_distance:
                        min_distance = distance
                        closest_track = track
            
            if closest_track is not None:
                closest_track.update_numberplate_bbox(x1, y1, x2, y2)
                closest_track.inactive_frames_numberplate = 0  # Reset inactive frames counter
                
                if closest_track.numberplate_bbox is None:
                    closest_track.assign_numberplate(x1, y1, x2, y2)
                else:
                    closest_track.inactive_frames_numberplate += 1
        
        # Clean up tracks where inactive_frames_numberplate >= 5
        for track in self.tracks:
            if track.numberplate_bbox is not None and hasattr(track, 'inactive_frames_numberplate'):
                if track.inactive_frames_numberplate >= 5:
                    track.numberplate_bbox = None


                    
    def get_active_tracks(self):
        return [track for track in self.tracks if track.matched]

    def calculate_center(self, x1, y1, x2, y2):
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        return (cx, cy)
