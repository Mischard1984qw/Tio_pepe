"""Vision processing agent for the Tío Pepe system."""

from typing import Dict, Any
import logging
import cv2
import numpy as np

class VisionAgent:
    """Specialized agent for computer vision tasks."""

    def __init__(self, config: Dict[str, Any] = None):
        self.logger = logging.getLogger(__name__)
        self.config = config or {}

    def process_task(self, task: Any) -> Dict[str, Any]:
        """Process a vision task based on its type."""
        task_type = task.data.get('vision_type')
        image_path = task.data.get('image_path')

        if not image_path:
            raise ValueError("No image path provided for processing")

        try:
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image from {image_path}")

            if task_type == 'object_detection':
                return self._detect_objects(image)
            elif task_type == 'face_detection':
                return self._detect_faces(image)
            elif task_type == 'image_classification':
                return self._classify_image(image)
            else:
                raise ValueError(f"Unsupported vision task type: {task_type}")

        except Exception as e:
            self.logger.error(f"Vision processing error: {str(e)}")
            raise

    def _detect_objects(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect objects in the given image."""
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Apply thresholding to get binary image
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            objects = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if area > 100:  # Filter small noise
                    x, y, w, h = cv2.boundingRect(contour)
                    objects.append({
                        'x': int(x),
                        'y': int(y),
                        'width': int(w),
                        'height': int(h),
                        'area': int(area)
                    })
            
            return {'objects': objects}
        except Exception as e:
            self.logger.error(f"Object detection error: {str(e)}")
            raise

    def _detect_faces(self, image: np.ndarray) -> Dict[str, Any]:
        """Detect faces in the given image."""
        try:
            # Load pre-trained face detection classifier
            face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
            
            # Convert to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Detect faces
            faces = face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(30, 30)
            )
            
            face_list = []
            for (x, y, w, h) in faces:
                face_list.append({
                    'x': int(x),
                    'y': int(y),
                    'width': int(w),
                    'height': int(h)
                })
            
            return {'faces': face_list}
        except Exception as e:
            self.logger.error(f"Face detection error: {str(e)}")
            raise

    def _classify_image(self, image: np.ndarray) -> Dict[str, Any]:
        """Classify the content of the given image."""
        try:
            # Basic image classification using color histogram
            hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
            cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
            
            # Simple classification based on dominant colors
            dominant_colors = np.unravel_index(hist.argmax(), hist.shape)
            
            # Map HSV values to basic color names
            hue = dominant_colors[0]
            saturation = dominant_colors[1]
            
            color_map = {
                (0, 20): 'red',
                (20, 40): 'yellow',
                (40, 80): 'green',
                (80, 120): 'blue',
                (120, 160): 'purple'
            }
            
            dominant_color = 'unknown'
            for (hue_min, hue_max), color in color_map.items():
                if hue_min <= hue <= hue_max:
                    dominant_color = color
                    break
            
            return {
                'classification': {
                    'dominant_color': dominant_color,
                    'saturation': int(saturation)
                }
            }
        except Exception as e:
            self.logger.error(f"Image classification error: {str(e)}")
            raise

    def cleanup(self) -> None:
        """Cleanup resources used by the agent."""
        cv2.destroyAllWindows()
        self.logger.info("Vision agent cleaned up")